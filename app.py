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

# Custom CSS for UI and the small bottom-left test button
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
    
    /* Fixed small button style for testing */
    .test-btn-container {{
        position: fixed;
        bottom: 20px;
        left: 20px;
        z-index: 999;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LISTS & RANDOMIZER ---
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hrs = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

def load_random_data():
    for i in [1, 2]:
        st.session_state[f"un{i}"] = random.choice(["Abdelrahman", "Sarah", "Ahmed", "Mariam"])
        for wk in ["Current", "Next"]:
