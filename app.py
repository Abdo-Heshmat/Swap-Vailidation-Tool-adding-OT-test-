import streamlit as st
from datetime import datetime, timedelta

# --- 1. THEME MANAGEMENT ---
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

# --- 2. HELPER FUNCTIONS ---
def calculate_end_time(start_time_str, dur):
    start_dt = datetime.strptime(start_time_str, "%I %p")
    end_dt = start_dt + timedelta(hours=dur)
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

# --- 3. PAGE CONFIG & THEME ICONS ---
st.set_page_config(layout="wide", page_title="Swap Validator Pro")

# Theme icon logic
icon = "☀️" if st.session_state.theme == "dark" else "🌙"
label = " Light Mode" if st.session_state.theme == "dark" else " Dark Mode"

# --- 4. MAIN UI LAYOUT ---
# Left side toggle button as requested
col_toggle, col_spacer = st.columns([2, 10])
with col_toggle:
    st.button(f"{icon}{label}", on_click=toggle_theme, use_container_width=True)

st.markdown("<h1 style='text-align: center;'>🔄 Smart Swap Validator</h1>", unsafe_allow_html=True)

# Ramadan Toggle in original position
is_ramadan = st.checkbox("🌙 Ramadan's shifts (7 hours)")
duration = 7 if is_ramadan else 9

day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hours = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

col1, col2 = st.columns(2)
shift_data = {}

for i, col in enumerate([col1, col2], 1):
    with col:
        st.markdown(f"### 👤 Employee {i}")
        st.text_input("Name", placeholder=f"Employee {i} Name", key=f"name_{i}", label_visibility="collapsed")
        
        for week in ["Current", "Next"]:
            st.write(f"**{week} Week**")
            with st.container(border=True):
                t1, t2, t3 = st.columns([4, 1, 4])
                
                with t1:
                    s_time = st.selectbox(f"Start {week}{i}", hours, 
                                          index=17 if i==1 and week=="Current" else 9, 
                                          key=f"s{i}_{week}")
                with t2:
                    st.markdown("<p style='text-align:center; padding-top:35px;'>to</p>", unsafe_allow_html=True)
                
                with t3:
                    # UPDATED: Using st.text_input (disabled) so it matches the selectbox style exactly
                    e_time = calculate_end_time(s_time, duration)
                    st.text_input(f"End {week}{i}", value=e_time, disabled=True, key=f"disp_e{i}_{week}")
                
                o1, o2 = st.columns(2)
                off1 = o1.selectbox(f"Off 1 {week}{i}", ["None"] + day_list, key=f"o1_{i}_{week}")
                off2 = o2.selectbox(f"Off 2 {week}{i}", ["None"] + [d for d in day_list if d != off1], key=f"o2_{i}_{week}")

                with st.expander("➕ Overtime (Max 2h)"):
                    st.number_input("Before (hrs)", 0, 2, 0, key=f"otb_{i}_{week}")
                    st.number_input("After (hrs)", 0, 2, 0, key=f"ota_{i}_{week}")
                    st.checkbox("Full Day OT", key=f"f_ot_{i}_{week}")
            
            shift_data[f"e{i}_{week}"] = {
                "start": s_time, "end": e_time, 
                "off_days": [off1, off2]
            }

st.divider()

# --- 5. EXECUTION LOGIC ---
if st.button("🚀 Run Swap Check", use_container_width=True):
    for emp_idx in [1, 2]:
        name = st.session_state[f"name_{emp_idx}"] or f"Employee {emp_idx}"
        cur_key = f"e{emp_idx}_Current"
        next_key = f"e{3-emp_idx}_Next"
        
        d_end = get_dt(7, shift_data[cur_key]["end"], is_end_time=True, start_time_str=shift_data[cur_key]["start"])
        d_start = get_dt(8, shift_data[next_key]["start"])

        # OT adjustment
        d_end += timedelta(hours=st.session_state[f"ota_{emp_idx}_Current"])
        d_start -= timedelta(hours=st.session_state[f"otb_{3-emp_idx}_Next"])

        rest = (d_start - d_end).total_seconds() / 3600
        if rest < 12 and not ("Saturday" in shift_data[cur_key]["off_days"] or "Sunday" in shift_data[next_key]["off_days"]):
            st.error(f"❌ {name}: Rest period is only {rest:.1f}h. Swap rejected.")
        else:
            st.success(f"✅ {name}: Schedule is valid.")

st.markdown("<br><center>Created by Abdelrahman heshmat @abheshma</center>", unsafe_allow_html=True)
