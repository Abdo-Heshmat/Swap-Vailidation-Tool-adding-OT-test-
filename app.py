import streamlit as st
from datetime import datetime, timedelta
import random

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
    .emp-header {{ color: {txt}; text-align: center; margin-bottom: 10px; font-weight: bold; font-size: 22px; }}
    .shift-label {{ font-size: 13px; font-weight: bold; margin-bottom: 5px; color: {txt}; opacity: 0.8; }}
    
    /* Center the Name Input */
    div[data-testid="stTextInput"] > div {{ text-align: center; }}
    
    .test-btn-container {{ position: fixed; bottom: 20px; left: 20px; z-index: 1000; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LISTS & CALLBACK ---
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hrs = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

def on_load_random():
    for i in [1, 2]:
        st.session_state[f"un{i}"] = random.choice(["Abdelrahman", "Sarah", "Ahmed", "Mariam"])
        for wk in ["Current", "Next"]:
            st.session_state[f"s{i}{wk}"] = random.choice(hrs)
            st.session_state[f"o1{i}{wk}"] = random.choice(days)
            st.session_state[f"o2{i}{wk}"] = random.choice([d for d in days if d != st.session_state[f"o1{i}{wk}"]])
            st.session_state[f"do_ot1_{i}_{wk}"] = random.choice([True, False])
            st.session_state[f"do_ot2_{i}_{wk}"] = random.choice([True, False])

# --- 3. HELPER FUNCTIONS ---
def get_dt(day_idx, time_str, is_end=False, s_time_str=None):
    base = datetime(2026, 3, 22) 
    dt = base + timedelta(days=day_idx-1)
    t_obj = datetime.strptime(time_str, "%I %p")
    final_dt = datetime.combine(dt, t_obj.time())
    if is_end and s_time_str:
        s_obj = datetime.strptime(s_time_str, "%I %p")
        if t_obj.hour < s_obj.hour: final_dt += timedelta(days=1)
    return final_dt

# --- 4. HEADER ---
h_col, t_col = st.columns([9, 1])
with t_col: st.button(btn, on_click=toggle_theme)
with h_col: st.markdown(f"<h1><span style='margin-right:15px;'>👤🔁👤</span>Smart Swap Validator Pro</h1>", unsafe_allow_html=True)

is_ramadan = st.checkbox("🌙 Ramadan Mode (7h)")
dur = 7 if is_ramadan else 9

# --- 5. UI GENERATION ---
shift_data = {}
c1, c2 = st.columns(2)

for i, col in enumerate([c1, c2], 1):
    with col:
        st.markdown(f"<div class='emp-header'>👤 Employee {i}</div>", unsafe_allow_html=True)
        st.text_input(f"Name {i}", key=f"un{i}", placeholder=f"Enter Employee {i} Name", label_visibility="collapsed")
        
        for wk in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"<center><b>🗓️ {wk} Week</b></center>", unsafe_allow_html=True)
                
                # Shift Times
                h1, h2, h3 = st.columns([4, 1, 4])
                h1.markdown("<p class='shift-label'>Start of shift</p>", unsafe_allow_html=True)
                h3.markdown("<p class='shift-label'>End of shift</p>", unsafe_allow_html=True)
                
                t1, t2, t3 = st.columns([4, 1, 4])
                with t1:
                    curr_val = st.session_state.get(f"s{i}{wk}", "09 AM")
                    s_t = st.selectbox(f"S{i}{wk}", hrs, index=hrs.index(curr_val) if curr_val in hrs else 9, key=f"s{i}{wk}", label_visibility="collapsed")
                with t2: st.markdown("<p style='text-align:center; padding-top:10px;'>to</p>", unsafe_allow_html=True)
                with t3:
                    e_t = (datetime.strptime(s_t, "%I %p") + timedelta(hours=dur)).strftime("%I %p")
                    st.markdown(f"<div class='unified-box'>{e_t}</div>", unsafe_allow_html=True)
                
                # Days Off with OT Toggle
                st.markdown("<p class='shift-label' style='margin-top:10px;'>Days Off & OT Status:</p>", unsafe_allow_html=True)
                
                # Day Off 1
                row1_col1, row1_col2 = st.columns([2, 1])
                o1_val = st.session_state.get(f"o1{i}{wk}", "First Day off")
                off1 = row1_col1.selectbox(f"O1{i}{wk}", ["First Day off"] + days, index=(days.index(o1_val)+1 if o1_val in days else 0), key=f"o1{i}{wk}", label_visibility="collapsed")
                do_ot1 = row1_col2.toggle("Work OT", key=f"do_ot1_{i}_{wk}")
                
                # Day Off 2
                row2_col1, row2_col2 = st.columns([2, 1])
                remain = [d for d in days if d != off1]
                o2_val = st.session_state.get(f"o2{i}{wk}", "Second Day off")
                off2 = row2_col1.selectbox(f"O2{i}{wk}", ["Second Day off"] + remain, index=(remain.index(o2_val)+1 if o2_val in remain else 0), key=f"o2{i}{wk}", label_visibility="collapsed")
                do_ot2 = row2_col2.toggle("Work OT", key=f"do_ot2_{i}_{wk}")
                
                with st.expander("➕ Daily Overtime (Max 2h)"):
                    ot_b_key, ot_a_key = f"otb_{i}_{wk}", f"ota_{i}_{wk}"
                    st.number_input("Before (hrs)", 0, 2, 0, key=ot_b_key, disabled=st.session_state.get(ot_a_key, 0) > 0)
                    st.number_input("After (hrs)", 0, 2, 0, key=ot_a_key, disabled=st.session_state.get(ot_b_key, 0) > 0)
            
            # Logic: If OT toggle is ON, remove that day from the "off" list
            actual_offs = []
            if off1 in days and not do_ot1: actual_offs.append(days.index(off1)+1)
            if off2 in days and not do_ot2: actual_offs.append(days.index(off2)+1)
            
            shift_data[f"e{i}_{wk}"] = {"s": s_t, "e": e_t, "off": sorted(actual_offs)}

st.divider()

# --- 6. LOGIC & RESULTS ---
if st.button("🚀 Run Swap Check", use_container_width=True):
    results = []
    configs = {1: {"c": "e1_Current", "n": "e2_Next", "u": "un1"}, 2: {"c": "e2_Current", "n": "e1_Next", "u": "un2"}}
    for en, cfg in configs.items():
        reasons = []
        name = st.session_state[cfg['u']] or f"Employee {en}"
        
        # Check if the "Bridge" (Saturday/Sunday) is a Day Off
        is_exempt = (7 in shift_data[cfg['c']]["off"]) or (1 in shift_data[cfg['n']]["off"])
        
        if is_exempt:
            reasons.append("✅ **Rest Rule Approved:** Bridge rest is safe (Off Sat or Sun).")
        else:
            # Shift End + OT After
            dt_e = get_dt(7, shift_data[cfg['c']]["e"], True, shift_data[cfg['c']]["s"]) + timedelta(hours=st.session_state.get(f"ota_{en}_Current", 0))
            # Shift Start - OT Before
            dt_s = get_dt(8, shift_data[cfg['n']]["s"]) - timedelta(hours=st.session_state.get(f"otb_{en}_Next", 0))
            rest = (dt_s - dt_e).total_seconds() / 3600
            if rest < 12: reasons.append(f"❌ **Rest Rule Rejected:** Only **{rest:.1f}h** rest gap (Min 12h required).")
            else: reasons.append(f"✅ **Rest Rule Approved:** **{rest:.1f}h** rest gap provided.")
        
        results.append({"name": name, "msgs": reasons})

    success = all("❌" not in " ".join(r["msgs"]) for r in results)
    st.markdown(f"<div style='background-color:{'#1b5e20' if success else '#b71c1c'}; padding:20px; border-radius:12px; color:white;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center; color:white;'>{'✅ Swap Approved' if success else '❌ Swap Rejected'}</h2>", unsafe_allow_html=True)
    for r in results:
        st.write(f"**{r['name']}**")
        for m in r['msgs']: st.write(f"- {m}")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><center>Created by Abdelrahman heshmat @abheshma</center>", unsafe_allow_html=True)

# --- 7. MINI TEST BUTTON ---
st.markdown('<div class="test-btn-container">', unsafe_allow_html=True)
st.button("🎲 Test Data", key="mini_test_btn", on_click=on_load_random)
st.markdown('</div>', unsafe_allow_html=True)
