import streamlit as st
from datetime import datetime, timedelta

# --- 1. THEME MANAGEMENT ---
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

# --- 2. DYNAMIC NATIVE CSS ---
if st.session_state.theme == "dark":
    bg, txt, card, border = "#0e1117", "#ffffff", "#1d2129", "#3e4451"
else:
    bg, txt, card, border = "#ffffff", "#000000", "#f0f2f6", "#d1d5db"

st.set_page_config(layout="wide", page_title="Swap Validator Pro")

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg} !important; color: {txt} !important; }}
    [data-testid="stHeader"] {{ background-color: {bg} !important; }}
    .stMarkdown, p, label, h1, h2, h3 {{ color: {txt} !important; }}
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {card} !important;
        border: 1px solid {border} !important;
    }}
    /* Style the disabled end-time box to look like the dropdowns */
    input:disabled {{
        background-color: {card} !important;
        color: {txt} !important;
        -webkit-text-fill-color: {txt} !important;
        opacity: 1 !important;
        border: 1px solid {border} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. TOP BAR ---
col_title, col_theme = st.columns([10, 2])
with col_theme:
    icon = "☀️" if st.session_state.theme == "dark" else "🌙"
    label = " Light Mode" if st.session_state.theme == "dark" else " Dark Mode"
    st.button(f"{icon}{label}", on_click=toggle_theme, use_container_width=True)

with col_title:
    st.markdown("<h1>🔄 Smart Swap Validator</h1>", unsafe_allow_html=True)

# --- 4. RAMADAN TOGGLE ---
is_ramadan = st.checkbox("🌙 Ramadan's shifts (7 hours)")
duration = 7 if is_ramadan else 9

# --- 5. LOGIC HELPERS ---
def calculate_end_time(start_time_str, dur):
    start_dt = datetime.strptime(start_time_str, "%I %p")
    end_dt = start_dt + timedelta(hours=dur)
    return end_dt.strftime("%I %p")

def get_dt(day_idx, time_str, is_end_time=False, start_time_str=None):
    base_date = datetime(2026, 3, 22) 
    target_date = base_date + timedelta(days=day_idx-1)
    if is_end_time and start_time_str:
        s_h = datetime.strptime(start_time_str, "%I %p").hour
        e_h = datetime.strptime(time_str, "%I %p").hour
        if e_h < s_h: target_date += timedelta(days=1)
    time_obj = datetime.strptime(time_str, "%I %p").time()
    return datetime.combine(target_date, time_obj)

# --- 6. MAIN FORM ---
day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hours = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

col1, col2 = st.columns(2)
shift_data = {}

for i, col in enumerate([col1, col2], 1):
    with col:
        st.markdown(f"### 👤 Employee {i}")
        st.text_input("Name", placeholder=f"Employee {i} Name", key=f"name_{i}", label_visibility="collapsed")
        
        for week in ["Current", "Next"]:
            st.write(f"**🗓️ {week} Week**")
            with st.container(border=True):
                t1, t2, t3 = st.columns([4, 1, 4])
                with t1:
                    s_time = st.selectbox(f"Start {week}{i}", hours, index=17 if i==1 and week=="Current" else 9, key=f"s{i}_{week}", label_visibility="collapsed")
                with t2:
                    st.markdown("<p style='text-align:center; padding-top:10px;'>to</p>", unsafe_allow_html=True)
                with t3:
                    e_time = calculate_end_time(s_time, duration)
                    st.text_input(f"End {week}{i}", value=e_time, disabled=True, key=f"disp_e{i}_{week}", label_visibility="collapsed")
                
                st.write("Days Off:")
                d_col1, d_col2 = st.columns(2)
                off1 = d_col1.selectbox(f"Off1 {week}{i}", ["First Day off"] + day_list, key=f"o1_{i}_{week}", label_visibility="collapsed")
                off2 = d_col2.selectbox(f"Off2 {week}{i}", ["Second Day off"] + [d for d in day_list if d != off1], key=f"o2_{i}_{week}", label_visibility="collapsed")

                with st.expander("➕ Add Overtime"):
                    st.number_input("OT Before (hrs)", 0, 2, 0, key=f"otb_{i}_{week}")
                    st.number_input("OT After (hrs)", 0, 2, 0, key=f"ota_{i}_{week}")
                    st.checkbox("Full Day OT", key=f"f_ot_{i}_{week}")
            
            shift_data[f"e{i}_{week}"] = {"start": s_time, "end": e_time, "off_days": [off1, off2]}

st.divider()

if st.button("🚀 Run Swap Check", use_container_width=True):
    for emp_idx in [1, 2]:
        name = st.session_state[f"name_{emp_idx}"] or f"Employee {emp_idx}"
        cur_key, next_key = f"e{emp_idx}_Current", f"e{3-emp_idx}_Next"
        
        d_end = get_dt(7, shift_data[cur_key]["end"], True, shift_data[cur_key]["start"])
        d_start = get_dt(8, shift_data[next_key]["start"])

        d_end += timedelta(hours=st.session_state[f"ota_{emp_idx}_Current"])
        d_start -= timedelta(hours=st.session_state[f"otb_{3-emp_idx}_Next"])

        rest = (d_start - d_end).total_seconds() / 3600
        if rest < 12 and not ("Saturday" in shift_data[cur_key]["off_days"] or "Sunday" in shift_data[next_key]["off_days"]):
            st.error(f"❌ {name}: Rest period is only {rest:.1f}h.")
        else:
            st.success(f"✅ {name}: Valid schedule.")

st.markdown("<br><center>Created by Abdelrahman heshmat @abheshma</center>", unsafe_allow_html=True)
