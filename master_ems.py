import csv
import os
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
import uuid

# ----------- Paths ------------
DATA_DIR = "."
REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

EMP_CSV = os.path.join(DATA_DIR, "employees.csv")
TASKS_CSV = os.path.join(DATA_DIR, "tasks.csv")
ATT_CSV = os.path.join(DATA_DIR, "attendance.csv")
LEAVE_CSV = os.path.join(DATA_DIR, "leave_requests.csv")
PAYROLL_CSV = os.path.join(DATA_DIR, "payrolls.csv")

# ---------- Utilities ----------
def _uid() -> str:
    return str(uuid.uuid4())

def _now_iso() -> str:
    return datetime.utcnow().isoformat()

def _today_iso() -> str:
    return date.today().isoformat()

# ---------- Models ----------
class Employee:
    def __init__(self, emp_id: str, name: str, role: str, department: str, email: str = "", basic_salary: float = 0.0):
        self.emp_id = emp_id
        self.name = name
        self.role = role
        self.department = department
        self.email = email
        self.active = True
        self.basic_salary = float(basic_salary or 0.0)
        self.points = 0
        self.badges: List[str] = []
        self.task_ids: List[str] = []
        self.attendance: List[Dict[str, Any]] = []  # {date, check_in, check_out, hours}
        self.progress_notes: List[Dict[str, Any]] = []
        self.leaves: List[str] = []  # leave ids

    def __repr__(self):
        return f"{self.emp_id} | {self.name} ({self.role}) Dept:{self.department} Salary:{self.basic_salary}"

class Task:
    def __init__(self, task_id: str, title: str, assignee_id: Optional[str], priority: str, status: str, due_date: Optional[str], comments: str = "", attachment: str = ""):
        self.task_id = task_id
        self.title = title
        self.assignee_id = assignee_id
        self.priority = priority
        self.status = status
        self.due_date = due_date
        self.comments = comments
        self.attachment = attachment
        self.progress_percent = 0
        self.updates: List[Dict[str, Any]] = []
        self.created_at = _now_iso()

    def __repr__(self):
        return f"{self.task_id} | {self.title} ({self.status}) [{self.progress_percent}%]"

class LeaveRequest:
    def __init__(self, leave_id: str, emp_id: str, start_date: str, end_date: str, reason: str, status: str = "Pending"):
        self.leave_id = leave_id
        self.emp_id = emp_id
        self.start_date = start_date
        self.end_date = end_date
        self.reason = reason
        self.status = status
        self.requested_at = _now_iso()
    def __repr__(self):
        return f"{self.leave_id} {self.emp_id} {self.start_date}->{self.end_date} [{self.status}]"

class PayrollRecord:
    def __init__(self, payroll_id: str, emp_id: str, year: int, month: int, gross: float, tax: float, deductions: float, net: float, payslip_path: str):
        self.payroll_id = payroll_id
        self.emp_id = emp_id
        self.year = year
        self.month = month
        self.gross = gross
        self.tax = tax
        self.deductions = deductions
        self.net = net
        self.payslip_path = payslip_path
        self.generated_at = _now_iso()

# ---------- CSV Helpers ----------
def load_csv_dict(path: str) -> List[Dict[str,str]]:
    result = []
    if not os.path.exists(path):
        return result
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            result.append(r)
    return result

def save_csv_dict(path: str, rows: List[Dict[str,Any]], fieldnames: List[str]):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

