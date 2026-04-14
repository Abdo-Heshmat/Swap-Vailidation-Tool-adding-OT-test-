import streamlit as st
from datetime import datetime, timedelta
import random

# --- 1. THEME & INITIALIZATION ---
if 'theme' not in st.session_state: st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

if st.session_state.theme == 'dark':
    bg, box, txt, brd = "#0e1117", "#1e2129", "#ffffff", "#3e4451"
else:
    bg, box, txt, brd = "#f8f9fa", "#ffffff", "#1f2937", "#d1d5db"

st.set_page_config(layout="wide", page_title="Smart Swap Validator")

# --- 2. DATA & HELPERS ---
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hrs = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

def on_load_random():
    for i in [1, 2]:
        st.session_state[f"un{i}"] = random.choice(["Abdelrahman", "Sarah", "Ahmed", "Mariam"])
        for wk in ["Current", "Next"]:
            st.session_state[f"s{i}{wk}"] = random.choice(hrs)
            st.session_state[f"o1{i}{wk}"] = random.choice(days)
            st.session_state[f"o2{i}{wk}"] = random.choice([d for d in days if d != st.session_state[f"o1{i}{wk}"]])
            st.session_state[f"do_ot1_{i}_{wk}"] = False 
            st.session_state[f"do_ot2_{i}_{wk}"] = False
            st.session_state[f"otb_{i}_{wk}"] = 0
            st.session_state[f"ota_{i}_{wk}"] = 0

def get_dt(day_idx, time_str, is_end=False, s_time_str=None):
    base = datetime(2026, 3, 22) 
    dt = base + timedelta(days=day_idx-1)
    t_obj = datetime.strptime(time_str, "%I %p")
    final_dt = datetime.combine(dt, t_obj.time())
    if is_end and s_time_str:
        if t_obj.hour < datetime.strptime(s_time_str, "%I %p").hour: final_dt += timedelta(days=1)
    return final_dt

