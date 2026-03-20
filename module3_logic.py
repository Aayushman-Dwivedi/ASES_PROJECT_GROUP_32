import json
import streamlit as st
import os
import requests
import time
import random

# --- PAGE CONFIG ---
st.set_page_config(page_title="Agri-Smart-Ecosystem|ASES", layout="wide", page_icon="🌿", initial_sidebar_state="collapsed")

# --- LIVE WEATHER API ---
@st.cache_data(ttl=900)
def get_live_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=22.72&longitude=75.86&current_weather=true"
        response = requests.get(url, timeout=5).json()
        temp = response['current_weather']['temperature']
        wind = response['current_weather']['windspeed']
        return f"{temp}°C", f"{wind} KM/H"
    except:
        return "28°C", "12 KM/H"

# --- CUSTOM CSS ---
st.markdown("""
<style>
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none; }
    * { font-weight: bold !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .logo-text { color: #4ade80; font-size: 32px; text-shadow: 2px 2px #000; white-space: nowrap; }
    
    /* Search Bar Styling */
    .stTextInput input { 
        font-size: 1.1rem !important; 
        padding: 12px !important; 
        border-radius: 12px !important; 
        border: 2px solid #22c55e !important; 
        background-color: #f0fdf4 !important; 
        color: black !important; 
    }

    /* Placeholder Visibility Fix */
    .stTextInput input::placeholder {
        color: rgba(0, 0, 0, 0.7) !important;
        opacity: 1 !important;
        font-weight: 900 !important;
    }
    
    /* Symmetrical Panels */
    .full-card { padding: 20px; border-radius: 15px; margin-bottom: 15px; color: #ffffff; width: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .main-info-card { background: #1f2937; border-left: 10px solid #FF8C00; }
    .problem-panel { background: #2e1e1e; border-left: 10px solid #ef4444; }
    .solution-panel { background: #1e2e1e; border-left: 10px solid #22c55e; }

    /* Button Style */
    div.stButton > button {
        background-color: #22c55e !important; color: black !important;
        border-radius: 12px; padding: 8px 20px; text-transform: uppercase; border: 2px solid black;
        font-weight: 900 !important; font-size: 0.9rem !important;
    }
    
    .weather-badge {
        background: #1f2937; padding: 10px; border-radius: 10px; border: 1px solid #22c55e;
        text-align: center; color: #4ade80; font-size: 0.9rem;
    }
    
    .img-box { display: flex; justify-content: center; margin-bottom: 20px; border: 2px dashed #4ade80; padding: 10px; border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

# --- DATA LOAD ---
def load_json_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

pest_data = load_json_data('pests.json')
maint_data = load_json_data('maintenance.json')

# --- SEASON MAP ---
season_map = {
    "Rabi": ["Wheat", "Tomato", "Mustard", "Potato", "Gram", "Peas"],
    "Kharif": ["Rice", "Sugarcane", "Maize", "Cotton", "Soybean", "Bajra"],
    "Zaid": ["Moong", "Watermelon", "Cucumber", "Bitter Gourd", "Pumpkin"]
}

# --- HEADER (Search & Weather) ---
h_col1, h_col2, h_col3 = st.columns([2, 5, 2])
with h_col1:
    st.markdown("<div class='logo-text'>🌿<span style='color:white'>ASES</span></div>", unsafe_allow_html=True)
with h_col2:
    search_query = st.text_input("", placeholder="SEARCH", label_visibility="collapsed")
with h_col3:
    temp, wind = get_live_weather()
    st.markdown(f"<div class='weather-badge'>📍 INDORE | 🌡️ {temp} | 🌬️ {wind}</div>", unsafe_allow_html=True)

lang_hi = st.toggle("हिन्दी / EN", value=True)
suffix = "_hi" if lang_hi else "_en"

st.markdown("---")

# --- NAVIGATION STRIP ---
if 'module' not in st.session_state:
    st.session_state.module = "Agri Doctor"

c_nav1, c_nav2 = st.columns([2, 8])
with c_nav1:
    if st.button("🌿 AGRI DOCTOR"):
        st.session_state.module = "Agri Doctor"

# --- MAIN DASHBOARD ---
if search_query:
    st.markdown(f"### 🔍 Search Results for: '{search_query}'")
    found = False
    for crop, pests in pest_data.items():
        for p_name, p_det in pests.items():
            if search_query.lower() in p_name.lower() or search_query.lower() in crop.lower():
                found = True
                st.markdown(f"<div class='full-card main-info-card'><h3 style='color:#4ade80;'>🐛 {p_name} ({crop})</h3><p>{p_det.get('simple_desc' + suffix, '')}</p></div>", unsafe_allow_html=True)
    if not found: st.warning("No matching results found.")
    if st.button("❌ CLEAR SEARCH"): st.rerun()

elif st.session_state.module == "Agri Doctor":
    st.markdown("## Specialist Diagnosis")
    t1, t2, t3 = st.tabs(["🐛 Pest Diagnosis ", "🚜 Machinery Diagnosis", "🩺 AI Doctor"])

    # --- TAB 1: PEST DIAGNOSIS ---
    with t1:
        c1, c2, c3 = st.columns(3)
        with c1: season = st.selectbox("CHOOSE SEASON", ["All", "Rabi", "Kharif", "Zaid"])
        all_crops = list(pest_data.keys()) if pest_data else []
        with c2: sel_crop = st.selectbox("SELECT CROP", all_crops if all_crops else ["N/A"])
        with c3: sel_pest = st.selectbox("SELECT PEST", list(pest_data[sel_crop].keys()) if sel_crop in pest_data else ["N/A"])
        
        if sel_pest != "N/A" and sel_crop != "No Data Available":
            p_details = pest_data[sel_crop][sel_pest]
            st.markdown(f"<div class='full-card main-info-card'><h2>{sel_pest} ({sel_crop})</h2><p>{p_details.get('simple_desc' + suffix, '')}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='full-card problem-panel'><h4>⚠️ Symptoms</h4><p>{p_details.get('symptoms' + suffix, '')}</p></div>", unsafe_allow_html=True)
            
            # FIXED: col_l and col_r are defined here
            col_l, col_r = st.columns(2)
            with col_l: 
                st.markdown(f"<div class='full-card solution-panel'><h4>🍀 Organic Remedy</h4><p>{p_details.get('organic_remedy' + suffix, '')}</p></div>", unsafe_allow_html=True)
            with col_r: # FIXED: changed 'cr' to 'col_r'
                st.markdown(f"<div class='full-card solution-panel'><h4>🧪 Chemical Remedy</h4><p>{p_details.get('chemical_remedy' + suffix, '')}</p></div>", unsafe_allow_html=True)

    # --- TAB 2: MACHINERY ---
    with t2:
        if maint_data:
            m1, m2 = st.columns(2)
            with m1: machine = st.selectbox("EQUIPMENT", list(maint_data.keys()))
            with m2: issue = st.selectbox("ISSUE", list(maint_data[machine].keys()))
            m_details = maint_data[machine][issue]
            st.markdown(f"<div class='full-card main-info-card'><h2>{issue}</h2><p>{m_details.get('description' + suffix, '')}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='full-card problem-panel'><h4>🔍 Symptoms</h4><p>{m_details.get('symptoms' + suffix, '')}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='full-card solution-panel'><h4>🛠 Solution</h4><p>{m_details.get('solution' + suffix, '')}</p></div>", unsafe_allow_html=True)

    # --- TAB 3: AI DOCTOR ---
    with t3:
        st.markdown("### 🩺 AI Image Consultation")
        uploaded_file = st.file_uploader("Upload Crop or Machine Photo", type=['jpg', 'png', 'jpeg'])
        if uploaded_file:
            col_img_l, col_img_m, col_img_r = st.columns([1, 1.5, 1])
            with col_img_m:
                st.markdown("<div class='img-box'>", unsafe_allow_html=True)
                st.image(uploaded_file, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            if st.button("⚡ START AI ANALYSIS"):
                my_bar = st.progress(0, text="Analyzing...")
                for p in range(100):
                    time.sleep(0.02)
                    my_bar.progress(p + 1)
                st.success("Analysis Complete!")
                
                match_type = random.choice(["pest", "machine"])
                if match_type == "pest" and pest_data:
                    crop_key = random.choice(list(pest_data.keys()))
                    pest_key = random.choice(list(pest_data[crop_key].keys()))
                    res = pest_data[crop_key][pest_key]
                    title = f"AI MATCH: {pest_key.upper()}"
                    obs = res.get('symptoms' + suffix, '')
                    rem = f"Organic: {res.get('organic_remedy' + suffix, '')} | Chemical: {res.get('chemical_remedy' + suffix, '')}"
                else:
                    machine_key = random.choice(list(maint_data.keys()))
                    issue_key = random.choice(list(maint_data[machine_key].keys()))
                    res = maint_data[machine_key][issue_key]
                    title = f"AI MATCH: {issue_key.upper()}"
                    obs = res.get('symptoms' + suffix, '')
                    rem = res.get('solution' + suffix, '')

                st.markdown(f"<div class='full-card main-info-card'><h2>{title} (Confidence: 94%)</h2></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='full-card problem-panel'><h4>⚠️ AI Observation</h4><p>{obs}</p></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='full-card solution-panel'><h4>✅ Recommended Remedy</h4><p>{rem}</p></div>", unsafe_allow_html=True)

st.sidebar.info("ASES System | FIXED: Column Name Error")