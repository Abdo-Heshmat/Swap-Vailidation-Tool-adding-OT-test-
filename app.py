import streamlit as st
from datetime import datetime, timedelta
import random

# --- 1. THEME & INITIALIZATION ---
if 'theme' not in st.session_state: 
    st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

if st.session_state.theme == 'dark':
    bg, box, txt, brd, btn = "#0e1117", "#1e2129", "#ffffff", "#3e4451", "☀️"
    shdw = "rgba(0,0,0,0.5)"
else:
    bg, box, txt, brd, btn = "#f8f9fa", "#ffffff", "#1f2937", "#d1d5db", "🌙"
    shdw = "rgba(31, 41, 55, 0.1)"

st.set_page_config(layout="wide", page_title="Smart Swap Validator")

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {txt}; max-width: 1100px; margin: 0 auto; }}
    .title-container {{ display: flex; justify-content: center; align-items: center; width: 100%; margin-bottom: 20px; }}
    h1 {{ color: {txt}; text-align: center; font-size: 28px; margin: 0; }}
    div[data-testid="stVerticalBlockBorderWrapper"], .stSelectbox div[data-baseweb="select"],
    input[type="text"], .unified-box, .stNumberInput input {{
        background-color: {box} !important; color: {txt} !important;
        border: 1px solid {brd} !important; border-radius: 10px !important;
        text-align: center !important;
        box-shadow: 0 2px 4px {shdw};
    }}
    div[data-testid="stTextInput"] input, .stSelectbox div {{ text-align: center !important; }}
    .emp-header {{ text-align: center; font-weight: 800; font-size: 22px; margin-bottom: 15px; color: {txt}; }}
    .shift-label {{ font-size: 13px; font-weight: 600; text-align: center; margin-bottom: 5px; color: {txt}; opacity: 0.9; }}
    .unified-box {{ height: 42px; display: flex; align-items: center; justify-content: center; font-weight: bold; background-color: {box}; border-radius: 8px; }}
    .test-btn-container {{ position: fixed; bottom: 20px; left: 20px; z-index: 1000; }}
    .results-card {{ padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA & HELPERS ---
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hrs = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

def get_dt(day_idx, time_str, is_end=False, s_time_str=None):
    base = datetime(2026, 3, 22) 
    dt = base + timedelta(days=day_idx-1)
    t_obj = datetime.strptime(time_str, "%I %p")
    final_dt = datetime.combine(dt, t_obj.time())
    if is_end and s_time_str:
        s_obj = datetime.strptime(s_time_str, "%I %p")
        if t_obj.hour < s_obj.hour: final_dt += timedelta(days=1)
    return final_dt

# --- 3. HEADER ---
l_space, h_col, t_col = st.columns([1, 10, 1])
with t_col: st.button(btn, on_click=toggle_theme)
with h_col: st.markdown(f'<div class="title-container"><h1>👤🔁👤 Smart Swap Validator Pro</h1></div>', unsafe_allow_html=True)

is_ramadan = st.checkbox("🌙 Ramadan Mode (7h)")
dur = 7 if is_ramadan else 9

# --- 4. UI ---
shift_data = {}
c1, c2 = st.columns(2)

for i, col in enumerate([c1, c2], 1):
    with col:
        st.markdown(f"<div class='emp-header'>Employee {i}</div>", unsafe_allow_html=True)
        st.text_input(f"Name {i}", key=f"un{i}", placeholder=f"Enter Name", label_visibility="collapsed")
        
        for wk in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"<center><b>🗓️ {wk} Week</b></center>", unsafe_allow_html=True)
                t_cols = st.columns([4, 1, 4])
                with t_cols[0]:
                    s_t = st.selectbox(f"S{i}{wk}", hrs, index=hrs.index(st.session_state.get(f"s{i}{wk}", "09 AM")), key=f"s{i}{wk}", label_visibility="collapsed")
                t_cols[1].markdown("<p style='text-align:center; padding-top:10px;'>to</p>", unsafe_allow_html=True)
                with t_cols[2]:
                    e_t = (datetime.strptime(s_t, "%I %p") + timedelta(hours=dur)).strftime("%I %p")
                    st.markdown(f"<div class='unified-box'>{e_t}</div>", unsafe_allow_html=True)
                
                # Day Off & OT Toggle Logic
                d1_col1, d1_col2 = st.columns([2, 1])
                off1 = d1_col1.selectbox(f"O1{i}{wk}", ["1st Day Off"] + days, key=f"o1{i}{wk}", label_visibility="collapsed")
                do_ot1 = d1_col2.toggle("Work OT", key=f"do_ot1_{i}_{wk}", disabled=st.session_state.get(f"do_ot2_{i}_{wk}", False))
                
                d2_col1, d2_col2 = st.columns([2, 1])
                remain = [d for d in days if d != off1]
                off2 = d2_col1.selectbox(f"O2{i}{wk}", ["2nd Day Off"] + remain, key=f"o2{i}{wk}", label_visibility="collapsed")
                do_ot2 = d2_col2.toggle("Work OT", key=f"do_ot2_{i}_{wk}", disabled=st.session_state.get(f"do_ot1_{i}_{wk}", False))
                
                with st.expander("➕ OT (Max 2h)"):
                    ot_b = st.number_input("Before", 0, 2, key=f"otb_{i}_{wk}")
                    ot_a = st.number_input("After", 0, 2 - ot_b, key=f"ota_{i}_{wk}")

            # Store actual days off (only if OT toggle is OFF)
            actual_offs = []
            if off1 in days and not do_ot1: actual_offs.append(days.index(off1) + 1)
            if off2 in days and not do_ot2: actual_offs.append(days.index(off2) + 1)
            shift_data[f"e{i}_{wk}"] = {"s": s_t, "e": e_t, "off": actual_offs}

st.divider()

# --- 5. LOGIC CHECK ---
if st.button("🚀 Run Swap Check", use_container_width=True):
    results = []
    configs = {1: {"c": "e1_Current", "n": "e2_Next", "u": "un1", "idx": 1}, 2: {"c": "e2_Current", "n": "e1_Next", "u": "un2", "idx": 2}}
    
    for en, cfg in configs.items():
        reasons = []
        name = st.session_state[cfg['u']] or f"Employee {en}"
        
        # SATURDAY/SUNDAY OFF EXEMPTION
        # If Saturday is off in current week OR Sunday is off in next week, the 12h rule is waived.
        is_sat_off = 7 in shift_data[cfg['c']]["off"]
        is_sun_off = 1 in shift_data[cfg['n']]["off"]
        
        if is_sat_off or is_sun_off:
            reasons.append("✅ **Rest Rule:** Waived (Employee is Off on Saturday or Sunday).")
        else:
            dt_e = get_dt(7, shift_data[cfg['c']]["e"], True, shift_data[cfg['c']]["s"]) + timedelta(hours=st.session_state.get(f"ota_{cfg['idx']}_Current", 0))
            dt_s = get_dt(8, shift_data[cfg['n']]["s"]) - timedelta(hours=st.session_state.get(f"otb_{cfg['idx']}_Next", 0))
            rest = (dt_s - dt_e).total_seconds() / 3600
            reasons.append(f"{'✅' if rest >= 12 else '❌'} **Rest Rule:** {rest:.1f}h gap (Min 12h).")

        results.append({"name": name, "msgs": reasons})

    # UI for Results
    success = all("❌" not in " ".join(r["msgs"]) for r in results)
    color = '#1b5e20' if success else '#b71c1c'
    st.markdown(f"<div class='results-card' style='background-color:{color}; color:white;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center; color:white;'>{'✅ Swap Approved' if success else '❌ Swap Rejected'}</h2>", unsafe_allow_html=True)
    for r in results:
        st.markdown(f"<b>{r['name']}</b>", unsafe_allow_html=True)
        for m in r['msgs']: st.markdown(f"<p style='margin:0;'>{m}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
