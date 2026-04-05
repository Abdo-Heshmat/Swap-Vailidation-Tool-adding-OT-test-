import streamlit as st
from datetime import datetime, timedelta

# --- Helper Functions ---
def calculate_end_time(start_time_str, duration):
    start_dt = datetime.strptime(start_time_str, "%I %p")
    end_dt = start_dt + timedelta(hours=duration)
    return end_dt.strftime("%I %p")

def get_dt(day_idx, time_str, is_end_time=False, start_time_str=None):
    base_date = datetime(2026, 3, 22) 
    target_date = base_date + timedelta(days=day_idx-1)
    
    if is_end_time and start_time_str:
        s_hour = datetime.strptime(start_time_str, "%I %p").hour
        e_hour = datetime.strptime(time_str, "%I %p").hour
        if e_hour < s_hour:
            target_date += timedelta(days=1)
            
    time_obj = datetime.strptime(time_str, "%I %p").time()
    return datetime.combine(target_date, time_obj)

# --- UI Styling ---
st.set_page_config(layout="wide", page_title="Swap Validator Pro")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; max-width: 1100px; margin: 0 auto; }
    input[type="text"], .stNumberInput input { text-align: center !important; background-color: #1e2129 !important; color: white !important; border: 1px solid #3e4451 !important; border-radius: 8px !important; }
    
    .dark-match-box { 
        background-color: #1e2129; 
        color: white; 
        padding: 0 15px; 
        border-radius: 8px; 
        border: 1px solid #3e4451; 
        text-align: left; 
        font-size: 1rem; 
        height: 45px; 
        line-height: 45px; 
        display: flex; 
        align-items: center; 
        justify-content: space-between;
    }
    .dark-match-box::after { content: '▼'; font-size: 0.6rem; color: #9ea4b0; margin-left: 10px; }

    .rules-box { background-color: #1e2129; padding: 20px; border-radius: 10px; border-left: 5px solid #007bff; margin-bottom: 20px; }
    .status-container { padding: 20px; border-radius: 12px; margin-top: 15px; }
    .approved { background-color: #1b5e20; color: white; border: 2px solid #ffffff; }
    .rejected { background-color: #b71c1c; color: white; border: 2px solid #ffffff; }
    .emp-header { font-weight: bold; font-size: 1.2rem; margin-top: 10px; text-decoration: underline; }
    .reason-item { margin-left: 20px; font-size: 1rem; list-style-type: disc; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🔄 Smart Swap Validator</h1>", unsafe_allow_html=True)

# --- Rules Section ---
with st.expander("📋 View Validation Rules & OT Logic", expanded=False):
    st.markdown("""
    <div class='rules-box'>
        <b>✅ Rules Applied:</b><br>
        * Min 12h rest between shifts (Adjusted automatically if OT is added).<br>
        * Max 6 consecutive working days (Full Day OT adds to this count).<br>
        * <b>OT Limit:</b> Maximum of 2 hours allowed before or after a shift.<br>
        * <b>Exemption:</b> 12h rule waived if Saturday (Day 7) or Sunday (Day 8) is a Day Off.
    </div>
    """, unsafe_allow_html=True)

is_ramadan = st.checkbox("🌙 Ramadan's shifts (7 hours)")
duration = 7 if is_ramadan else 9

day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hours = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

col1, col2 = st.columns(2)
shift_starts, shift_ends, off_counts, off_days = {}, {}, {}, {}

for i, col in enumerate([col1, col2], 1):
    with col:
        st.markdown(f"<h3 style='text-align: center;'>👤 Employee {i}</h3>", unsafe_allow_html=True)
        st.text_input(f"Name {i}", placeholder=f"Employee {i} Name", key=f"user_name_{i}", label_visibility="collapsed")
        
        for week in ["Current", "Next"]:
            with st.container(border=True):
                st.markdown(f"<center><b>🗓️ {week} Week</b></center>", unsafe_allow_html=True)
                
                t1, t2, t3 = st.columns([3, 1, 3])
                with t1:
                    s_time = st.selectbox(f"Start {i}{week}", hours, index=17 if i==1 and week=="Current" else 9, key=f"s{i}_{week}", label_visibility="collapsed")
                with t2: st.write("<br><center>to</center>", unsafe_allow_html=True)
                with t3:
                    e_time = calculate_end_time(s_time, duration)
                    st.markdown(f"<div class='dark-match-box'><span>{e_time}</span></div>", unsafe_allow_html=True)
                    shift_starts[f"e{i}_{week}"] = s_time
                    shift_ends[f"e{i}_{week}"] = e_time

                st.write("Days Off:")
                d_col1, d_col2 = st.columns(2)
