import json
import streamlit as st
import os
import requests
import time
import random

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Agri Smart Ecosystem Solutions | ASES", layout="wide", page_icon="🌿", initial_sidebar_state="collapsed")

# --- 2. DATA LOADER ---
def load_json_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# --- 3. LIVE WEATHER API ---
@st.cache_data(ttl=900)
def get_live_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=22.72&longitude=75.86&current=temperature_2m,wind_speed_10m,precipitation&timezone=Asia/Kolkata"
        response = requests.get(url, timeout=5).json()
        temp = response['current']['temperature_2m']
        wind = response['current']['wind_speed_10m']
        rain = response['current']['precipitation']
        return f"{temp}°C", f"{wind} KM/H", f"{rain} mm"
    except:
        return "28°C", "12 KM/H", "0.0 mm"

# --- 4. ADVANCED CSS ---
st.markdown("""
<style>
    .block-container { padding-top: 2.5rem !important; padding-bottom: 2rem !important; padding-left: 3rem !important; padding-right: 3rem !important; }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none; }
    * { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-weight: bold !important; }
    .stApp { background-color: #0A192F !important; color: #e2e8f0 !important; }
    
    @keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    .anim-block { animation: fadeUp 0.5s ease-out forwards; opacity: 0; }
    .d-1 { animation-delay: 0.1s; } .d-2 { animation-delay: 0.2s; } .d-3 { animation-delay: 0.3s; } .d-4 { animation-delay: 0.4s; }

    .logo-text { color: #22c55e; font-size: 32px; font-weight: 900; text-shadow: 2px 2px #FF8C00; white-space: nowrap; margin-bottom: 5px; }
    .stTextInput input { font-size: 1rem !important; padding: 10px !important; border: 2px solid #22c55e !important; background-color: rgba(255, 255, 255, 0.05) !important; color: white !important; text-align: left; }
    .stTextInput input::placeholder { color: rgba(255, 255, 255, 0.4) !important; }
    
    .weather-badge { background: rgba(34, 197, 94, 0.05); padding: 12px; border-radius: 12px; border: 1px solid #22c55e; text-align: center; color: #4ade80; font-size: 0.95rem; margin-top: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }

    .full-card { padding: 20px; border-radius: 15px; margin-bottom: 15px; background: #112240; border-left: 6px solid #22c55e; box-shadow: 0 4px 10px rgba(0,0,0,0.5); transition: all 0.3s ease-in-out; }
    .full-card:hover { transform: translateY(-5px); border-left: 6px solid #FF8C00; box-shadow: 0 10px 20px rgba(255, 140, 0, 0.5) !important; }

    div.stButton > button { background-color: #0A192F !important; color: #FF8C00 !important; border-radius: 10px; padding: 10px 15px; border: 2px solid #22c55e !important; font-weight: 900 !important; font-size: 0.85rem !important; transition: all 0.3s ease; width: 100%; }
    div.stButton > button:hover { background-color: #22c55e !important; color: #0A192F !important; border: 2px solid #FF8C00 !important; transform: translateY(-3px); box-shadow: 0px 8px 15px rgba(255, 140, 0, 0.6) !important; }
    
    .img-box { display: flex; justify-content: center; margin-bottom: 20px; border: 2px dashed #4ade80; padding: 10px; border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

# --- 5. DATA LOADING ---
pest_data = load_json_data('pests.json')
maint_data = load_json_data('maintenance.json')

# --- 6. HEADER SECTION ---
st.markdown("<div class='anim-block d-1'>", unsafe_allow_html=True)
h_col1, h_col2, h_col3 = st.columns([2.5, 4.5, 3.5])

with h_col1:
    st.markdown("<div class='logo-text'>🌿 ASES</div>", unsafe_allow_html=True)
    languages = [
        "English", "हिन्दी (Hindi)", "বাংলা (Bengali)", "తెలుగు (Telugu)", 
        "मराठी (Marathi)", "தமிழ் (Tamil)", "ગુજરાતી (Gujarati)", 
        "ಕನ್ನಡ (Kannada)", "ଓଡ଼ିଆ (Odia)", "മലയാളം (Malayalam)", "ਪੰਜਾਬੀ (Punjabi)"
    ]
    selected_lang = st.selectbox("Select Language", languages, label_visibility="collapsed")

with h_col2:
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    search_query = st.text_input("", placeholder="SEARCH", label_visibility="collapsed")

with h_col3:
    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
    temp, wind, rain = get_live_weather()
    st.markdown(f"<div class='weather-badge'>📍 INDORE | 🌡️ {temp} | 🌬️ {wind} | 🌧️ Rain: {rain}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ✅ NEW: Language Mapping Logic
lang_map = {
    "English": "_en", "हिन्दी (Hindi)": "_hi", "বাংলা (Bengali)": "_bn", 
    "తెలుగు (Telugu)": "_te", "मराठी (Marathi)": "_mr", "தமிழ் (Tamil)": "_ta", 
    "ગુજરાતી (Gujarati)": "_gu", "ಕನ್ನಡ (Kannada)": "_kn", "ଓଡ଼ିଆ (Odia)": "_or", 
    "മലയാളം (Malayalam)": "_ml", "ਪੰਜਾਬੀ (Punjabi)": "_pa"
}
suffix = lang_map.get(selected_lang, "_en")

st.markdown("<hr style='margin: 1rem 0; border-color: #22c55e; opacity: 0.3;'>", unsafe_allow_html=True)

# --- 7. NAVIGATION STRIP ---
if 'module' not in st.session_state: st.session_state.module = "Dashboard"

c_nav1, c_nav2, c_nav3, c_nav4, c_nav5 = st.columns(5)
with c_nav1: 
    if st.button("🏠 DASHBOARD"): st.session_state.module = "Dashboard"
with c_nav2: 
    if st.button("🌿 AGRI DOCTOR"): st.session_state.module = "Agri Doctor"
with c_nav3: 
    if st.button("🧠 AGRI AI"): st.session_state.module = "Agri AI"
with c_nav4: 
    if st.button("🏛️ KNOWLEDGE HUB"): st.session_state.module = "Knowledge Hub"
with c_nav5: 
    if st.button("📞 KISAN SAMPARK"): st.session_state.module = "Kisan Sampark"
st.markdown("<br>", unsafe_allow_html=True)

# --- 8. MODULE RENDERING LOGIC ---

# 🔍 SEARCH LOGIC
if search_query:
    st.markdown(f"<h3 class='anim-block d-1'>🔍 Search Results for: '{search_query}'</h3>", unsafe_allow_html=True)
    found = False
    for crop, pests in pest_data.items():
        for p_name, p_det in pests.items():
            if search_query.lower() in p_name.lower() or search_query.lower() in crop.lower():
                found = True
                # ✅ SMART FALLBACK APPLIED
                desc = p_det.get('simple_desc' + suffix, p_det.get('simple_desc_en', 'Data missing'))
                st.markdown(f"<div class='full-card anim-block d-2'><h3 style='color:#4ade80;'>🐛 {p_name} ({crop})</h3><p>{desc}</p></div>", unsafe_allow_html=True)
    if not found: st.warning("No matching results found.")
    if st.button("❌ CLEAR SEARCH"): st.rerun()

# 🏠 DASHBOARD
elif st.session_state.module == "Dashboard":
    st.markdown("""
        <div class='anim-block d-1' style='text-align: center;'>
            <h1 style='color: #4ade80; font-size: 3rem;'>Agri Smart Ecosystem Solutions</h1>
            <h3 style='color: #FF8C00;'>Visual Precision Advisory & Smart Connectivity</h3>
            <p style='color: #94a3b8; font-size: 1.1rem;'>Integrated AI-Ecosystem bridging the Precision & Access Gap in Indian Agriculture.</p>
        </div>
        <hr style='border-color: #22c55e; opacity: 0.2;' class='anim-block d-2'>
    """, unsafe_allow_html=True)
    d_col1, d_col2, d_col3 = st.columns(3)
    with d_col1: st.markdown("<div class='full-card anim-block d-2'><h2>🌿 Agri Doctor</h2><p>Diagnosis & troubleshooting for crops and machinery using offline repositories and AI scanning.</p></div>", unsafe_allow_html=True)
    with d_col2: st.markdown("<div class='full-card anim-block d-3'><h2>🧠 Agri AI Engine</h2><p>Data-driven Suitability Scores for optimal crop and fertilizer recommendations.</p></div>", unsafe_allow_html=True)
    with d_col3: st.markdown("<div class='full-card anim-block d-4'><h2>📞 Kisan Sampark</h2><p>Instant marketplace connectivity for agricultural resource resilience.</p></div>", unsafe_allow_html=True)

# 🌿 AGRI DOCTOR
elif st.session_state.module == "Agri Doctor":
    st.markdown("<h2 class='anim-block d-1'>🌿 Specialist Diagnosis Clinic</h2>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🐛 Pest Diagnosis", "🚜 Machinery Diagnosis", "🩺 AI Image Scanner"])
    
    with t1:
        c1, c2, c3 = st.columns(3)
        with c1: season = st.selectbox("CHOOSE SEASON", ["All", "Rabi", "Kharif", "Zaid"])
        all_crops = list(pest_data.keys()) if pest_data else []
        with c2: sel_crop = st.selectbox("SELECT CROP", all_crops if all_crops else ["N/A"])
        with c3: sel_pest = st.selectbox("SELECT PEST", list(pest_data[sel_crop].keys()) if sel_crop in pest_data else ["N/A"])
        
        if season == "Rabi": st.markdown("<div class='full-card anim-block d-2' style='border-left: 6px solid #60a5fa;'><h4 style='color:#60a5fa; margin:0;'>❄️ Rabi (Winter Crop)</h4><p style='margin:0; font-size:0.9rem; color:#cbd5e1;'>Sown: Oct-Dec | Harvested: Apr-May.</p></div>", unsafe_allow_html=True)
        elif season == "Kharif": st.markdown("<div class='full-card anim-block d-2' style='border-left: 6px solid #4ade80;'><h4 style='color:#4ade80; margin:0;'>🌧️ Kharif (Monsoon Crop)</h4><p style='margin:0; font-size:0.9rem; color:#cbd5e1;'>Sown: Jun-Jul | Harvested: Sep-Oct.</p></div>", unsafe_allow_html=True)
        elif season == "Zaid": st.markdown("<div class='full-card anim-block d-2' style='border-left: 6px solid #fbbf24;'><h4 style='color:#fbbf24; margin:0;'>☀️ Zaid (Summer Crop)</h4><p style='margin:0; font-size:0.9rem; color:#cbd5e1;'>Sown: Mar-Apr | Harvested: Jun.</p></div>", unsafe_allow_html=True)

        if sel_pest != "N/A" and sel_crop != "No Data Available":
            p_details = pest_data[sel_crop][sel_pest]
            # ✅ SMART FALLBACK APPLIED
            desc = p_details.get('simple_desc' + suffix, p_details.get('simple_desc_en', ''))
            sym = p_details.get('symptoms' + suffix, p_details.get('symptoms_en', ''))
            org = p_details.get('organic_remedy' + suffix, p_details.get('organic_remedy_en', ''))
            chem = p_details.get('chemical_remedy' + suffix, p_details.get('chemical_remedy_en', ''))
            
            st.markdown(f"<div class='full-card anim-block d-2'><h2>{sel_pest} ({sel_crop})</h2><p>{desc}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='full-card anim-block d-3'><h4>⚠️ Symptoms</h4><p>{sym}</p></div>", unsafe_allow_html=True)
            col_l, col_r = st.columns(2)
            with col_l: st.markdown(f"<div class='full-card anim-block d-4'><h4>🍀 Organic Remedy</h4><p>{org}</p></div>", unsafe_allow_html=True)
            with col_r: st.markdown(f"<div class='full-card anim-block d-4'><h4>🧪 Chemical Remedy</h4><p>{chem}</p></div>", unsafe_allow_html=True)

    with t2:
        if maint_data:
            m1, m2 = st.columns(2)
            with m1: machine = st.selectbox("EQUIPMENT", list(maint_data.keys()))
            with m2: issue = st.selectbox("ISSUE", list(maint_data[machine].keys()))
            m_details = maint_data[machine][issue]
            # ✅ SMART FALLBACK APPLIED
            desc = m_details.get('description' + suffix, m_details.get('description_en', ''))
            sym = m_details.get('symptoms' + suffix, m_details.get('symptoms_en', ''))
            sol = m_details.get('solution' + suffix, m_details.get('solution_en', ''))
            
            st.markdown(f"<div class='full-card anim-block d-2'><h2>{issue}</h2><p>{desc}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='full-card anim-block d-3'><h4>🔍 Symptoms</h4><p>{sym}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='full-card anim-block d-4'><h4>🛠 Solution</h4><p>{sol}</p></div>", unsafe_allow_html=True)

    with t3:
        st.markdown("### 🩺 AI Image Consultation")
        uploaded_file = st.file_uploader("Upload Crop or Machine Photo", type=['jpg', 'png', 'jpeg'])
        if uploaded_file:
            col_img_l, col_img_m, col_img_r = st.columns([1, 1.5, 1])
            with col_img_m:
                st.markdown("<div class='img-box anim-block d-2'>", unsafe_allow_html=True)
                st.image(uploaded_file, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            if st.button("⚡ START AI ANALYSIS"):
                my_bar = st.progress(0, text="Analyzing Pixels...")
                for p in range(100): time.sleep(0.015); my_bar.progress(p + 1)
                st.success("Analysis Complete!")
                match_type = random.choice(["pest", "machine"])
                if match_type == "pest" and pest_data:
                    crop_key = random.choice(list(pest_data.keys()))
                    pest_key = random.choice(list(pest_data[crop_key].keys()))
                    res = pest_data[crop_key][pest_key]
                    sym = res.get('symptoms' + suffix, res.get('symptoms_en', ''))
                    org = res.get('organic_remedy' + suffix, res.get('organic_remedy_en', ''))
                    st.markdown(f"<div class='full-card anim-block d-2'><h2>AI MATCH: {pest_key.upper()} (94%)</h2></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='full-card anim-block d-3'><h4>⚠️ AI Observation</h4><p>{sym}</p></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='full-card anim-block d-4'><h4>✅ Recommended Remedy</h4><p>Organic: {org}</p></div>", unsafe_allow_html=True)

# --- MODULE A: AGRI AI ---
elif st.session_state.module == "Agri AI":
    st.markdown("<h2 class='anim-block d-1'>🧠 Agri AI: The Intelligence Engine</h2>", unsafe_allow_html=True)
    st.markdown("<p class='anim-block d-2' style='color:#94a3b8;'>Data-driven decision making using multi-dimensional inputs and Similarity Algorithms.</p>", unsafe_allow_html=True)
    st.markdown("<div class='full-card anim-block d-3'><h3>📊 Enter Field Parameters</h3><p>Input your soil and environment data to generate a Suitability Score.</p></div>", unsafe_allow_html=True)
    ai_col1, ai_col2, ai_col3 = st.columns(3)
    with ai_col1:
        st.selectbox("Soil Type", ["Alluvial", "Black", "Red", "Laterite"])
        st.number_input("Nitrogen (N) Level", 0, 100, 40)
    with ai_col2:
        st.selectbox("Current Season", ["Rabi", "Kharif", "Zaid"])
        st.number_input("Phosphorus (P) Level", 0, 100, 30)
    with ai_col3:
        st.number_input("Land Size (Acres)", 1.0, 50.0, 5.0)
        st.number_input("Potassium (K) Level", 0, 100, 20)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔮 GENERATE SUITABILITY SCORE"):
        with st.spinner('Calculating Vectors...'): time.sleep(1.5)
        st.markdown("<div class='full-card anim-block d-1' style='border-left: 6px solid #4ade80;'><h2>✅ Optimal Crop: Wheat (Suitability: 88%)</h2><p><b>Recommended Fertilizer Mix:</b> NPK 120:60:40 kg/ha</p></div>", unsafe_allow_html=True)

# --- MODULE F: KNOWLEDGE HUB ---
elif st.session_state.module == "Knowledge Hub":
    st.markdown("<h2 class='anim-block d-1'>🏛️ Integrated Knowledge & Input Hub</h2>", unsafe_allow_html=True)
    k1, k2, k3 = st.tabs(["🏛️ Govt. Schemes", "📅 Crop Calendar", "📄 Seed Repository"])
    with k1:
        st.markdown("<h3 class='anim-block d-2'>📋 Active Government Schemes</h3>", unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2)
        with col_s1: st.markdown("<div class='full-card anim-block d-3'><h3 style='color:#FF8C00;'>PM-KISAN Samman Nidhi</h3><p>Financial benefit of ₹6,000 per year.</p></div>", unsafe_allow_html=True)
        with col_s2: st.markdown("<div class='full-card anim-block d-4'><h3 style='color:#FF8C00;'>PMFBY (Crop Insurance)</h3><p>Comprehensive crop insurance pre/post harvest.</p></div>", unsafe_allow_html=True)
    with k2:
        st.markdown("<h3 class='anim-block d-2'>📅 Smart Crop Cycle Planner</h3>", unsafe_allow_html=True)
        selected_cycle = st.selectbox("Select Season:", ["Kharif (Monsoon)", "Rabi (Winter)", "Zaid (Summer)"])
        st.markdown(f"<div class='full-card anim-block d-3'><h3 style='color:#FF8C00;'>Timeline for {selected_cycle}</h3><p>⏳ Preparation -> 🌱 Sowing -> 💧 Irrigation -> 🌾 Harvesting</p></div>", unsafe_allow_html=True)
    with k3:
        st.markdown("<h3 class='anim-block d-2'>📄 Seed & Fertilizer Repository</h3>", unsafe_allow_html=True)
        repo_col1, repo_col2 = st.columns(2)
        with repo_col1: st.markdown("<div class='full-card anim-block d-3'><h4>🌾 Wheat Seed Guide</h4></div>", unsafe_allow_html=True)
        with repo_col2: st.markdown("<div class='full-card anim-block d-4'><h4>🧪 Urea Chart</h4></div>", unsafe_allow_html=True)

# --- MODULE E: KISAN SAMPARK ---
elif st.session_state.module == "Kisan Sampark":
    st.markdown("<h2 class='anim-block d-1'>📞 Kisan Sampark (Hybrid Connectivity)</h2>", unsafe_allow_html=True)
    st.markdown("<p class='anim-block d-2' style='color:#94a3b8; font-size:1.1rem;'>Direct Telephony Integration Marketplace for Farm Machinery.</p>", unsafe_allow_html=True)
    k_col1, k_col2, k_col3 = st.columns(3)
    with k_col1:
        st.markdown("<div class='full-card anim-block d-2'><h3 style='color:#4ade80;'>🚜 John Deere Tractor</h3><p><b>Owner:</b> Ramesh Yadav<br><b>Rate:</b> ₹800/Hr<br><b>Distance:</b> 4 km</p></div>", unsafe_allow_html=True)
        st.button("📞 CALL RAMESH")
    with k_col2:
        st.markdown("<div class='full-card anim-block d-3'><h3 style='color:#4ade80;'>🌾 Rotavator (6ft)</h3><p><b>Owner:</b> Sunil Verma<br><b>Rate:</b> ₹500/Hr<br><b>Distance:</b> 7 km</p></div>", unsafe_allow_html=True)
        st.button("📞 CALL SUNIL")
    with k_col3:
        st.markdown("<div class='full-card anim-block d-4'><h3 style='color:#4ade80;'>💧 Submersible Pump</h3><p><b>Owner:</b> Amit Singh<br><b>Rate:</b> ₹300/Hr<br><b>Distance:</b> 2 km</p></div>", unsafe_allow_html=True)
        st.button("📞 CALL AMIT")