# ---------- Core System ----------
class MasterEMS:
    def __init__(self):
        self.employees: Dict[str, Employee] = {}
        self.tasks: Dict[str, Task] = {}
        self.leaves: Dict[str, LeaveRequest] = {}
        self.payrolls: Dict[str, PayrollRecord] = {}  # payroll_id -> PayrollRecord
        # demo auth
        self.default_users = {"admin@example.com":{"password":"admin","role":"Admin"}, "manager@example.com":{"password":"manager","role":"Manager"}}

        # load CSVs if present
        self._load_employees_csv()
        self._load_tasks_csv()
        self._load_attendance_csv()
        self._load_leaves_csv()
        self._load_payrolls_csv()

    # ---------- CSV load/save implementations ----------
    def _load_employees_csv(self):
        rows = load_csv_dict(EMP_CSV)
        for r in rows:
            emp_id = r.get("id") or _uid()
            basic_salary = float(r.get("basic_salary") or r.get("salary") or 0.0)
            e = Employee(emp_id, r.get("name",""), r.get("role","Employee"), r.get("department",""), r.get("email",""), basic_salary)
            self.employees[emp_id] = e

    def save_employees_csv(self):
        rows = []
        for e in self.employees.values():
            rows.append({"id": e.emp_id, "name": e.name, "role": e.role, "department": e.department, "email": e.email, "basic_salary": e.basic_salary})
        fieldnames = ["id","name","role","department","email","basic_salary"]
        save_csv_dict(EMP_CSV, rows, fieldnames)

    def _load_tasks_csv(self):
        rows = load_csv_dict(TASKS_CSV)
        for r in rows:
            t = Task(r.get("task_id") or _uid(), r.get("title",""), r.get("employee_id") or None, r.get("priority","Medium"), r.get("status","Pending"), r.get("due_date"), r.get("comments",""), r.get("attachment",""))
            # if employee exists, link task id
            self.tasks[t.task_id] = t
            if t.assignee_id and t.assignee_id in self.employees:
                self.employees[t.assignee_id].task_ids.append(t.task_id)

    def save_tasks_csv(self):
        rows = []
        for t in self.tasks.values():
            rows.append({"task_id": t.task_id, "employee_id": t.assignee_id or "", "title": t.title, "priority": t.priority, "status": t.status, "due_date": t.due_date or "", "comments": t.comments, "attachment": t.attachment})
        fieldnames = ["task_id","employee_id","title","priority","status","due_date","comments","attachment"]
        save_csv_dict(TASKS_CSV, rows, fieldnames)

    def _load_attendance_csv(self):
        rows = load_csv_dict(ATT_CSV)
        for r in rows:
            emp_id = r.get("employee_id")
            if not emp_id:
                continue
            rec = {"date": r.get("date"), "check_in": r.get("check_in"), "check_out": r.get("check_out"), "hours": float(r.get("work_hours") or r.get("hours") or 0.0)}
            if emp_id in self.employees:
                self.employees[emp_id].attendance.append(rec)

    def save_attendance_csv(self):
        rows = []
        for e in self.employees.values():
            for rec in e.attendance:
                rows.append({"employee_id": e.emp_id, "date": rec.get("date"), "status": rec.get("status","Present" if rec.get("hours") and rec.get("hours")>0 else "Present"), "work_hours": rec.get("hours") or 0})
        fieldnames = ["employee_id","date","status","work_hours"]
        save_csv_dict(ATT_CSV, rows, fieldnames)

    def _load_leaves_csv(self):
        rows = load_csv_dict(LEAVE_CSV)
        for r in rows:
            lid = r.get("leave_id") or _uid()
            lr = LeaveRequest(lid, r.get("employee_id",""), r.get("start_date",""), r.get("end_date",""), r.get("reason",""), r.get("status","Pending"))
            self.leaves[lid] = lr
            if lr.emp_id in self.employees:
                self.employees[lr.emp_id].leaves.append(lid)

    def save_leaves_csv(self):
        rows = []
        for l in self.leaves.values():
            rows.append({"leave_id": l.leave_id, "employee_id": l.emp_id, "start_date": l.start_date, "end_date": l.end_date, "reason": l.reason, "status": l.status})
        fieldnames = ["leave_id","employee_id","start_date","end_date","reason","status"]
        save_csv_dict(LEAVE_CSV, rows, fieldnames)

    def _load_payrolls_csv(self):
        rows = load_csv_dict(PAYROLL_CSV)
        for r in rows:
            pid = r.get("payroll_id") or _uid()
            try:
                p = PayrollRecord(pid, r.get("emp_id",""), int(r.get("year",0)), int(r.get("month",0)), float(r.get("gross",0)), float(r.get("tax",0)), float(r.get("other_deductions",0)), float(r.get("net",0)), r.get("payslip_path",""))
                self.payrolls[pid] = p
            except Exception:
                continue

    def save_payrolls_csv(self):
        rows = []
        for p in self.payrolls.values():
            rows.append({"payroll_id": p.payroll_id, "emp_id": p.emp_id, "year": p.year, "month": p.month, "gross": p.gross, "tax": p.tax, "other_deductions": p.deductions, "net": p.net, "payslip_path": p.payslip_path})
        fieldnames = ["payroll_id","emp_id","year","month","gross","tax","other_deductions","net","payslip_path"]
        save_csv_dict(PAYROLL_CSV, rows, fieldnames)

    # ---------- Employee operations ----------
    def add_employee(self, name: str, role: str, department: str, email: str = "", basic_salary: float = 0.0) -> str:
        eid = _uid()
        e = Employee(eid, name, role, department, email, basic_salary)
        self.employees[eid] = e
        return eid

    def update_employee(self, emp_id: str, **kwargs) -> bool:
        e = self.employees.get(emp_id)
        if not e: return False
        for k,v in kwargs.items():
            if hasattr(e,k):
                setattr(e,k,v)
        return True

    def list_employees(self) -> List[Employee]:
        return list(self.employees.values())

    # ---------- Task operations ----------
    def create_task(self, title: str, assignee_id: Optional[str], priority: str = "Medium", due_date: Optional[str] = None, comments: str = "", attachment: str = "") -> str:
        tid = _uid()
        t = Task(tid, title, assignee_id, priority, "Pending", due_date, comments, attachment)
        self.tasks[tid] = t
        if assignee_id and assignee_id in self.employees:
            self.employees[assignee_id].task_ids.append(tid)
        return tid

    def assign_task(self, task_id: str, emp_id: str) -> bool:
        t = self.tasks.get(task_id); e = self.employees.get(emp_id)
        if not t or not e: return False
        # remove from old
        if t.assignee_id and t.assignee_id in self.employees:
            old = self.employees[t.assignee_id]
            if task_id in old.task_ids:
                old.task_ids.remove(task_id)
        t.assignee_id = emp_id
        if task_id not in e.task_ids: e.task_ids.append(task_id)
        return True

    def update_task_progress(self, task_id: str, percent: int, note: str = "") -> bool:
        t = self.tasks.get(task_id)
        if not t: return False
        percent = max(0,min(100,int(percent)))
        t.progress_percent = percent
        if note:
            t.updates.append({"ts":_now_iso(),"note":note})
        if percent >= 100:
            t.status = "Completed"
        elif percent > 0:
            t.status = "In Progress"
        return True

    # ---------- Attendance ----------
    def check_in(self, emp_id: str, ts: Optional[str] = None) -> bool:
        e = self.employees.get(emp_id)
        if not e: return False
        today = _today_iso()
        ts = ts or datetime.utcnow().time().strftime("%H:%M:%S")
        # find record for today
        for rec in e.attendance:
            if rec["date"] == today:
                rec["check_in"] = ts
                return True
        e.attendance.append({"date": today, "check_in": ts, "check_out": None, "hours": 0.0})
        return True

    def check_out(self, emp_id: str, ts: Optional[str] = None) -> bool:
        e = self.employees.get(emp_id)
        if not e: return False
        today = _today_iso()
        ts = ts or datetime.utcnow().time().strftime("%H:%M:%S")
        for rec in e.attendance:
            if rec["date"] == today:
                rec["check_out"] = ts
                ci = rec.get("check_in")
                if ci:
                    fmt = "%H:%M:%S"
                    try:
                        t1 = datetime.strptime(ci, fmt)
                        t2 = datetime.strptime(ts, fmt)
                        seconds = max(0, (t2 - t1).seconds)
                        rec["hours"] = round(seconds/3600.0,2)
                    except Exception:
                        rec["hours"] = 0.0
                return True
        # no record
        e.attendance.append({"date": today, "check_in": None, "check_out": ts, "hours": 0.0})
        return True

    # ---------- Leaves ----------
    def request_leave(self, emp_id: str, start_date: str, end_date: str, reason: str) -> Optional[str]:
        if emp_id not in self.employees: return None
        lid = _uid()
        lr = LeaveRequest(lid, emp_id, start_date, end_date, reason, "Pending")
        self.leaves[lid] = lr
        self.employees[emp_id].leaves.append(lid)
        return lid

    def set_leave_status(self, leave_id: str, status: str) -> bool:
        if leave_id not in self.leaves: return False
        if status not in ("Pending","Approved","Rejected"): return False
        self.leaves[leave_id].status = status
        return True

    # ---------- Gamification ----------
    def award_points(self, emp_id: str, points: int) -> bool:
        e = self.employees.get(emp_id)
        if not e: return False
        e.points += int(points)
        return True

    def assign_badge(self, emp_id: str, badge: str) -> bool:
        e = self.employees.get(emp_id)
        if not e: return False
        if badge not in e.badges:
            e.badges.append(badge)
            e.points += 50
        return True

    def leaderboard(self, top_n: int = 10) -> List[Dict[str,Any]]:
        def completed(e: Employee):
            return sum(1 for tid in e.task_ids if self.tasks.get(tid) and self.tasks[tid].status == "Completed")
        ranked = sorted(self.employees.values(), key=lambda e:(e.points, completed(e)), reverse=True)
        return [{"emp_id": r.emp_id, "name": r.name, "points": r.points, "completed": completed(r)} for r in ranked[:top_n]]

    # ---------- Analytics ----------
    def compute_employee_kpi(self, emp_id: str) -> Optional[Dict[str,Any]]:
        e = self.employees.get(emp_id)
        if not e: return None
        assigned = len(e.task_ids)
        completed = sum(1 for tid in e.task_ids if self.tasks.get(tid) and self.tasks[tid].status == "Completed")
        avg_progress = 0.0
        if assigned>0:
            avg_progress = sum(self.tasks[tid].progress_percent for tid in e.task_ids if self.tasks.get(tid))/assigned
        hours = sum(rec.get("hours") or 0 for rec in e.attendance)
        return {"employee_id": emp_id, "assigned": assigned, "completed": completed, "avg_progress": round(avg_progress,2), "hours": round(hours,2)}

    def company_completion_rate(self) -> float:
        total = len(self.tasks); done = sum(1 for t in self.tasks.values() if t.status == "Completed")
        return round((done/total*100),2) if total>0 else 0.0

    # ---------- Behavior analytics ----------
    def behavior_score(self, emp_id: str) -> float:
        e = self.employees.get(emp_id)
        if not e: return 0.0
        total_days = len(e.attendance)
        present_days = sum(1 for r in e.attendance if (r.get("hours") or 0)>0)
        attendance_score = (present_days/total_days*100) if total_days>0 else 50.0
        late_tasks = 0
        for tid in e.task_ids:
            t = self.tasks.get(tid)
            if not t: continue
            if t.status!="Completed" and t.due_date:
                try:
                    due = datetime.strptime(t.due_date,"%Y-%m-%d").date()
                    if due < date.today(): late_tasks +=1
                except Exception:
                    pass
        late_score = max(0, 100 - late_tasks*10)
        final = attendance_score*0.6 + late_score*0.4
        return round(final,2)

    def department_performance(self) -> Dict[str,float]:
        dept_scores: Dict[str, List[float]] = {}
        for e in self.employees.values():
            k = self.compute_employee_kpi(e.emp_id)
            if not k: continue
            dept_scores.setdefault(e.department or "Unknown", []).append(k["avg_progress"])
        return {d: round(sum(v)/len(v),2) for d,v in dept_scores.items()}

    # ---------- Payroll module ----------
    # payroll algorithm design:
    # gross = basic + hra(20%) + allowances(10%) - simple example
    # tax: progressive slabs (example):
    #   up to 250000: 0
    #   250001-500000: 5%
    #   500001-1000000: 20%
    #   >1000000: 30%
    # monthly tax = annual_tax / 12
    def _compute_gross(self, basic: float) -> float:
        hra = basic * 0.20
        allowances = basic * 0.10
        gross = basic + hra + allowances
        return round(gross,2)

    def _compute_annual_tax(self, annual_income: float) -> float:
        # simple progressive calculation
        tax = 0.0
        remaining = annual_income
        # slab 1: up to 250k -> 0
        slab_limits = [(250000,0.0),(250000,0.05),(500000,0.20),(float('inf'),0.30)]
        # We'll subtract piecewise
        brackets = [250000,250000,500000]  # totals 1,000,000 < rest
        rates = [0.0,0.05,0.20,0.30]
        lower = 0
        income = annual_income
        if income <= 250000:
            return 0.0
        # handle ranges
        # Up to 250k: 0
        remaining = income
        # 0 - 250k
        remaining -= 250000
        # next 250k at 5% (250001-500k)
        if remaining>0:
            taxable = min(250000, remaining)
            tax += taxable * 0.05
            remaining -= taxable
        # next 500k at 20% (500001-1,000,000)
        if remaining>0:
            taxable = min(500000, remaining)
            tax += taxable * 0.20
            remaining -= taxable
        # rest at 30%
        if remaining>0:
            tax += remaining * 0.30
        return round(tax,2)

    def compute_payslip(self, emp_id: str, year: int, month: int, other_deductions: float = 0.0) -> Optional[PayrollRecord]:
        e = self.employees.get(emp_id)
        if not e:
            return None
        basic = e.basic_salary
        gross_monthly = self._compute_gross(basic)
        annual_income = gross_monthly * 12
        annual_tax = self._compute_annual_tax(annual_income)
        monthly_tax = round(annual_tax / 12.0,2)
        net = round(gross_monthly - monthly_tax - float(other_deductions),2)
        # create payslip file (text)
        payslip_name = f"payslip_{emp_id}_{year}_{month}.txt"
        payslip_path = os.path.join(REPORT_DIR, payslip_name)
        with open(payslip_path, "w", encoding='utf-8') as f:
            f.write("PAYSLIP\n")
            f.write("=======\n")
            f.write(f"Employee: {e.name} ({e.emp_id})\n")
            f.write(f"Role: {e.role} | Dept: {e.department}\n")
            f.write(f"Period: {year}-{str(month).zfill(2)}\n\n")
            f.write(f"Basic Salary: {basic:.2f}\n")
            f.write(f"HRA (20%): {basic*0.20:.2f}\n")
            f.write(f"Allowances (10%): {basic*0.10:.2f}\n")
            f.write(f"Gross (monthly): {gross_monthly:.2f}\n\n")
            f.write(f"Annual Tax (est): {annual_tax:.2f}\n")
            f.write(f"Monthly Tax (est): {monthly_tax:.2f}\n")
            f.write(f"Other Deductions: {other_deductions:.2f}\n\n")
            f.write(f"Net Pay (monthly): {net:.2f}\n")
            f.write("\nGenerated at: " + _now_iso())
        payroll_id = _uid()
        pr = PayrollRecord(payroll_id, emp_id, year, month, gross_monthly, monthly_tax, float(other_deductions), net, payslip_path)
        self.payrolls[payroll_id] = pr
        return pr

    def generate_monthly_payroll(self, year: int, month: int, other_deductions_map: Optional[Dict[str,float]] = None) -> List[PayrollRecord]:
        other_deductions_map = other_deductions_map or {}
        records = []
        for e in self.employees.values():
            od = other_deductions_map.get(e.emp_id, 0.0)
            pr = self.compute_payslip(e.emp_id, year, month, other_deductions=od)
            if pr:
                records.append(pr)
        # save payrolls CSV immediately
        self.save_payrolls_csv()
        return records

    def export_payroll_csv(self, year: int, month: int, out_path: Optional[str] = None) -> str:
        out = out_path or os.path.join(REPORT_DIR, f"payroll_{year}_{str(month).zfill(2)}.csv")
        rows = []
        for p in self.payrolls.values():
            if p.year==year and p.month==month:
                rows.append({"payroll_id": p.payroll_id, "emp_id": p.emp_id, "year": p.year, "month": p.month, "gross": p.gross, "tax": p.tax, "other_deductions": p.deductions, "net": p.net, "payslip_path": p.payslip_path})
        fieldnames = ["payroll_id","emp_id","year","month","gross","tax","other_deductions","net","payslip_path"]
        save_csv_dict(out, rows, fieldnames)
        return out

    # ---------- Reporting ----------
    def generate_employee_report_txt(self, emp_id: str) -> Optional[str]:
        e = self.employees.get(emp_id)
        if not e: return None
        lines = []
        lines.append("EMPLOYEE REPORT")
        lines.append("================")
        lines.append(f"Name: {e.name}")
        lines.append(f"Email: {e.email}")
        lines.append(f"Role: {e.role}")
        lines.append(f"Department: {e.department}")
        lines.append(f"Basic Salary: {e.basic_salary:.2f}")
        lines.append(f"Points: {e.points}")
        lines.append(f"Badges: {', '.join(e.badges) if e.badges else 'None'}")
        lines.append("")
        lines.append("Tasks:")
        for tid in e.task_ids:
            t = self.tasks.get(tid)
            if not t: continue
            lines.append(f"- {t.title} | Status: {t.status} | Progress: {t.progress_percent}% | Due: {t.due_date}")
        lines.append("")
        lines.append("Recent Progress Notes:")
        for note in e.progress_notes[-10:]:
            lines.append(f"[{note.get('ts')}] {note.get('note')}")
        lines.append("")
        lines.append("Attendance (last 10):")
        for rec in e.attendance[-10:]:
            lines.append(f"- {rec.get('date')}: in={rec.get('check_in')} out={rec.get('check_out')} hours={rec.get('hours')}")
        content = "\n".join(lines)
        fn = os.path.join(REPORT_DIR, f"employee_report_{emp_id}.txt")
        with open(fn, "w", encoding='utf-8') as f:
            f.write(content)
        return fn

    def generate_company_report_txt(self) -> str:
        lines = []
        lines.append("COMPANY REPORT")
        lines.append("================")
        lines.append(f"Generated at: {_now_iso()}")
        lines.append("")
        lines.append("Employees:")
        for e in self.list_employees():
            lines.append(f"- {e.name} ({e.role}) Dept: {e.department} Salary: {e.basic_salary}")
        lines.append("")
        lines.append("Leaderboard:")
        for i,r in enumerate(self.leaderboard(), start=1):
            lines.append(f"{i}. {r['name']} - Points: {r['points']} Completed: {r['completed']}")
        lines.append("")
        lines.append(f"Task Completion Rate: {self.company_completion_rate()}%")
        content = "\n".join(lines)
        fn = os.path.join(REPORT_DIR, "company_report.txt")
        with open(fn, "w", encoding='utf-8') as f:
            f.write(content)
        return fn

