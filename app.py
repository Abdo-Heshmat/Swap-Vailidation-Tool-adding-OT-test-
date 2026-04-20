import streamlit as st
from datetime import datetime, timedelta
import random

# --- 1. INITIALIZATION ---
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hrs = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

if 'theme' not in st.session_state: st.session_state.theme = 'light'
if 'initialized' not in st.session_state:
    for i in [1, 2]:
        st.session_state[f"un{i}"] = ""
        for wk in ["Current", "Next"]:
            st.session_state[f"s{i}{wk}"] = "11 PM"
            st.session_state[f"e{i}{wk}"] = "08 AM" # Default 9h end
            st.session_state[f"o1{i}{wk}"] = "1st Day Off"
            st.session_state[f"o2{i}{wk}"] = "2nd Day Off"
            st.session_state[f"do_ot1_{i}_{wk}"] = False 
            st.session_state[f"do_ot2_{i}_{wk}"] = False
            st.session_state[f"otb_{i}_{wk}"] = 0
            st.session_state[f"ota_{i}_{wk}"] = 0
    st.session_state.initialized = True

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

def on_load_random():
    for i in [1, 2]:
        st.session_state[f"un{i}"] = random.choice(["Abdelrahman", "Sarah", "Ahmed", "Mariam"])
        for wk in ["Current", "Next"]:
            s_rand = random.choice(hrs)
            st.session_state[f"s{i}{wk}"] = s_rand
            # Auto-calc default end for random data
            st.session_state[f"e{i}{wk}"] = (datetime.strptime(s_rand, "%I %p") + timedelta(hours=dur)).strftime("%I %p")
            st.session_state[f"o1{i}{wk}"] = random.choice(days)
            st.session_state[f"o2{i}{wk}"] = random.choice([d for d in days if d != st.session_state[f"o1{i}{wk}"]])

# --- 2. STYLING ---
bg, box, txt, brd = ("#0e1117", "#1e2129", "#ffffff", "#3e4451") if st.session_state.theme == 'dark' else ("#f8f9fa", "#ffffff", "#1f2937", "#d1d5db")

