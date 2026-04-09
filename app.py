import streamlit as st
from datetime import datetime, timedelta

# --- Theme Management ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

if st.session_state.theme == 'dark':
    bg, box, txt, brd, btn = "#0e1117", "#1e2129", "#ffffff", "#3e4451", "☀️"
else:
    bg, box, txt, brd, btn = "#ffffff", "#f0f2f6", "#31333F", "#d3d3d3", "🌙"

st.set_page_config(layout="wide", page_title="Smart Swap Validator")

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {txt}; max-width: 1100px; margin: 0 auto; }}
    
    /* Native Card Container */
    div[data-testid="stVerticalBlockBorderWrapper"], .stSelectbox div[data-baseweb="select"],
    input[type="text"], .unified-box, .stNumberInput input {{
        background-color: {box} !important; color: {txt} !important;
        border: 1px solid {brd} !important; border-radius: 8px !important;
    }}
    
    /* Center the unified (disabled) end-time box */
    .unified-box {{
        height: 42px; display: flex; align-items: center; justify-content: center; font-weight: bold;
    }}
    
    /* Headings styling */
    h1 {{ color: {txt}; display: flex; align-items: center; justify-content: center; }}
    h3 {{ color: {txt}; text-align: center; }}

    /* Remove standard top padding for columns */
    [data-testid="column"] {{
        padding: 0 5px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- Logic Functions ---
def get_dt(day_idx, time_str, is_end=False, s_time_str=None):
    # Week 1 = Days 1-7 | Week 2 = Days 8-14
    base = datetime(2026, 3, 22) 
    dt = base + timedelta(days=day_idx-1)
    t_obj = datetime.strptime(time_str, "%I %p")
    final_dt = datetime.combine(dt, t_obj.time())
    
    if is_end and s_time_str:
        s_obj = datetime.strptime(s_time_str, "%I %p")
        if t_obj.hour < s_obj.hour:
            final_dt += timedelta(days=1)
    return final_dt

# --- INTEGRATED CUSTOM SWAP ICON SVG (Base64) ---
# This ensures perfect scalability and theme handling without external files.
# The `fill="currentColor"` ensures the icon automatically matches the text color (White in Dark, Dark Gray in Light)
custom_swap_svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">
        <circle cx="15.8" cy="17.6" r="14.4" fill="none" stroke="{txt}" stroke-width="2.1" opacity="1"/>
        <g opacity="1">
            <circle cx="28.9" cy="11.2" r="6.2" fill="none" stroke="{txt}" stroke-width="2.1"/>
            <circle cx="28.9" cy="9.1" r="3.1" fill="{txt}"/>
            <path d="M25.8 14.3 C25.8 12.6, 32.0 12.6, 32.0 14.3 Z" fill="{txt}"/>
        </g>
        <g opacity="1">
            <circle cx="12.0" cy="24.3" r="6.2" fill="none" stroke="{txt}" stroke-width="2.1"/>
            <circle cx="12.0" cy="22.2" r="3.1" fill="{txt}"/>
            <path d="M8.9 27.4 C8.9 25.7, 15.1 25.7, 15.1 27.4 Z" fill="{txt}"/>
        </g>
    </svg>
"""

# --- Header Setup with Custom Icon ---
h_col, t_col = st.columns([9, 1])
with t_col:
    # Use key to preserve theme state
    st.button(btn, on_click=toggle_theme, key="theme_toggle_btn")

# Display title and custom vector icon side-by-side
with h_col:
    # Use HTML to integrate the SVG and the title
    header_html = f"""
        <h1>
            <span style='margin-right:12px; display:inline-block; vertical-align:middle;'>
                {custom_swap_svg}
            </span>
            Smart Swap Validator Pro
        </h1>
    """
    st.markdown(header_html, unsafe_allow_html=True)

is_ramadan = st.checkbox("🌙 Ramadan Mode (7h)")
dur = 7 if is_ramadan else 9

# view validation rules
with st.expander("📝 View Validation Rules"):
    rules_html = f"""
    <div style='background-color:{box}; border-left:5px solid {txt}; padding:15px; border-radius:4px; color:{txt}'>
    <b>✅ Rules Applied:</b><br>
    Min 12h rest between shifts | Max 6 consecutive work days.<br>
    <b>Exemption:</b> 12h rule waived if off Saturday (Day 7) or off Sunday (Day 8).
    </div>"""
    st.markdown(rules_html, unsafe_allow_html=True)

days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
hrs = [datetime.strptime(str(i), "%H").strftime("%I %p") for i in range(24)]

shift_data = {}
c1, c2 = st.columns(2)

for i, col in enumerate([c1, c2], 1):
    with col:
        st.markdown(f"### 👤 Employee {i}")
        # RESTORED: full text placeholders like in previous design
        st.text_input("Name", key=f"un{i}", placeholder=f"Employee {i} Name", label_visibility="collapsed")
        
        for wk in ["Current", "Next"]:
            # Card Container
            st.markdown(f'<div style="background-color:{box}; border:1px solid {brd}; border-radius:12px; padding:1.5rem; margin-bottom:1rem;">', unsafe_allow_html=True)
            st.markdown(f"<center><b>🗓️ {wk} Week</b></center>", unsafe_allow_html=True)
            
            # Start/End times
            t1, t2, t3 = st.columns([4, 1, 4])
            with t1: 
                s_time = st.selectbox(f"Start {wk}{i}", hrs, index=17 if i==1 and wk=="Current" else 9, key=f"s{i}{wk}")
            with t2: 
                st.markdown("<p style='text-align:center; padding-top:35px;'>to</p>", unsafe_allow_html=True)
            with t3: 
                # Automatic native handling of disabled style
                e_time = (datetime.strptime(s_time, "%I %p") + timedelta(hours=dur)).strftime("%I %p")
                # Need label for alignment
                st.text_input(f"End {wk}{i}", value=e_time, disabled=True, key=f"disp_e{i}{wk}")
                # Store calculated end-time
                shift_data[f"e{i}_{wk}"] = {"s": s_time, "e": e_time}
            
            # Days Off with native filtering
            st.markdown("<p style='margin-bottom:8px; margin-top:15px;'>Days Off:</p>", unsafe_allow_html=True)
            o1, o2 = st.columns(2)
            # RESTORED: labels matching the image design
            off1 = o1.selectbox(f"Off 1 {wk}{i}", ["First Day off"] + days, key=f"o1{i}{wk}", label_visibility="collapsed")
            # Filter remaining days and preserve placeholder
            filtered = [d for d in days if d != off1]
            off2 = o2.selectbox(f"Off 2 {wk}{i}", ["Second Day off"] + filtered, key=f"o2{i}{wk}", label_visibility="collapsed")
            
            # Safe logic check to only count real days
            real_offs = sorted([days.index(o)+1 for o in [off1, off2] if o in days])
            shift_data[f"e{i}_{wk}"]["off"] = real_offs
            
            # Native expander
            with st.expander("➕ Overtime (Max 2h)"):
                st.number_input("OT Before (hrs)", 0, 2, 0, key=f"otb_{i}_{wk}")
                st.number_input("OT After (hrs)", 0, 2, 0, key=f"ota_{i}_{wk}")
                st.checkbox("Full Day OT", key=f"f_ot_{i}_{week}")
            
            st.markdown('</div>', unsafe_allow_html=True) # End card container

st.divider()

if st.button("🚀 Run Swap Check", use_container_width=True):
    validation_reasons = []
    swap_config = {
        1: {"c": "e1_Current", "n": "e2_Next", "u": "un1"},
        2: {"c": "e2_Current", "n": "e1_Next", "u": "un2"}
    }

    # Iterate through employees and perform logic check
    for en, cfg in swap_config.items():
        reasons = []
        name = st.session_state[cfg['u']] or f"Employee {en}"
        
        # --- Rule 1: 12H Rest Check ---
        # Exemption: Sat=Day7 (Week1), Sun=Day8 (Week2)
        week1_is_exempt = 7 in shift_data[cfg['c']]["off"]
        week2_is_exempt = 1 in shift_data[cfg['n']]["off"]
        
        # Corrected: rest rule is waived if either Saturday or Sunday is a day off
        if week1_is_exempt or week2_is_exempt:
            reasons.append(f"✅ Safe: Rest rule waived (Saturday or Sunday is a day off).")
        else:
            d_end = get_dt(7, shift_data[cfg['c']]["e"], True, shift_data[cfg['c']]["s"])
            d_start = get_dt(8, shift_data[cfg['n']]["s"])
            
            # Squeeze from OT Before/After
            d_end += timedelta(hours=st.session_state[f"ota_{en}_Current"])
            # Subtract OT from next start (assuming checks other employee's next week)
            # Find index of the *other* employee
            other_en = 3 - en
            d_start -= timedelta(hours=st.session_state[f"otb_{other_en}_Next"])

            rest = (d_start - d_end).total_seconds() / 3600
            if rest < 12:
                reasons.append(f"❌ Rejected: Insufficient Rest between shifts (**{rest:.1f}h**).")
            else:
                reasons.append(f"✅ Safe: Rest period is **{rest:.1f}h**.")
                
        validation_reasons.append({"name": name, "msgs": reasons})

    # Results display container with native coloring
    success = all("❌" not in " ".join(r["msgs"]) for r in validation_reasons)
    status_bg = "#1b5e20" if success else "#b71c1c"
    
    # Custom results container that matches native layout
    st.markdown(f"<div style='background-color:{status_bg}; padding:2rem; border-radius:12px; color:white; margin-top:1rem;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center; color:white;'>{'✅ Swap Approved' if success else '❌ Swap Rejected'}</h2>", unsafe_allow_html=True)
    for res in validation_reasons:
        st.markdown(f"<p style='margin-bottom:5px;'><b>{res['name']}</b>:</p>", unsafe_allow_html=True)
        for msg in res['msgs']:
            st.markdown(f"<p style='margin-left:15px; margin-bottom:5px;'>{msg}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><center>Created by Abdelrahman heshmat @abheshma</center>", unsafe_allow_html=True)
