import streamlit as st
from datetime import datetime, timedelta

# --- 1. Helper Functions ---
def calculate_end_time(start_time_str, duration):
    start_dt = datetime.strptime(start_time_str, "%I %p")
    end_dt = start_dt + timedelta(hours=duration)
    return end_dt.strftime("%I %p")

def get_dt(day_idx, time_str, is_end_time=False, start_time_str=None):
    base_date = datetime(2026, 3, 22) 
    target_date = base_date + timedelta(days=day_idx-1)
    if is_end_time and start_time_str:
        s_hour = datetime.strptime(start_time_str, "%I %p").hour
        e_hour = datetime.strptime(time_str, "%I %p").hour
        if e_hour < s_hour: target_date += timedelta(days=1)
    time_obj = datetime.strptime(time_str, "%I %p").time()
    return datetime.combine(target_date, time_obj)

# --- 2. NATIVE UI STYLING ---
st.set_page_config(layout="wide", page_title="Swap Validator Pro")

# Using CSS Variables ensures it follows the user's system theme automatically
st.markdown("""
    <style>
    /* Card design using native theme variables */
    .native-card {
        background-color: var(--secondary-bg-color);
        border: 1px solid var(--border-color);
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
    }

    /* Shift display box */
    .shift-box {
        background-color: var(--background-color);
        border: 1px solid var(--border-color);
        color: var(--text-color);
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    h1, h2, h3 {
        text-align: center;
    }

    /* Remove extra padding from streamlit columns */
    [data-testid="column"] {
        padding: 0 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    is_ramadan = st.checkbox("🌙 Ramadan Mode (7h)")
    st.info("The app will automatically match your browser's Light/Dark settings.")

duration = 7 if is_ramadan else 9

st.markdown("<h1>🔄 Smart Swap Validator</h1>", unsafe_allow_html=True)

day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hours = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

col1, col2 = st.columns(2)
shift_data = {}

for i, col in enumerate([col1, col2], 1):
    with col:
        st.markdown(f"### 👤 Employee {i}")
        e_name = st.text_input(f"Name", placeholder=f"Employee {i} Name", key=f"name_{i}", label_visibility="collapsed")
        
        for week in ["Current", "Next"]:
            # Start of the Native Card
            st.markdown(f'<div class="native-card">', unsafe_allow_html=True)
            st.markdown(f"<center><b>🗓️ {week} Week</b></center>", unsafe_allow_html=True)
            
            t1, t2, t3 = st.columns([4, 1, 4])
            with t1:
                s_time = st.selectbox(f"Start", hours, index=17 if i==1 and week=="Current" else 9, key=f"s{i}_{week}")
            with t2:
                st.markdown("<p style='text-align:center; padding-top:35px;'>to</p>", unsafe_allow_html=True)
            with t3:
                e_time = calculate_end_time(s_time, duration)
                st.markdown("<p style='font-size:0.8rem; margin-bottom:10px;'>End Time</p>", unsafe_allow_html=True)
                st.markdown(f"<div class='shift-box'>{e_time}</div>", unsafe_allow_html=True)
            
            o1, o2 = st.columns(2)
            off1 = o1.selectbox("Off Day 1", ["None"] + day_list, key=f"o1_{i}_{week}")
            off2 = o2.selectbox("Off Day 2", ["None"] + [d for d in day_list if d != off1], key=f"o2_{i}_{week}")

            with st.expander("➕ Overtime"):
                ot_b = st.number_input("Before (hrs)", 0, 2, 0, key=f"otb_{i}_{week}")
                ot_a = st.number_input("After (hrs)", 0, 2, 0, key=f"ota_{i}_{week}")
                st.checkbox("Full Day OT", key=f"f_ot_{i}_{week}")
            
            st.markdown('</div>', unsafe_allow_html=True) # End of the Card
            
            shift_data[f"e{i}_{week}"] = {
                "start": s_time, "end": e_time, 
                "off_count": (1 if off1 != "None" else 0) + (1 if off2 != "None" else 0),
                "off_days": [off1, off2]
            }

st.divider()

if st.button("🚀 Run Swap Check", use_container_width=True):
    # Validation Logic
    all_reasons = []
    for emp_idx in [1, 2]:
        name = st.session_state[f"name_{emp_idx}"] or f"Employee {emp_idx}"
        reasons = []
        
        # Define current vs next
        cur_key = f"e{emp_idx}_Current"
        next_key = f"e{3-emp_idx}_Next" # Checks against the other employee's next week
        
        d_end = get_dt(7, shift_data[cur_key]["end"], is_end_time=True, start_time_str=shift_data[cur_key]["start"])
        d_start = get_dt(8, shift_data[next_key]["start"])

        # OT Squeeze
        d_end += timedelta(hours=st.session_state[f"ota_{emp_idx}_Current"])
        d_start -= timedelta(hours=st.session_state[f"otb_{3-emp_idx}_Next"])

        rest = (d_start - d_end).total_seconds() / 3600
        if rest < 12 and not ("Saturday" in shift_data[cur_key]["off_days"] or "Sunday" in shift_data[next_key]["off_days"]):
            reasons.append(f"Rest is only {rest:.1f}h (Min 12h required).")
        
        if reasons:
            st.error(f"❌ **{name}:** " + " | ".join(reasons))
        else:
            st.success(f"✅ **{name}:** Schedule is valid.")

st.markdown("<br><center>Created by Abdelrahman heshmat @abheshma</center>", unsafe_allow_html=True)
