import streamlit as st
from datetime import datetime, timedelta

# --- 1. THEME MANAGEMENT ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

if st.session_state.theme == 'dark':
    bg, box, txt, brd, btn = "#0e1117", "#1e2129", "#ffffff", "#3e4451", "☀️"
else:
    bg, box, txt, brd, btn = "#ffffff", "#f0f2f6", "#31333F", "#d3d3d3", "🌙"

st.set_page_config(layout="wide", page_title="Smart Swap Validator")

# Custom CSS
st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {txt}; max-width: 1100px; margin: 0 auto; }}
    div[data-testid="stVerticalBlockBorderWrapper"], .stSelectbox div[data-baseweb="select"],
    input[type="text"], .unified-box, .stNumberInput input {{
        background-color: {box} !important; color: {txt} !important;
        border: 1px solid {brd} !important; border-radius: 8px !important;
    }}
    .unified-box {{ 
        height: 42px; display: flex; align-items: center; justify-content: center; 
        font-weight: bold; background-color: {box}; border: 1px solid {brd}; border-radius: 8px;
    }}
    h1 {{ color: {txt}; display: flex; align-items: center; justify-content: center; font-size: 28px; }}
    h3 {{ color: {txt}; text-align: center; margin-bottom: 20px; }}
    .shift-label {{ font-size: 14px; font-weight: bold; margin-bottom: 5px; color: {txt}; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC FUNCTIONS ---
def get_dt(day_idx, time_str, is_end=False, s_time_str=None):
    base = datetime(2026, 3, 22) 
    dt = base + timedelta(days=day_idx-1)
    t_obj = datetime.strptime(time_str, "%I %p")
    final_dt = datetime.combine(dt, t_obj.time())
    if is_end and s_time_str:
        s_obj = datetime.strptime(s_time_str, "%I %p")
        if t_obj.hour < s_obj.hour:
            final_dt += timedelta(days=1)
    return final_dt

# --- 3. CUSTOM ICON & HEADER ---
custom_swap_svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="35" height="35" viewBox="0 0 40 40">
        <circle cx="15.8" cy="17.6" r="14.4" fill="none" stroke="{txt}" stroke-width="2.1"/>
        <circle cx="28.9" cy="11.2" r="6.2" fill="none" stroke="{txt}" stroke-width="2.1"/>
        <path d="M25.8 14.3 C25.8 12.6, 32.0 12.6, 32.0 14.3 Z" fill="{txt}"/>
        <circle cx="12.0" cy="24.3" r="6.2" fill="none" stroke="{txt}" stroke-width="2.1"/>
        <path d="M8.9 27.4 C8.9 25.7, 15.1 25.7, 15.1 27.4 Z" fill="{txt}"/>
    </svg>
"""

h_col, t_col = st.columns([9, 1])
with t_col:
    st.button(btn, on_click=toggle_theme)
with h_col:
    st.markdown(f"<h1><span style='margin-right:15px;'>{custom_swap_svg}</span>Smart Swap Validator Pro</h1>", unsafe_allow_html=True)

# --- 4. GLOBAL SETTINGS ---
is_ramadan = st.checkbox("🌙 Ramadan Mode (7h)")
dur = 7 if is_ramadan else 9

days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hrs = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

shift_data = {}
c1, c2 = st.columns(2)

for i, col in enumerate([c1, c2], 1):
    with col:
        st.markdown(f"### 👤 Employee {i}")
        st.text_input("Name", key=f"un{i}", placeholder=f"Enter Employee {i} Name", label_visibility="collapsed")
        
        for wk in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"<center><b>🗓️ {wk} Week</b></center>", unsafe_allow_html=True)
                
                # HEADERS for Start and End
                h1, h2, h3 = st.columns([4, 1, 4])
                h1.markdown("<p class='shift-label'>Start of shift</p>", unsafe_allow_html=True)
                h3.markdown("<p class='shift-label'>End of shift</p>", unsafe_allow_html=True)
                
                t1, t2, t3 = st.columns([4, 1, 4])
                with t1: 
                    s_t = st.selectbox(f"Start{i}{wk}", hrs, index=9, key=f"s{i}{wk}", label_visibility="collapsed")
                with t2: 
                    st.markdown("<p style='text-align:center; padding-top:10px;'>to</p>", unsafe_allow_html=True)
                with t3:
                    # AUTOMATIC CALCULATION logic inside the loop
                    start_dt = datetime.strptime(s_t, "%I %p")
                    end_dt = start_dt + timedelta(hours=dur)
                    e_t = end_dt.strftime("%I %p")
                    # Displaying the calculated end time in a clean, matching box
                    st.markdown(f"<div class='unified-box'>{e_t}</div>", unsafe_allow_html=True)
                
                st.markdown("<p class='shift-label' style='margin-top:10px;'>Days Off:</p>", unsafe_allow_html=True)
                d1, d2 = st.columns(2)
                off1 = d1.selectbox(f"O1{i}{wk}", ["First Day off"] + days, key=f"o1{i}{wk}", label_visibility="collapsed")
                off2 = d2.selectbox(f"O2{i}{wk}", ["Second Day off"] + [d for d in days if d != off1], key=f"o2{i}{wk}", label_visibility="collapsed")
                
                with st.expander("➕ Overtime (Max 2h)"):
                    st.number_input("Before (hrs)", 0, 2, 0, key=f"otb_{i}_{wk}")
                    st.number_input("After (hrs)", 0, 2, 0, key=f"ota_{i}_{wk}")
                    st.checkbox("Full Day OT", key=f"f_ot_{i}_{wk}")
            
            real_offs = sorted([days.index(o)+1 for o in [off1, off2] if o in days])
            shift_data[f"e{i}_{wk}"] = {"s": s_t, "e": e_t, "off": real_offs}

st.divider()

# --- 5. RUN CHECK ---
if st.button("🚀 Run Swap Check", use_container_width=True):
    results = []
    configs = {1: {"c": "e1_Current", "n": "e2_Next", "u": "un1"}, 2: {"c": "e2_Current", "n": "e1_Next", "u": "un2"}}

    for en, cfg in configs.items():
        reasons = []
        name = st.session_state[cfg['u']] or f"Employee {en}"
        
        is_exempt = (7 in shift_data[cfg['c']]["off"]) or (1 in shift_data[cfg['n']]["off"])
        if is_exempt:
            reasons.append("✅ Rest rule waived (Off Saturday or Sunday).")
        else:
            dt_e = get_dt(7, shift_data[cfg['c']]["e"], True, shift_data[cfg['c']]["s"])
            dt_s = get_dt(8, shift_data[cfg['n']]["s"])
            dt_e += timedelta(hours=st.session_state[f"ota_{en}_Current"])
            dt_s -= timedelta(hours=st.session_state[f"otb_{3-en}_Next"])
            
            rest = (dt_s - dt_e).total_seconds() / 3600
            if rest < 12: reasons.append(f"❌ Insufficient Rest: **{rest:.1f}h**")
            else: reasons.append(f"✅ Sufficient Rest: **{rest:.1f}h**")
            
        results.append({"name": name, "msgs": reasons})

    success = all("❌" not in " ".join(r["msgs"]) for r in results)
    st.markdown(f"<div style='background-color:{'#1b5e20' if success else '#b71c1c'}; padding:20px; border-radius:12px; color:white;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center; color:white;'>{'✅ Swap Approved' if success else '❌ Swap Rejected'}</h2>", unsafe_allow_html=True)
    for r in results:
        st.write(f"**{r['name']}**")
        for m in r['msgs']: st.write(m)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><center>Created by Abdelrahman heshmat @abheshma</center>", unsafe_allow_html=True)