st.set_page_config(layout="wide", page_title="Smart Swap Validator Pro")

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {txt}; max-width: 1100px; margin: 0 auto; }}
    h1 {{ color: {txt}; text-align: center; margin-bottom: 5px; font-weight: 800; }}
    .results-card {{ padding: 25px; border-radius: 15px; margin-top: 20px; text-align: left; }}
    .status-line {{ padding: 5px 0; display: flex; align-items: center; gap: 10px; font-size: 16px; }}
    .footer {{ text-align: center; margin-top: 50px; padding: 20px; color: {txt}; opacity: 0.7; font-size: 14px; border-top: 1px solid {brd}; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
l_space, h_col, t_col = st.columns([1, 10, 1])
with t_col: st.button("☀️" if st.session_state.theme == 'dark' else "🌙", on_click=toggle_theme)
with h_col: st.markdown('<h1>👤🔁👤 Smart Swap Validator Pro</h1>', unsafe_allow_html=True)

is_ramadan = st.checkbox("🌙 Ramadan Mode (7h Shifts)")
dur = 7 if is_ramadan else 9

# --- 4. FORM ---
shift_data = {}
all_days_selected = True 

c1, c2 = st.columns(2)
for i, col in enumerate([c1, c2], 1):
    with col:
        st.markdown(f"### Employee {i}")
        st.text_input(f"Name {i}", key=f"un{i}", placeholder="Enter Name", label_visibility="collapsed")
        
        for wk in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"<center><b>🗓️ {wk} Week</b></center>", unsafe_allow_html=True)
                t_cols = st.columns([4, 1, 4])
                
                # Start Time
                with t_cols[0]:
                    s_t = st.selectbox(f"S{i}{wk}", hrs, key=f"s{i}{wk}", label_visibility="collapsed")
                
                t_cols[1].markdown("<p style='text-align:center; padding-top:10px;'>to</p>", unsafe_allow_html=True)
                
                # --- AUTO-CALC LOGIC FOR END TIME ---
                calc_end = (datetime.strptime(s_t, "%I %p") + timedelta(hours=dur)).strftime("%I %p")
                
                # End Time (User can edit this box freely)
                with t_cols[2]:
                    e_t = st.selectbox(f"E{i}{wk}", hrs, key=f"e{i}{wk}", index=hrs.index(calc_end), label_visibility="collapsed")

                # Day Off & OT Logic
                o1 = st.selectbox(f"O1{i}{wk}", ["1st Day Off"] + days, key=f"o1{i}{wk}", label_visibility="collapsed")
                st.toggle("Work 6th Day OT", key=f"do_ot1_{i}_{wk}", disabled=st.session_state.get(f"do_ot2_{i}_{wk}", False))
                
                o2 = st.selectbox(f"O2{i}{wk}", ["2nd Day Off"] + [d for d in days if d != o1], key=f"o2{i}{wk}", label_visibility="collapsed")
                st.toggle("Work 7th Day OT", key=f"do_ot2_{i}_{wk}", disabled=st.session_state.get(f"do_ot1_{i}_{wk}", False))
                
                if o1 == "1st Day Off" or o2 == "2nd Day Off": all_days_selected = False

                with st.expander("➕ Daily OT"):
                    b_val = st.session_state.get(f"otb_{i}_{wk}", 0)
                    a_val = st.session_state.get(f"ota_{i}_{wk}", 0)
                    st.number_input(f"Before {i}{wk}", 0, 2 - a_val, key=f"otb_{i}_{wk}", label_visibility="collapsed")
                    st.number_input(f"After {i}{wk}", 0, 2 - b_val, key=f"ota_{i}_{wk}", label_visibility="collapsed")

            real_offs = []
            if o1 in days and not st.session_state.get(f"do_ot1_{i}_{wk}", False): real_offs.append(days.index(o1)+1)
            if o2 in days and not st.session_state.get(f"do_ot2_{i}_{wk}", False): real_offs.append(days.index(o2)+1)
            shift_data[f"e{i}_{wk}"] = {"s": s_t, "e": e_t, "off": sorted(real_offs)}

st.divider()

# --- 5. SWAP LOGIC ---
def get_dt(day_idx, time_str, is_end=False, s_time_str=None):
    base = datetime(2026, 4, 19) # Arbitrary Sunday
    dt = base + timedelta(days=day_idx-1)
    t_obj = datetime.strptime(time_str, "%I %p")
    final_dt = datetime.combine(dt, t_obj.time())
    if is_end and s_time_str:
        if t_obj.hour < datetime.strptime(s_time_str, "%I %p").hour: final_dt += timedelta(days=1)
    return final_dt

if st.button("🚀 Run Swap Check", use_container_width=True):
    if not all_days_selected:
        st.error("⚠️ No Days off selected.")
    else:
        swaps = [
            {"name": st.session_state.un1 or "Employee 1", "curr": "e1_Current", "next": "e2_Next", "idx_c": 1, "idx_n": 2},
            {"name": st.session_state.un2 or "Employee 2", "curr": "e2_Current", "next": "e1_Next", "idx_c": 2, "idx_n": 1}
        ]
        
        results = []
        for s in swaps:
            is_exempt = (7 in shift_data[s['curr']]["off"]) or (1 in shift_data[s['next']]["off"])
            dt_e = get_dt(7, shift_data[s['curr']]["e"], True, shift_data[s['curr']]["s"]) + timedelta(hours=st.session_state.get(f"ota_{s['idx_c']}_Current", 0))
            dt_s = get_dt(8, shift_data[s['next']]["s"]) - timedelta(hours=st.session_state.get(f"otb_{s['idx_n']}_Next", 0))
            gap = (dt_s - dt_e).total_seconds() / 3600
            
            l_off = shift_data[s['curr']]["off"][-1] if shift_data[s['curr']]["off"] else 0
            f_off = shift_data[s['next']]["off"][0] if shift_data[s['next']]["off"] else 8
            streak = (7 - l_off) + (f_off - 1)

            results.append({
                "name": s["name"],
                "r_pass": gap >= 12 or is_exempt,
                "r_msg": "Waived (Off Saturday or Sunday)." if is_exempt else f"{gap:.1f}h gap (Min 12h).",
                "s_pass": streak <= 6,
                "s_val": f"{streak} consecutive days (Max 6)."
            })

        all_pass = all(r["r_pass"] and r["s_pass"] for r in results)
        
        # UI Restoration based on image
        st.markdown(f"<div class='results-card'>", unsafe_allow_html=True)
        if all_pass:
            st.markdown(f"## ✅ Swap Approved", unsafe_allow_html=True)
        else:
            st.markdown(f"## ❌ Swap Rejected", unsafe_allow_html=True)
        
        for r in results:
            st.markdown(f"**{r['name']}**")
            st.markdown(f"<div class='status-line'>{'✅' if r['r_pass'] else '❌'} **Rest Rule:** {r['r_msg']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='status-line'>{'✅' if r['s_pass'] else '❌'} **Streak:** {r['s_val']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- 6. FOOTER ---
st.markdown('<div class="test-btn-container">', unsafe_allow_html=True)
st.button("🎲 Test Data For H", on_click=on_load_random)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
    <div class="footer">
        Created by Abdelrahman Heshmat - chime me @abheshma
    </div>
    """, unsafe_allow_html=True)
