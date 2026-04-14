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

st.set_page_config(layout="wide", page_title="Smart Swap Validator Pro")

# --- 2. DYNAMIC HELPERS ---
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
    today = datetime.now()
    start_of_week = today - timedelta(days=(today.weekday() + 1) % 7)
    dt = start_of_week + timedelta(days=day_idx-1)
    t_obj = datetime.strptime(time_str, "%I %p")
    final_dt = datetime.combine(dt, t_obj.time())
    if is_end and s_time_str:
        if t_obj.hour < datetime.strptime(s_time_str, "%I %p").hour: 
            final_dt += timedelta(days=1)
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
    .results-card {{ padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); margin-top: 20px; }}
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
        name_input = st.text_input(f"Name {i}", key=f"un{i}", placeholder=f"Employee {i} Name", label_visibility="collapsed")
        
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
                
                o1 = st.selectbox(f"O1{i}{wk}", ["None"] + days, key=f"o1{i}{wk}", label_visibility="collapsed")
                ot1 = st.toggle("Work 6th Day OT", key=f"do_ot1_{i}_{wk}")
                
                o2 = st.selectbox(f"O2{i}{wk}", ["None"] + [d for d in days if d != o1], key=f"o2{i}{wk}", label_visibility="collapsed")
                ot2 = st.toggle("Work 7th Day OT", key=f"do_ot2_{i}_{wk}")
                
                with st.expander("➕ Daily OT (Max 2h)"):
                    otb = st.number_input(f"Before {i}{wk}", 0, 2, key=f"otb_{i}_{wk}")
                    ota = st.number_input(f"After {i}{wk}", 0, 2, key=f"ota_{i}_{wk}")

            # Data Capture
            real_offs = []
            if o1 in days and not ot1: real_offs.append(days.index(o1)+1)
            if o2 in days and not ot2: real_offs.append(days.index(o2)+1)
            shift_data[f"e{i}_{wk}"] = {"s": s_t, "e": e_t, "off": real_offs, "otb": otb, "ota": ota, "name": name_input or f"Emp {i}"}

st.divider()

# --- 5. THE REAL CROSS-SWAP VALIDATOR ---
if st.button("🚀 Run Swap Check", use_container_width=True):
    results = []
    
    # Logic: E1 Cur -> E2 Next AND E2 Cur -> E1 Next
    checks = [
        {"id": 1, "cur": "e1_Current", "nxt": "e2_Next", "nxt_id": 2},
        {"id": 2, "cur": "e2_Current", "nxt": "e1_Next", "nxt_id": 1}
    ]

    for check in checks:
        emp_name = shift_data[check['cur']]['name']
        target_name = shift_data[check['nxt']]['name']
        msgs = []
        fail = False
        
        # RULE 1: 12-HOUR TRANSITION (Sat to Sun)
        is_exempt = (7 in shift_data[check['cur']]['off']) or (1 in shift_data[check['nxt']]['off'])
        if is_exempt:
            msgs.append("✅ **Rest Rule:** Waived (Weekend Day Off).")
        else:
            # Saturday End + OT After
            dt_e = get_dt(7, shift_data[check['cur']]['e'], True, shift_data[check['cur']]['s']) + timedelta(hours=shift_data[check['cur']]['ota'])
            # Sunday Start - OT Before
            dt_s = get_dt(8, shift_data[check['nxt']]['s']) - timedelta(hours=shift_data[check['nxt']]['otb'])
            
            gap = (dt_s - dt_e).total_seconds() / 3600
            if gap >= 12:
                msgs.append(f"✅ **Rest Rule:** Valid {gap:.1f}h gap between weeks.")
            else:
                msgs.append(f"❌ **Rest Rule:** REJECTED. Only {gap:.1f}h gap into {target_name}'s Sunday.")
                fail = True

        # RULE 2: 6-DAY CONSECUTIVE RULE
        w1_work = [d for d in range(1, 8) if d not in shift_data[check['cur']]['off']]
        w2_work = [d for d in range(8, 15) if (d-7) not in shift_data[check['nxt']]['off']]
        combined = sorted(w1_work + w2_work)
        
        streak, max_s = 0, 0
        for day in range(1, 15):
            if day in combined:
                streak += 1
                max_s = max(max_s, streak)
            else: streak = 0
            
        if max_s <= 6:
            msgs.append(f"✅ **Consecutive Rule:** Passed ({max_s} days streak).")
        else:
            msgs.append(f"❌ **Consecutive Rule:** REJECTED. Creates a {max_s}-day streak.")
            fail = True
            
        results.append({"name": emp_name, "msgs": msgs, "fail": fail})

    # Display UI
    all_ok = not any(r['fail'] for r in results)
    res_bg = "#1b5e20" if all_ok else "#b71c1c"
    
    st.markdown(f"<div class='results-card' style='background-color:{res_bg}; color:white;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center; color:white;'>{'✅ Swap Approved' if all_ok else '❌ Swap Rejected'}</h2>", unsafe_allow_html=True)
    for r in results:
        st.markdown(f"<b>{r['name']}</b>", unsafe_allow_html=True)
        for m in r['msgs']: st.markdown(f"<p style='margin:0; font-size: 14px;'>{m}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 6. FLOATING TEST BUTTON ---
st.markdown('<div class="test-btn-container">', unsafe_allow_html=True)
st.button("🎲 Test Random Data", on_click=on_load_random)
st.markdown('</div>', unsafe_allow_html=True)
