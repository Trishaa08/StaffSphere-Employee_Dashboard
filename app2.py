# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
from sklearn.linear_model import LinearRegression
from sklearn.exceptions import NotFittedError
from sklearn.model_selection import train_test_split

# ---------------------------- PAGE CONFIG ----------------------------
st.set_page_config(page_title="StaffSphere | Employee Dashboard", layout="wide", page_icon="💼")

# ---------------------------- CSS STYLING ----------------------------
st.markdown("""
<style>
:root {
    --bg: #0b0f13;
    --card: #10161a;
    --accent1: #9b59b6;
    --accent2: #00ffd5;
    --muted: #9aa3a8;
}
body { background-color: var(--bg); color: #e8eef1; font-family: 'Poppins', sans-serif; }
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 25% 25%, #0e1317, #090c10);
}
.neon-title {
    font-size: 44px;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #00ffd5, #9b59b6, #00ffd5);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 3.5s infinite linear;
    margin-bottom: 0;
}
@keyframes shimmer {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.slogan {
    text-align: center;
    color: var(--muted);
    font-size: 16px;
    margin-bottom: 25px;
}
.neon-logo {
    width:90px; height:90px; margin: 0 auto 10px; display:block;
    border-radius: 50%;
    box-shadow: 0 0 18px rgba(155,89,182,0.45), 0 0 34px rgba(0,255,213,0.25) inset;
    background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.1), transparent 20%),
                linear-gradient(135deg, rgba(155,89,182,0.25), rgba(0,255,213,0.15));
    animation: pulse 2.5s infinite;
}
@keyframes pulse {
    0% { transform: scale(1); box-shadow: 0 0 15px rgba(155,89,182,0.3); }
    50% { transform: scale(1.08); box-shadow: 0 0 25px rgba(0,255,213,0.25); }
    100% { transform: scale(1); box-shadow: 0 0 15px rgba(155,89,182,0.3); }
}
.bubbles {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: -1;
    overflow: hidden;
}
.bubble {
    position: absolute;
    bottom: -150px;
    background: rgba(155,89,182,0.12);
    border-radius: 50%;
    animation: rise 15s infinite ease-in;
}
@keyframes rise {
    0% { transform: translateY(0) scale(1); opacity: 1; }
    100% { transform: translateY(-100vh) scale(1.5); opacity: 0; }
}
.card {
    background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 12px;
    box-shadow: 0 0 8px rgba(0,255,213,0.03);
}

/* Loading dots animation */
.loading-dots {
    text-align:center;
    margin-top: 25px;
    font-size: 18px;
    color: #00ffd5;
    letter-spacing: 2px;
    text-shadow: 0 0 10px #00ffd5, 0 0 20px #9b59b6;
}
.loading-dots span {
    animation: blink 1.5s infinite;
}
.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink {
    0% { opacity: 0.2; }
    20% { opacity: 1; }
    100% { opacity: 0.2; }
}

/* Badge styling */
.badge {
    display:inline-block;
    padding:6px 14px;
    border-radius:20px;
    background:linear-gradient(90deg,#00ffd5,#9b59b6);
    color:#0b0f13;
    font-weight:600;
    text-shadow:none;
    margin-left:8px;
}

/* Icon badges for smart highlights */
.icon-badge {
    display:inline-flex;
    align-items:center;
    justify-content:center;
    width:42px; height:42px;
    border-radius:50%;
    margin-right:10px;
    font-size:20px;
    color:#fff;
    text-shadow:0 0 6px rgba(0,0,0,0.3);
}
.top-icon { 
    background:linear-gradient(135deg,#00ffd5,#9b59b6); 
    box-shadow:0 0 12px rgba(0,255,213,0.35);
}
.low-icon { 
    background:linear-gradient(135deg,#ff4757,#9b59b6); 
    box-shadow:0 0 16px rgba(255,71,87,0.4);
}
.sum-icon { 
    background:linear-gradient(135deg,#1abc9c,#9b59b6); 
    box-shadow:0 0 12px rgba(26,188,156,0.35);
}
.title-flex { display:flex; align-items:center; justify-content:center; }

/* 🔴 Pulsing animation for alert card */
@keyframes pulse-red {
    0% { box-shadow:0 0 8px rgba(255,71,87,0.2), 0 0 20px rgba(255,71,87,0.06); transform:scale(1); }
    50% { box-shadow:0 0 20px rgba(255,71,87,0.45), 0 0 36px rgba(255,71,87,0.12); transform:scale(1.02); }
    100% { box-shadow:0 0 8px rgba(255,71,87,0.2), 0 0 20px rgba(255,71,87,0.06); transform:scale(1); }
}
.alert-card {
    animation: pulse-red 2.2s infinite ease-in-out;
}
</style>

<div class='bubbles'>
    <div class='bubble' style='left:10%;width:40px;height:40px;animation-delay:1s;'></div>
    <div class='bubble' style='left:30%;width:20px;height:20px;animation-delay:3s;'></div>
    <div class='bubble' style='left:50%;width:60px;height:60px;animation-delay:5s;'></div>
    <div class='bubble' style='left:70%;width:25px;height:25px;animation-delay:2s;'></div>
    <div class='bubble' style='left:90%;width:35px;height:35px;animation-delay:4s;'></div>
</div>
""", unsafe_allow_html=True)