# ---------- Demo / Example usage ----------
if __name__ == "__main__":
    print("Master EMS with Payroll demo starting...\n")
    ems = MasterEMS()

    # If no employees loaded, seed demo
    if not ems.employees:
        print("Seeding demo employees...")
        a = ems.add_employee("Alice Smith","Manager","Engineering","alice@org.com", basic_salary=60000)  # basic monthly
        b = ems.add_employee("Bob Kumar","Employee","Engineering","bob@org.com", basic_salary=30000)
        c = ems.add_employee("Charlie Ray","Employee","Design","charlie@org.com", basic_salary=35000)
        # tasks
        t1 = ems.create_task("Prepare onboarding docs", a, "High", (date.today()+timedelta(days=3)).isoformat())
        t2 = ems.create_task("Design hero", c, "Medium", (date.today()+timedelta(days=7)).isoformat())
        ems.update_task_progress(t2, 20, "Initial wireframes")
        # attendance
        ems.check_in(b); ems.check_out(b,"17:30:00")
        ems.award_points(a,150); ems.award_points(c,80)
        # leave
        lid = ems.request_leave(b, (date.today()+timedelta(days=5)).isoformat(), (date.today()+timedelta(days=6)).isoformat(), "Personal")
        ems.set_leave_status(lid,"Approved")
        # save initial CSVs (optional)
        ems.save_employees_csv()
        ems.save_tasks_csv()
        ems.save_attendance_csv()
        ems.save_leaves_csv()

    # List employees
    print("Employees loaded:")
    for e in ems.list_employees():
        print(" ", e)

    # Generate payroll for current month
    year = date.today().year
    month = date.today().month
    print(f"\nGenerating payroll for {year}-{month} ...")
    payrolls = ems.generate_monthly_payroll(year, month)
    for p in payrolls:
        print(f" Payslip: {p.emp_id} gross={p.gross} tax={p.tax} net={p.net} -> {p.payslip_path}")

    # Export payroll CSV
    payroll_csv_path = ems.export_payroll_csv(year, month)
    print("Payroll CSV exported to:", payroll_csv_path)

    # Generate individual employee report and company report
    for e in ems.list_employees():
        r = ems.generate_employee_report_txt(e.emp_id)
        print("Employee report:", r)
    comp = ems.generate_company_report_txt()
    print("Company report:", comp)

    # Save payroll records and CSVs
    ems.save_payrolls_csv()
    print("\nDemo finished. Check the reports/ folder for payslips and reports.")