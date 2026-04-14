import streamlit as st
from datetime import datetime, timedelta
import random

# --- 1. THEME & INITIALIZATION ---
if 'theme' not in st.session_state: 
    st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

if st.session_state.theme == 'dark':
    bg, box, txt, brd = "#0e1117", "#1e2129", "#ffffff", "#3e4451"
    shdw = "rgba(0,0,0,0.5)"
else:
    bg, box, txt, brd = "#f8f9fa", "#ffffff", "#1f2937", "#d1d5db"
    shdw = "rgba(31, 41, 55, 0.1)"

st.set_page_config(layout="wide", page_title="Smart Swap Validator Pro")

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
        box-shadow: 0 2px 4px {shdw};
    }}
    .emp-header {{ text-align: center; font-weight: 800; font-size: 22px; margin-bottom: 15px; color: {txt}; }}
    .unified-box {{ height: 42px; display: flex; align-items: center; justify-content: center; font-weight: bold; background-color: {box}; border-radius: 8px; }}
    .test-btn-container {{ position: fixed; bottom: 20px; left: 20px; z-index: 1000; }}
    .results-card {{ padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }}
    .status-line {{ padding: 10px; margin: 8px 0; border-radius: 8px; background: rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; border: 1px solid rgba(255,255,255,0.05); }}
    </style>
    """, unsafe_allow_html=True)

l_space, h_col, t_col = st.columns([1, 10, 1])
with t_col: 
    st.button
