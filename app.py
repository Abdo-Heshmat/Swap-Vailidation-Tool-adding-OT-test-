import streamlit as st
from datetime import datetime, timedelta
import random

# --- 1. THEME & INITIALIZATION ---
if 'theme' not in st.session_state: st.session_state.theme = 'light'
def toggle_theme(): st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

if st.session_state.theme == 'dark':
    bg, box, txt, brd = "#0e1117", "#1e2129", "#ffffff", "#3e4451"
else:
    bg, box, txt, brd = "#f8f9fa", "#ffffff", "#1f2937", "#d1d5db"

st.set_page_config(layout="wide", page_title="Professional Swap Validator")

# --- 2. DYNAMIC HELPERS ---
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hrs = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

def get_dt(day_idx, time_str, is_end=False, s_time_str=None):
    today = datetime.now()
    start_of_week = today - timedelta(days=(today.weekday() + 1) % 7)
    dt = start_of_week + timedelta(days=day_idx-1)
    t_obj = datetime.strptime(time_str, "%I %p")
    final_dt = datetime.combine(dt, t_obj.time())
    if is_end and s_time_str:
        if t_obj.hour < datetime.strptime(s_time_str, "%I %p").hour: final_dt += timedelta(days=1)
    return final_dt

# --- 3. UI STYLING ---
st.markdown(f"""<style>
    .stApp {{ background-color: {bg}; color: {txt}; max-width: 1200px; margin: 0 auto; }}
    .emp-card {{ background-color: {box}; border: 1px solid {brd}; border-radius: 15px; padding: 20px; margin-bottom: 20px; }}
    .results-card {{ padding: 25px; border-radius: 15px; margin-top: 20px; border: 1px solid rgba(255,255,255,0.1); }}
    .status-msg {{ font-size: 14px; margin: 4px 0; padding: 5px; border-radius: 5px; }}
</style>""", unsafe_allow_html=True)

st.markdown(f"<h1 style='text-align:center;'>👤🔁👤 Smart Swap Validator Pro</h1>", unsafe_allow_html=True)

is_ramadan = st.checkbox("🌙 Ramadan Mode (7h Shift)")
dur = 7 if is_ramadan else 9

# --- 4. DATA INPUT ---
shift_data = {}
c1, c2 = st.columns(2)

for i, col in enumerate([c1, c2], 1):
    with col:
        st.markdown(f"### Employee {i}")
        name = st.text_input(f"Name {i}", key=f"un{i}", placeholder=f"Enter Name", label_visibility="collapsed")
        for wk in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"<center><b>🗓️ {wk} Week</b></center>", unsafe_allow_html=True)
                s_t = st.selectbox(f"Shift Start {i}{wk}", hrs, index=hrs.index(st.session_state.get(f"s{i}{wk}", "09 AM")), key=f"s{i}{wk}", label_visibility="collapsed")
                e_t = (datetime.strptime(s_t, "%I %p") + timedelta(hours=dur)).strftime("%I %p")
                st.info(f"Shift: {s_t} to {e_t}")
                
                o1 = st.selectbox(f"Off Day 1 {i}{wk}", ["None"] + days, key=f"o1{i}{wk}")
                ot1 = st.toggle("Work 6th Day OT", key=f"do_ot1_{i}_{wk}")
                o2 = st.selectbox(f"Off Day 2 {i}{wk}", ["None"] + [d for d in days if d != o1], key=f"o2{i}{wk}")
                ot2 = st.toggle("Work 7th Day OT", key=f"do_ot2_{i}_{wk}")
                
                with st.expander("Daily OT (Max 2h)"):
                    otb = st.number_input(f"Before {i}{wk}", 0, 2, key=f"otb_{i}_{wk}")
                    ota = st.number_input(f"After {i}{wk}", 0, 2, key=f"ota_{i}_{wk}")

            # CRITICAL: A day is only 'OFF' if OT toggle is FALSE
            actual_offs = []
            if o1 in days and not ot1: actual_offs.append(days.index(o1)+1)
            if o2 in days and not ot2: actual_offs.append(days.index(o2)+1)
            
            shift_data[f"e{i}_{wk}"] = {
                "s": s_t, "e": e_t, "off": actual_offs, 
                "otb": otb, "ota": ota, "name": name or f"Emp {i}"
            }

# --- 5. VALIDATION ENGINE ---
if st.button("🚀 RUN COMPLIANCE CHECK", use_container_width=True):
    results = []
    
    # Validation Map: 
    # Employee 1 takes Employee 2's Next Week
    # Employee 2 takes Employee 1's Next Week
    checks = [
        {"id": 1, "cur": "e1_Current", "nxt": "e2_Next", "nxt_id": 2},
        {"id": 2, "cur": "e2_Current", "nxt": "e1_Next", "nxt_id": 1}
    ]

    for check in checks:
        emp_name = shift_data[check['cur']]['name']
        msgs = []
        fail = False
        
        # 1. 12-HOUR REST RULE (Between Saturday and Sunday)
        is_exempt = (7 in shift_data[check['cur']]['off']) or (1 in shift_data[check['nxt']]['off'])
        
        if is_exempt:
            msgs.append("✅ **Rest Rule:** Waived (Has a full rest day between weeks).")
        else:
            # Saturday End + OT After
            dt_e = get_dt(7, shift_data[check['cur']]['e'], True, shift_data[check['cur']]['s']) + timedelta(hours=shift_data[check['cur']]['ota'])
            # Sunday Start - OT Before
            dt_s = get_dt(8, shift_data[check['nxt']]['s']) - timedelta(hours=shift_data[check['nxt']]['otb'])
            
            gap = (dt_s - dt_e).total_seconds() / 3600
            if gap >= 12:
                msgs.append(f"✅ **Rest Rule:** Valid {gap:.1f}h transition gap.")
            else:
                msgs.append(f"❌ **Rest Rule:** REJECTED. Gap is {gap:.1f}h (12h required).")
                fail = True

        # 2. 6-DAY CONSECUTIVE RULE
        # Logic: If OT was toggled ON for an off day, that day is counted as a WORK day.
        w1_work = [d for d in range(1, 8) if d not in shift_data[check['cur']]['off']]
        w2_work = [d for d in range(8, 15) if (d-7) not in shift_data[check['nxt']]['off']]
        combined_schedule = sorted(w1_work + w2_work)
        
        max_streak = 0
        current_streak = 0
        for day in range(1, 15):
            if day in combined_schedule:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        if max_streak <= 6:
            msgs.append(f"✅ **Consecutive Rule:** Passed ({max_streak} days streak).")
        else:
            msgs.append(f"❌ **Consecutive Rule:** REJECTED. Swap creates a {max_streak}-day streak.")
            fail = True

        results.append({"name": emp_name, "msgs": msgs, "fail": fail})

    # --- 6. DISPLAY RESULTS ---
    overall_fail = any(r['fail'] for r in results)
    res_bg = "#b71c1c" if overall_fail else "#1b5e20"
    
    st.markdown(f"<div class='results-card' style='background-color:{res_bg}; color:white;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center;'>{'❌ SWAP REJECTED' if overall_fail else '✅ SWAP APPROVED'}</h2>", unsafe_allow_html=True)
    
    for r in results:
        st.markdown(f"#### {r['name']}")
        for m in r['msgs']:
            st.markdown(f"<div class='status-msg'>{m}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
