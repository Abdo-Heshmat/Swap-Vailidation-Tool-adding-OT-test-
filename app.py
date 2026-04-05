import streamlit as st
from datetime import datetime, timedelta

# --- 1. THEME STATE & TOGGLE ---
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

# Define theme-dependent symbols
theme_icon = "☀️" if st.session_state.theme == "dark" else "🌙"
theme_label = "Switch to Light Mode" if st.session_state.theme == "dark" else "Switch to Dark Mode"

# --- 2. NATIVE CSS (Zero Specific Colors) ---
st.set_page_config(layout="wide", page_title="Swap Validator Pro")

# This CSS uses variables that change automatically with the Streamlit theme
st.markdown(f"""
    <style>
    /* Ensure all containers use the same native background */
    .stHeader, .stApp {{
        background-color: transparent !important;
    }}
    
    /* Uniform styling for the 'End Time' display box */
    .unified-box {{
        background-color: var(--secondary-bg-color);
        border: 1px solid var(--border-color);
        color: var(--text-color);
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    /* Center headers */
    h1, h3 {{
        text-align: center;
        margin-bottom: 20px;
    }}

    /* Remove individual box styles to keep everything flat and uniform */
    .stSelectbox, .stNumberInput, .stTextInput {{
        background-color: transparent !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. TOP BAR (Theme Toggle) ---
col_title, col_theme = st.columns([9, 2])
with col_theme:
    st.button(f"{theme_icon} {theme_label}", on_click=toggle_theme, use_container_width=True)

with col_title:
    st.markdown("<h1>🔄 Smart Swap Validator</h1>", unsafe_allow_html=True)

# --- 4. RAMADAN TOGGLE (Back to original position) ---
is_ramadan = st.checkbox("🌙 Ramadan's shifts (7 hours)")
duration = 7 if is_ramadan else 9

# --- Helper Functions ---
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

# --- 5. MAIN FORM ---
day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hours = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

col1, col2 = st.columns(2)
shift_data = {}

for i, col in enumerate([col1, col2], 1):
    with col:
        st.markdown(f"### 👤 Employee {i}")
        st.text_input("Name", placeholder=f"Enter Employee {i} Name", key=f"name_{i}")
        
        for week in ["Current", "Next"]:
            st.write(f"**{week} Week**")
            # Uniform Card Layout
            with st.container(border=True):
                t1, t2, t3 = st.columns([4, 1, 4])
                with t1:
                    s_time = st.selectbox(f"Start {week}{i}", hours, index=17 if i==1 and week=="Current" else 9, key=f"s{i}_{week}", label_visibility="collapsed")
                with t2:
                    st.markdown("<p style='text-align:center; padding-top:10px;'>to</p>", unsafe_allow_html=True)
                with t3:
                    e_time = calculate_end_time(s_time, duration)
                    st.markdown(f"<div class='unified-box'>{e_time}</div>", unsafe_allow_html=True)
                
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

if st.button("🚀 Run Swap Check", use_container_width=True):
    # Logic implementation
    for emp_idx in [1, 2]:
        name = st.session_state[f"name_{emp_idx}"] or f"Employee {emp_idx}"
        cur_key = f"e{emp_idx}_Current"
        next_key = f"e{3-emp_idx}_Next"
        
        d_end = get_dt(7, shift_data[cur_key]["end"], is_end_time=True, start_time_str=shift_data[cur_key]["start"])
        d_start = get_dt(8, shift_data[next_key]["start"])

        # Add OT adjustment
        d_end += timedelta(hours=st.session_state[f"ota_{emp_idx}_Current"])
        d_start -= timedelta(hours=st.session_state[f"otb_{3-emp_idx}_Next"])

        rest = (d_start - d_end).total_seconds() / 3600
        if rest < 12 and not ("Saturday" in shift_data[cur_key]["off_days"] or "Sunday" in shift_data[next_key]["off_days"]):
            st.error(f"❌ {name}: Rest is only {rest:.1f}h.")
        else:
            st.success(f"✅ {name}: Schedule looks good!")

st.markdown("<br><center>Created by Abdelrahman heshmat @abheshma</center>", unsafe_allow_html=True)