# --- 3. UI STYLING ---
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
    }}
    .emp-header {{ text-align: center; font-weight: 800; font-size: 22px; margin-bottom: 15px; color: {txt}; }}
    .unified-box {{ height: 42px; display: flex; align-items: center; justify-content: center; font-weight: bold; background-color: {box}; border-radius: 8px; }}
    .test-btn-container {{ position: fixed; bottom: 20px; left: 20px; z-index: 1000; }}
    .results-card {{ padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); }}
    </style>
    """, unsafe_allow_html=True)

l_space, h_col, t_col = st.columns([1, 10, 1])
with t_col: st.button("☀️" if st.session_state.theme == 'dark' else "🌙", on_click=toggle_theme)
with h_col: st.markdown(f'<div class="title-container"><h1>👤🔁👤 Smart Swap Validator Pro</h1></div>', unsafe_allow_html=True)

is_ramadan = st.checkbox("🌙 Ramadan Mode (7h)")
dur = 7 if is_ramadan else 9

# --- 4. MAIN INTERFACE ---
shift_data = {}
c1, c2 = st.columns(2)

for i, col in enumerate([c1, c2], 1):
    with col:
        st.markdown(f"<div class='emp-header'>Employee {i}</div>", unsafe_allow_html=True)
        st.text_input(f"Name {i}", key=f"un{i}", placeholder="Enter Name", label_visibility="collapsed")
        for wk in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"<center><b>🗓️ {wk} Week</b></center>", unsafe_allow_html=True)
                t_cols = st.columns([4, 1, 4])
                with t_cols[0]:
                    s_t = st.selectbox(f"S{i}{wk}", hrs, index=hrs.index(st.session_state.get(f"s{i}{wk}", "11 PM")), key=f"s{i}{wk}", label_visibility="collapsed")
                t_cols[1].markdown("<p style='text-align:center; padding-top:10px;'>to</p>", unsafe_allow_html=True)
                with t_cols[2]:
                    e_t = (datetime.strptime(s_t, "%I %p") + timedelta(hours=dur)).strftime("%I %p")
                    st.markdown(f"<div class='unified-box'>{e_t}</div>", unsafe_allow_html=True)
                
                # MUTUAL EXCLUSION TOGGLES
                o1 = st.selectbox(f"O1{i}{wk}", ["1st Day Off"] + days, key=f"o1{i}{wk}", label_visibility="collapsed")
                # Disable Toggle 1 if Toggle 2 is ON
                st.toggle("Work 6th Day OT", key=f"do_ot1_{i}_{wk}", disabled=st.session_state.get(f"do_ot2_{i}_{wk}", False))
                
                o2 = st.selectbox(f"O2{i}{wk}", ["2nd Day Off"] + [d for d in days if d != o1], key=f"o2{i}{wk}", label_visibility="collapsed")
                # Disable Toggle 2 if Toggle 1 is ON
                st.toggle("Work 7th Day OT", key=f"do_ot2_{i}_{wk}", disabled=st.session_state.get(f"do_ot1_{i}_{wk}", False))
                
                with st.expander("➕ Daily OT (Max 2h)"):
                    cb, ca = st.session_state.get(f"otb_{i}_{wk}", 0), st.session_state.get(f"ota_{i}_{wk}", 0)
                    st.number_input("Before", 0, 2 - ca, key=f"otb_{i}_{wk}")
                    st.number_input("After", 0, 2 - cb, key=f"ota_{i}_{wk}")

            real_offs = []
            if o1 in days and not st.session_state[f"do_ot1_{i}_{wk}"]: real_offs.append(days.index(o1)+1)
            if o2 in days and not st.session_state[f"do_ot2_{i}_{wk}"]: real_offs.append(days.index(o2)+1)
            shift_data[f"e{i}_{wk}"] = {"s": s_t, "e": e_t, "off": real_offs}

st.divider()

# --- 5. VALIDATION ---
if st.button("🚀 Run Swap Check", use_container_width=True):
    results = []
    configs = {1: {"c": "e1_Current", "n": "e1_Next", "idx": 1}, 2: {"c": "e2_Current", "n": "e2_Next", "idx": 2}}
    
    for en, cfg in configs.items():
        name = st.session_state[f"un{en}"] or f"Employee {en}"
        is_exempt = (7 in shift_data[cfg['c']]["off"]) or (1 in shift_data[cfg['n']]["off"])
        
        if is_exempt:
            msg = ["✅ **Rest Rule:** Waived (Day Off on Weekend)."]
        else:
            dt_e = get_dt(7, shift_data[cfg['c']]["e"], True, shift_data[cfg['c']]["s"]) + timedelta(hours=st.session_state.get(f"ota_{cfg['idx']}_Current", 0))
            dt_s = get_dt(8, shift_data[cfg['n']]["s"]) - timedelta(hours=st.session_state.get(f"otb_{cfg['idx']}_Next", 0))
            gap = (dt_s - dt_e).total_seconds() / 3600
            msg = [f"{'✅' if gap >= 12 else '❌'} **Rest Rule:** {gap:.1f}h gap (Min 12h)."]
        
        results.append({"name": name, "msgs": msg})

    success = all("❌" not in "".join(r["msgs"]) for r in results)
    st.markdown(f"<div class='results-card' style='background-color:{'#1b5e20' if success else '#b71c1c'}; color:white;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center; color:white;'>{'✅ Approved' if success else '❌ Rejected'}</h2>", unsafe_allow_html=True)
    for r in results:
        st.markdown(f"<b>{r['name']}</b>", unsafe_allow_html=True)
        for m in r['msgs']: st.markdown(f"<p style='margin:0;'>{m}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="test-btn-container">', unsafe_allow_html=True)
st.button("🎲 Test Data", on_click=on_load_random)
st.markdown('</div>', unsafe_allow_html=True)