# ---------------------------- HEADER ----------------------------
st.markdown("<div class='neon-logo'></div>", unsafe_allow_html=True)
st.markdown("<div class='neon-title'>💼 StaffSphere</div>", unsafe_allow_html=True)
st.markdown("<div class='slogan'>“Where employee performance meets clarity.”</div>", unsafe_allow_html=True)

# ---------------------------- UPLOAD SECTION ----------------------------
uploaded = st.file_uploader("📂 Upload Employee_Progress_Data CSV", type=["csv"])
if not uploaded:
    st.markdown("""
        <div style='text-align:center; margin-top:60px;'>
            <div style='display:inline-block; background:linear-gradient(90deg,#00ffd522,#9b59b622);
                        border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:30px 60px;
                        box-shadow:0 0 20px rgba(155,89,182,0.15);'>
                <p style='color:#a7b3b8; font-size:15px;'>Upload your <b>Employee_Progress_Data.csv</b> to unlock analytics and visuals.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# ---------------------------- LOADING ANIMATION & LOAD DATA ----------------------------
with st.spinner("✨ Processing your data... Please wait!"):
    st.markdown("<div class='loading-dots'>Loading<span>.</span><span>.</span><span>.</span></div>", unsafe_allow_html=True)
    time.sleep(1.2)  # small delay for animation visibility

    df = pd.read_csv(uploaded)

    # Validate required columns
    required_cols = ["Tasks_Completed", "Tasks_Pending", "Efficiency_%", "Attendance_%", "Basic_Salary", "Name"]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Missing required column: {col}")
            st.stop()

    # Derived metrics
    df["Tasks_Assigned"] = df["Tasks_Completed"].fillna(0) + df["Tasks_Pending"].fillna(0)
    # avoid division by zero
    df["Progress_%"] = np.where(df["Tasks_Assigned"] > 0, df["Tasks_Completed"] / df["Tasks_Assigned"] * 100, 0)
    df["Progress_%"] = df["Progress_%"].fillna(0)
    # make sure numeric types
    num_cols = ["Tasks_Completed", "Tasks_Pending", "Tasks_Assigned", "Efficiency_%", "Attendance_%", "Basic_Salary", "Progress_%"]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

# ---------------------------- SMART HIGHLIGHTS ----------------------------
st.markdown("---")
st.markdown("<h3 style='text-align:center;margin-bottom:20px;'>🌟 Smart Highlights</h3>", unsafe_allow_html=True)

colH1, colH2, colH3 = st.columns(3)

# Top performer
with colH1:
    try:
        top = df.loc[df["Efficiency_%"].idxmax()]
        top_name = top["Name"]
        top_eff = top["Efficiency_%"]
        top_att = top["Attendance_%"]
    except Exception:
        top_name, top_eff, top_att = "N/A", 0.0, 0.0

    st.markdown(f"""
    <div class='card' style='text-align:center;'>
        <div class='title-flex'>
            <div class='icon-badge top-icon'>🏆</div>
            <h4 style='margin:0;'>Top Performer <span class='badge'>⭐</span></h4>
        </div>
        <p style='font-size:18px; margin:5px 0;'><b>{top_name}</b></p>
        <div style='height:6px; width:80%; background:#222; border-radius:4px; margin:8px auto; overflow:hidden;'>
            <div style='width:{top_eff}%; height:100%; background:linear-gradient(90deg,#00ffd5,#9b59b6);'></div>
        </div>
        <p style='color:#00ffd5;'>Efficiency: {top_eff:.1f}%</p>
        <p style='color:#9b59b6;'>Attendance: {top_att:.1f}%</p>
    </div>
    """, unsafe_allow_html=True)

# Lowest attendance (alert card with pulse)
with colH2:
    try:
        low = df.loc[df["Attendance_%"].idxmin()]
        low_name = low["Name"]
        low_att = low["Attendance_%"]
        low_eff = low["Efficiency_%"]
    except Exception:
        low_name, low_att, low_eff = "N/A", 0.0, 0.0

    st.markdown(f"""
    <div class='card alert-card' style='text-align:center;'>
        <div class='title-flex'>
            <div class='icon-badge low-icon'>⛔</div>
            <h4 style='margin:0;'>Lowest Attendance</h4>
        </div>
        <p style='font-size:18px; margin:5px 0;'><b>{low_name}</b></p>
        <p style='color:#9b59b6;'>Attendance: {low_att:.1f}%</p>
        <p style='color:#00ffd5;'>Efficiency: {low_eff:.1f}%</p>
    </div>
    """, unsafe_allow_html=True)

# Overall summary
with colH3:
    avg_eff = df["Efficiency_%"].mean()
    avg_att = df["Attendance_%"].mean()
    completion_rate = (df["Tasks_Completed"].sum() / df["Tasks_Assigned"].sum() * 100) if df["Tasks_Assigned"].sum() > 0 else 0
    st.markdown(f"""
    <div class='card' style='text-align:center;'>
        <div class='title-flex'>
            <div class='icon-badge sum-icon'>📊</div>
            <h4 style='margin:0;'>Overall Summary</h4>
        </div>
        <p>Avg Efficiency: <b style='color:#00ffd5'>{avg_eff:.1f}%</b></p>
        <p>Avg Attendance: <b style='color:#9b59b6'>{avg_att:.1f}%</b></p>
        <p>Completion Rate: <b style='color:#00ffd5'>{completion_rate:.1f}%</b></p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------- DASHBOARD CONTENT ----------------------------
st.markdown("---")
st.markdown("<h3 style='text-align:center;margin-bottom:20px;'>📈 Employee Analytics Dashboard</h3>", unsafe_allow_html=True)

# KPIs
st.markdown("<div class='card'>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Employees", f"{len(df)}")
with c2:
    st.metric("Avg Efficiency", f"{df['Efficiency_%'].mean():.1f}%")
with c3:
    st.metric("Avg Attendance", f"{df['Attendance_%'].mean():.1f}%")
with c4:
    completion_rate = (df['Tasks_Completed'].sum() / df['Tasks_Assigned'].sum() * 100) if df['Tasks_Assigned'].sum() > 0 else 0
    st.metric("Completion Rate", f"{completion_rate:.1f}%")
st.markdown("</div>", unsafe_allow_html=True)

# Top employees chart + department pie
top10 = df.sort_values(by="Efficiency_%", ascending=False).head(10)
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.markdown("**Top 10 Employees by Efficiency**")
    fig1 = px.bar(top10, x="Name", y="Efficiency_%", color="Efficiency_%", color_continuous_scale="Blugrn")
    fig1.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("**Average Attendance by Department**")
    if "Department" in df.columns:
        avg_att = df.groupby("Department")["Attendance_%"].mean().sort_values(ascending=False)
        fig2 = px.pie(names=avg_att.index, values=avg_att.values, hole=0.55,
                      color_discrete_sequence=px.colors.sequential.Plasma)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Department data not available.")

st.markdown("---")
col3, col4 = st.columns(2, gap="large")
with col3:
    st.markdown("**Salary vs Efficiency**")
    fig3 = px.scatter(df, x="Basic_Salary", y="Efficiency_%", color="Efficiency_%",
                      color_continuous_scale="Plasma", hover_data=["Name"])
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("**Efficiency Trend (Top 10)**")
    if not top10.empty:
        fig4 = px.line(top10, x="Name", y="Efficiency_%", markers=True)
        fig4.update_traces(line_color="#9b59b6", marker=dict(color="#00ffd5"))
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No data to display.")

# ---------------------------- FORECASTING SETUP ----------------------------
st.markdown("---")
st.markdown("<h3 style='text-align:center;margin-bottom:12px;'>🔮 Forecasting & Predictive Insights</h3>", unsafe_allow_html=True)

# Prepare model training data (features -> Efficiency_%)
FEATURE_COLS = ["Tasks_Assigned", "Attendance_%", "Basic_Salary", "Progress_%"]
# If not enough rows to train a model, we will fallback
model = LinearRegression()
can_train = len(df) >= 10  # require minimum samples to get a somewhat reasonable model

if can_train:
    X = df[FEATURE_COLS].values
    y = df["Efficiency_%"].values
    try:
        model.fit(X, y)
        model_trained = True
    except Exception:
        model_trained = False
else:
    model_trained = False

# Helper: predict next-month efficiency for a single employee given adjustments
def predict_efficiency_for_employee(row, attendance_adj_pct=0.0, tasks_completed_adj_pct=0.0):
    """
    row: series of employee
    attendance_adj_pct: percentage change to attendance (e.g., +5 means +5%)
    tasks_completed_adj_pct: percentage change to tasks completed
    returns predicted_eff (float)
    """
    # Create modified copy
    attendance = max(0.0, row["Attendance_%"] * (1 + attendance_adj_pct / 100.0))
    tasks_completed = max(0.0, row["Tasks_Completed"] * (1 + tasks_completed_adj_pct / 100.0))
    tasks_pending = row.get("Tasks_Pending", 0.0)
    tasks_assigned = tasks_completed + tasks_pending
    progress = (tasks_completed / tasks_assigned * 100.0) if tasks_assigned > 0 else 0.0
    basic_salary = row["Basic_Salary"]
    feat = np.array([[tasks_assigned, attendance, basic_salary, progress]])
    if model_trained:
        try:
            pred = model.predict(feat)[0]
            # clamp predictions 0-100
            pred = float(np.clip(pred, 0, 100))
            return pred
        except Exception:
            return row["Efficiency_%"]
    else:
        # fallback heuristic: adjust current efficiency proportionally to attendance and progress
        # baseline: current efficiency scaled by attendance change and progress
        eff = row["Efficiency_%"] * (attendance / max(1e-6, row["Attendance_%"])) * (progress / max(1e-6, row["Progress_%"] if row["Progress_%"]>0 else 1))
        # if progress was zero, don't explode
        if not np.isfinite(eff) or eff <= 0:
            return row["Efficiency_%"]
        return float(np.clip(eff, 0, 100))

# ---------------------------- SIDEBAR: Employee selector + personal forecast ----------------------------
st.sidebar.title("📊 Track Employee Progress & Forecast")
employee = st.sidebar.selectbox("Select Employee", df["Name"].tolist())

st.sidebar.markdown("### Forecast scenario")
scenario = st.sidebar.selectbox("Scenario", ["Baseline (0%)", "Optimistic (+5% attendance)", "Pessimistic (-5% attendance)"])
# allow fine tuning
adj_slider = st.sidebar.slider("Additional attendance adjustment (%)", -20, 20, 0, step=1, help="Extra manual tweak to attendance for the forecast (±%)")
task_adj_slider = st.sidebar.slider("Tasks Completed adj (%)", -20, 20, 0, step=1, help="Adjust tasks completed to simulate productivity change")

# map preset scenario to attendance change
scenario_map = {"Baseline (0%)": 0.0, "Optimistic (+5% attendance)": 5.0, "Pessimistic (-5% attendance)": -5.0}
preset_att_adj = scenario_map.get(scenario, 0.0)
total_att_adj = preset_att_adj + adj_slider

if st.sidebar.button("Show Progress & Forecast"):
    emp_row = df[df["Name"] == employee].iloc[0]
    # show progress pie
    fig_progress = px.pie(
        names=["Completed", "Remaining"],
        values=[emp_row["Tasks_Completed"], max(0, emp_row["Tasks_Assigned"] - emp_row["Tasks_Completed"])],
        hole=0.6,
    )
    fig_progress.update_traces(textinfo='label+percent')
    st.sidebar.plotly_chart(fig_progress, use_container_width=True)
    st.sidebar.markdown(f"""
    <div style='background: linear-gradient(90deg,#00ffd544,#9b59b660);
                border-radius:8px; padding:10px; text-align:center; margin-bottom:8px; color:#e8eef1'>
        <b>Efficiency:</b> {emp_row['Efficiency_%']:.1f}%<br>
        <b>Attendance:</b> {emp_row['Attendance_%']:.1f}%<br>
        <b>Progress:</b> {emp_row['Progress_%']:.1f}%
    </div>""", unsafe_allow_html=True)

    # predict next-month with adjustments
    pred_next = predict_efficiency_for_employee(emp_row, attendance_adj_pct=total_att_adj, tasks_completed_adj_pct=task_adj_slider)

    # create 6-month projection: current -> predicted -> extrapolate by linear monthly growth derived from difference
    current_eff = emp_row["Efficiency_%"]
    months = ["Now", "M+1", "M+2", "M+3", "M+4", "M+5"]
    values = [current_eff, pred_next]
    # derive monthly growth from difference / 4, then apply a decaying growth factor for realism
    diff = pred_next - current_eff
    monthly_step = diff / 1.5  # faster convergence for demo
    for i in range(2, 6):
        next_val = values[-1] + monthly_step * (0.85 ** (i-2))  # decay
        values.append(float(np.clip(next_val, 0, 100)))

    personal_df = pd.DataFrame({"Month": months, "Efficiency": values})
    fig_personal = px.line(personal_df, x="Month", y="Efficiency", markers=True, title=f"{employee} — 6-month Projection")
    st.sidebar.plotly_chart(fig_personal, use_container_width=True)

    st.sidebar.markdown(f"**Predicted Next Month Efficiency:** {pred_next:.1f}%")
    st.sidebar.download_button(f"📄 Download Report ({employee})",
                               f"Employee Report for {employee}\nPredicted Next-Month Efficiency: {pred_next:.1f}%",
                               file_name=f"{employee}_forecast_report.txt")

# ---------------------------- OVERALL FORECAST SECTION ----------------------------
st.markdown("---")
st.markdown("### 🔁 Overall Next-Month Forecast (All Employees)", unsafe_allow_html=True)
st.markdown("Use the sliders to simulate optimistic/pessimistic scenarios across the organization.", unsafe_allow_html=True)

colA1, colA2 = st.columns([2,1], gap="large")
with colA2:
    org_att_adj = st.slider("Org-wide attendance adj (%)", -10, 10, 0, step=1)
    org_task_adj = st.slider("Org-wide tasks completed adj (%)", -10, 10, 0, step=1)
    apply_btn = st.button("Apply Organization Scenario")

# compute baseline predictions (no extra button required)
preds = []
for idx, row in df.iterrows():
    # baseline pred (no org-wide adjustment)
    baseline_pred = predict_efficiency_for_employee(row, attendance_adj_pct=0.0, tasks_completed_adj_pct=0.0)
    preds.append(baseline_pred)
df["Predicted_Eff_Next"] = preds

# apply org-wide if requested (recompute predicted column)
if 'apply_btn' in locals() and apply_btn:
    preds_adj = []
    for idx, row in df.iterrows():
        p = predict_efficiency_for_employee(row, attendance_adj_pct=org_att_adj, tasks_completed_adj_pct=org_task_adj)
        preds_adj.append(p)
    df["Predicted_Eff_Next"] = preds_adj

# show a table of Name | Current | Predicted
table_df = df[["Name", "Efficiency_%", "Predicted_Eff_Next"]].copy()
table_df = table_df.sort_values(by="Predicted_Eff_Next", ascending=False).reset_index(drop=True)
table_df.columns = ["Name", "Current_Eff_%", "Predicted_Eff_Next_%"]
with colA1:
    st.dataframe(table_df, use_container_width=True)

# Plot: current vs predicted (for all) and a 6-month projection stack (averaged)
avg_current = df["Efficiency_%"].mean()
avg_pred = df["Predicted_Eff_Next"].mean()

# Create 6-month projected average line for display using same extrapolation trick
avg_values = [avg_current, avg_pred]
diff = avg_pred - avg_current
monthly_step = diff / 1.5
for i in range(2,6):
    next_val = avg_values[-1] + monthly_step * (0.85 ** (i-2))
    avg_values.append(float(np.clip(next_val, 0, 100)))
months = ["Now","M+1","M+2","M+3","M+4","M+5"]
overall_proj_df = pd.DataFrame({"Month": months, "Avg_Efficiency": avg_values})

fig_overall = px.line(overall_proj_df, x="Month", y="Avg_Efficiency", markers=True, title="Overall Avg Efficiency — 6-Month Projection")
fig_overall.add_scatter(x=["Now","M+1"], y=[avg_current, avg_pred], mode="lines+markers", name="Now→Next", line=dict(dash="dash"))
st.plotly_chart(fig_overall, use_container_width=True)

# download predicted CSV
st.download_button("💾 Download Predictions (CSV)", df.to_csv(index=False).encode('utf-8'),
                   file_name="employees_with_predictions.csv")

# ---------------------------- DATA TABLE ----------------------------
st.markdown("---")
st.subheader("📋 Data Table (with Predicted Next-Month Efficiency)")
display_cols = ["Name", "Department"] if "Department" in df.columns else ["Name"]
display_cols += ["Basic_Salary", "Efficiency_%", "Predicted_Eff_Next", "Attendance_%", "Tasks_Assigned", "Tasks_Completed", "Progress_%"]
st.dataframe(df[display_cols].rename(columns={"Predicted_Eff_Next": "Predicted_Eff_Next_%"}), use_container_width=True)

# ---------------------------- SIDEBAR: Quick search box (convenience) ----------------------------
# (non-blocking) quick search to focus on an employee in main table
st.sidebar.markdown("---")
quick_search = st.sidebar.text_input("Quick search name (highlights main table)", "")
if quick_search:
    subset = df[df["Name"].str.contains(quick_search, case=False, na=False)]
    if not subset.empty:
        st.sidebar.success(f"Found {len(subset)} match(es). Use the main table to review.")
    else:
        st.sidebar.info("No matches.")

# ---------------------------- FOOTER ----------------------------
st.markdown("<div style='text-align:center; color:#7d8790; margin-top:20px;'>© 2025 StaffSphere • Where employee performance meets clarity.</div>", unsafe_allow_html=True)
