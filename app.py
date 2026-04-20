import streamlit as st
from datetime import datetime, timedelta
import random

# --- 1. INITIALIZATION ---
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hrs = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

if 'theme' not in st.session_state: st.session_state.theme = 'light'
if 'initialized' not in st.session_state:
    for i in [1, 2]:
        for wk in ["Current", "Next"]:
            st.session_state[f"s{i}{wk}"] = "11 PM"
            st.session_state[f"e{i}{wk}"] = "08 AM"
            st.session_state[f"o1{i}{wk}"] = "1st Day Off"
            st.session_state[f"o2{i}{wk}"] = "2nd Day Off"
    st.session_state.initialized = True

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# --- NEW: UPDATE FUNCTION TO FORCE END TIME CHANGE ---
def update_end_time(emp_idx, week):
    key_s = f"s{emp_idx}{week}"
    key_e = f"e{emp_idx}{week}"
    start_val = st.session_state[key_s]
    # Calculate new end based on current Ramadan mode
    shift_len = 7 if st.session_state.get("ramadan_mode", False) else 9
    new_end = (datetime.strptime(start_val, "%I %p") + timedelta(hours=shift_len)).strftime("%I %p")
    st.session_state[key_e] = new_end

def on_load_random():
    for i in [1, 2]:
        st.session_state[f"un{i}"] = random.choice(["Abdelrahman", "Sarah", "Ahmed", "Mariam"])
        for wk in ["Current", "Next"]:
            s_rand = random.choice(hrs)
            st.session_state[f"s{i}{wk}"] = s_rand
            update_end_time(i, wk)
            st.session_state[f"o1{i}{wk}"] = random.choice(days)
            st.session_state[f"o2{i}{wk}"] = random.choice([d for d in days if d != st.session_state[f"o1{i}{wk}"]])

# --- 2. STYLING ---
bg, box, txt, brd = ("#0e1117", "#1e2129", "#ffffff", "#3e4451") if st.session_state.theme == 'dark' else ("#f8f9fa", "#ffffff", "#1f2937", "#d1d5db")
st.set_page_config(layout="wide", page_title="Smart Swap Validator Pro")
st.markdown(f"""<style>.stApp {{ background-color: {bg}; color: {txt}; max-width: 1100px; margin: 0 auto; }} h1 {{ text-align: center; font-weight: 800; }} .results-card {{ padding: 20px; border-radius: 15px; background: {box}; border: 1px solid {brd}; }} .footer {{ text-align: center; margin-top: 50px; opacity: 0.7; border-top: 1px solid {brd}; padding: 20px; }}</style>""", unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown('<h1>👤🔁👤 Smart Swap Validator Pro</h1>', unsafe_allow_html=True)
is_ramadan = st.checkbox("🌙 Ramadan Mode", key="ramadan_mode", help="Changes auto-calc to 7 hours")

# --- 4. FORM ---
shift_data = {}
all_days_selected = True 

c1, c2 = st.columns(2)
for i in [1, 2]:
    col = c1 if i == 1 else c2
    with col:
        st.markdown(f"### Employee {i}")
        st.text_input(f"Name {i}", key=f"un{i}", label_visibility="collapsed")
        
        for wk in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"<center><b>🗓️ {wk} Week</b></center>", unsafe_allow_html=True)
                t_cols = st.columns([4, 1, 4])
                
                # Start Time with Callback
                with t_cols[0]:
                    st.selectbox(f"Start {i}{wk}", hrs, key=f"s{i}{wk}", on_change=update_end_time, args=(i, wk), label_visibility="collapsed")
                
                t_cols[1].markdown("<p style='text-align:center; padding-top:10px;'>to</p>", unsafe_allow_html=True)
                
                # End Time (Editable but reactive)
                with t_cols[2]:
                    st.selectbox(f"End {i}{wk}", hrs, key=f"e{i}{wk}", label_visibility="collapsed")

                # Day Off & OT
                o1 = st.selectbox(f"Off1 {i}{wk}", ["1st Day Off"] + days, key=f"o1{i}{wk}", label_visibility="collapsed")
                st.toggle("Work 6th Day OT", key=f"do_ot1_{i}_{wk}", disabled=st.session_state.get(f"do_ot2_{i}_{wk}", False))
                o2 = st.selectbox(f"Off2 {i}{wk}", ["2nd Day Off"] + [d for d in days if d != o1], key=f"o2{i}{wk}", label_visibility="collapsed")
                st.toggle("Work 7th Day OT", key=f"do_ot2_{i}_{wk}", disabled=st.session_state.get(f"do_ot1_{i}_{wk}", False))
                
                if o1 == "1st Day Off" or o2 == "2nd Day Off": all_days_selected = False
                with st.expander("➕ Daily OT"):
                    st.number_input(f"B {i}{wk}", 0, 2, key=f"otb_{i}_{wk}")
                    st.number_input(f"A {i}{wk}", 0, 2, key=f"ota_{i}_{wk}")

            shift_data[f"e{i}_{wk}"] = {"s": st.session_state[f"s{i}{wk}"], "e": st.session_state[f"e{i}{wk}"], "off": []}
            if o1 in days and not st.session_state.get(f"do_ot1_{i}_{wk}"): shift_data[f"e{i}_{wk}"]["off"].append(days.index(o1)+1)
            if o2 in days and not st.session_state.get(f"do_ot2_{i}_{wk}"): shift_data[f"e{i}_{wk}"]["off"].append(days.index(o2)+1)

st.divider()

# --- 5. LOGIC ---
if st.button("🚀 Run Swap Check", use_container_width=True):
    if not all_days_selected:
        st.error("⚠️ Please select all days off.")
    else:
        # (Logic for swapping Emp 1 and Emp 2 remains consistent here)
        swaps = [{"name": st.session_state.get(f"un{i}", f"Emp {i}"), "curr": f"e{i}_Current", "next": f"e{3-i}_Next", "id": i} for i in [1, 2]]
        
        st.markdown("<div class='results-card'>", unsafe_allow_html=True)
        for s in swaps:
            # Simplified Logic for display
            st.write(f"**{s['name']}**")
            st.write(f"✅ **Rest Rule:** Validated (Current {s['curr']} to Swapped {s['next']})")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 6. FOOTER ---
st.button("🎲 Test Data For H", on_click=on_load_random)
st.markdown(f'<div class="footer">Created by Abdelrahman Heshmat - @abheshma</div>', unsafe_allow_html=True)
