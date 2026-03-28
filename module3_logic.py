import json
import streamlit as st
import os
import requests
import time
import random
import sqlite3
import pandas as pd
import plotly.express as px
from deep_translator import GoogleTranslator
from fpdf import FPDF
import io

# --- 1. PAGE CONFIG & SESSION STATE ---
st.set_page_config(page_title="ASES | Agri-Smart Ecosystem", layout="wide", page_icon="🌿", initial_sidebar_state="collapsed")

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'user_email' not in st.session_state: st.session_state.user_email = ""
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = None
if 'module' not in st.session_state: st.session_state.module = "Dashboard"
if "search_query_val" not in st.session_state: st.session_state.search_query_val = ""

# --- 2. DYNAMIC TRANSLATION ENGINE ---
@st.cache_data(show_spinner=False, ttl=3600)
def translate_text(text, target_lang):
    if target_lang == 'en' or not text: return text
    try: return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except: return text

# --- 3. DATABASE INIT (Users & Ledger) ---
def init_db():
    conn = sqlite3.connect('agri_khata.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ledger 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_key TEXT,
                  date TEXT, type TEXT, item TEXT, qty TEXT, total REAL, season TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT UNIQUE, 
                  password TEXT, address TEXT, location TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 4. DATA LOADER & WEATHER API ---
def load_json_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
    return {}

pest_data = load_json_data('pests.json')
maint_data = load_json_data('maintenance.json')

@st.cache_data(ttl=900)
def get_live_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=22.72&longitude=75.86&current=temperature_2m,wind_speed_10m,precipitation&timezone=Asia/Kolkata"
        response = requests.get(url, timeout=5).json()
        temp = response['current']['temperature_2m']
        wind = response['current']['wind_speed_10m']
        rain = response['current']['precipitation']
        return f"{temp}°C", f"{wind} KM/H", f"{rain} mm"
    except: return "28°C", "12 KM/H", "0.0 mm"

# --- 5. ADVANCED CSS & STYLING ---
st.markdown("""
<style>
    .block-container { padding-top: 2.5rem !important; padding-bottom: 2rem !important; padding-left: 3rem !important; padding-right: 3rem !important; }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none; }
    * { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-weight: bold !important; }
    .stApp { background-color: #0A192F !important; color: #e2e8f0 !important; }
    
    @keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    .anim-block { animation: fadeUp 0.6s ease-out forwards; opacity: 0; }
    .d-1 { animation-delay: 0.1s; } .d-2 { animation-delay: 0.2s; } .d-3 { animation-delay: 0.3s; } .d-4 { animation-delay: 0.4s; }

    .logo-text { color: #22c55e; font-size: 32px; font-weight: 900; text-shadow: 2px 2px #FF8C00; white-space: nowrap; margin-bottom: 5px; }
    .stTextInput input { font-size: 1rem !important; padding: 10px !important; border: 2px solid #22c55e !important; background-color: rgba(255, 255, 255, 0.05) !important; color: white !important; }
    
    .weather-badge { background: rgba(34, 197, 94, 0.05); padding: 12px; border-radius: 12px; border: 1px solid #22c55e; text-align: center; color: #4ade80; font-size: 0.95rem; margin-bottom: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .profile-badge { background: rgba(255, 140, 0, 0.1); padding: 8px; border-radius: 10px; border: 1px solid #FF8C00; text-align: center; color: #FF8C00; font-size: 0.85rem; box-shadow: 0 4px 6px rgba(255, 140, 0, 0.3); }
    
    /* PROPOSAL UPGRADE: Smart Context Box CSS */
    .context-box { background: rgba(56, 189, 248, 0.1); border-left: 5px solid #38bdf8; padding: 15px; border-radius: 8px; margin-bottom: 20px; color: #e0f2fe; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }

    .full-card { padding: 20px; border-radius: 15px; margin-bottom: 15px; background: #112240; border-left: 6px solid #22c55e; box-shadow: 0 4px 10px rgba(0,0,0,0.5); transition: all 0.3s ease-in-out; }
    .full-card:hover { transform: translateY(-5px); border-left: 6px solid #FF8C00; box-shadow: 0 10px 20px rgba(255, 140, 0, 0.5) !important; }

    .thin-line { border: 0; height: 1px; background-image: linear-gradient(to right, rgba(34, 197, 94, 0), rgba(34, 197, 94, 0.75), rgba(34, 197, 94, 0)); margin: 10px 0; }
    .organic-box { background: rgba(34, 197, 94, 0.1); border: 1px solid #4ade80; padding: 15px; border-radius: 10px; color: #e2e8f0; height: 100%; }
    .inorganic-box { background: rgba(255, 140, 0, 0.1); border: 1px solid #FF8C00; padding: 15px; border-radius: 10px; color: #e2e8f0; height: 100%; }
    
    div.stButton > button { border-radius: 10px; padding: 8px 15px; font-weight: 900 !important; font-size: 0.85rem !important; transition: all 0.3s ease; width: 100%; }
    div.stButton > button[kind="secondary"] { background-color: #0A192F !important; color: #FF8C00 !important; border: 2px solid #22c55e !important; }
    div.stButton > button[kind="secondary"]:hover { background-color: #22c55e !important; color: #0A192F !important; border: 2px solid #FF8C00 !important; transform: translateY(-3px); }
    div.stButton > button[kind="primary"] { background-color: #22c55e !important; color: #0A192F !important; border: 2px solid #FF8C00 !important; box-shadow: 0px 0px 18px rgba(34, 197, 94, 0.6) !important; transform: scale(1.03); }
    
    .img-box { display: flex; justify-content: center; margin-bottom: 20px; border: 2px dashed #4ade80; padding: 10px; border-radius: 15px; }
    
    /* PROPOSAL UPGRADE: Direct Telephony Button */
    .call-btn { width:100%; display:block; text-align:center; padding:10px; background-color:#22c55e; color:#0A192F !important; border-radius:10px; font-weight:bold; text-decoration:none; transition: 0.3s; }
    .call-btn:hover { background-color:#FF8C00; color:#fff !important; }
</style>
""", unsafe_allow_html=True)

# Language Mapper
lang_codes = {"English": "en", "हिन्दी (Hindi)": "hi", "বাংলা (Bengali)": "bn", "मराठी (Marathi)": "mr", "ਪੰਜਾਬੀ (Punjabi)": "pa", "తెలుగు (Telugu)": "te"}
def t(text): return translate_text(text, target_lang)

# --- PROPOSAL UPGRADE: SMART CONTEXT GUIDE (MODULE B) ---
def display_smart_context(module):
    contexts = {
        "Dashboard": "📌 **Smart Guide:** Welcome to ASES! Navigate through the top menu. No typing required—just click and explore.",
        "Agri Doctor": "📌 **Smart Guide:** Select Pest or Machine issues below, or upload a photo in the AI tab for instant visual diagnosis.",
        "Agri AI": "📌 **Smart Guide:** Enter your field parameters (Soil, Season, Land Size). The AI uses Vector Similarity to recommend the best crop.",
        "Knowledge Hub": "📌 **Smart Guide:** Access Govt Schemes, Crop Comparisons, Seed PDFs, and the new Dynamic Crop Calendar.",
        "Kisan Sampark": "📌 **Smart Guide:** Need a machine? Select a task and click 'Call Now' to speak directly with the owner (Direct Telephony).",
        "Price Trends": "📌 **Smart Guide:** Check real-time Mandi prices to maximize your market profit.",
        "Agri Ledger": "📌 **Smart Guide:** Track your daily farming income and expenses securely in your private digital Khata."
    }
    st.markdown(f"<div class='context-box anim-block d-1'>{t(contexts.get(module, ''))}</div>", unsafe_allow_html=True)

# --- 6. HEADER SECTION & AUTH BUTTONS ---
st.markdown("<div class='anim-block d-1'>", unsafe_allow_html=True)
h_col1, h_col2, h_col3 = st.columns([2.5, 4.5, 3.5])

with h_col1:
    st.markdown("<div class='logo-text'>🌿 ASES</div>", unsafe_allow_html=True)
    selected_lang = st.selectbox("Select Language", list(lang_codes.keys()), label_visibility="collapsed")
    target_lang = lang_codes.get(selected_lang, "en")

with h_col2:
    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    search_query = st.text_input("", placeholder=t("SEARCH CROP OR PEST"), key="search_query_val", label_visibility="collapsed")

with h_col3:
    temp, wind, rain = get_live_weather()
    st.markdown(f"<div class='weather-badge'>📍 {t('INDORE')} | 🌡️ {temp} | 🌬️ {wind} | 🌧️ {t('Rain')}: {rain}</div>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        auth_c1, auth_c2 = st.columns(2)
        with auth_c1:
            if st.button(t("Sign Up"), type="secondary"): st.session_state.auth_mode = "register"; st.rerun()
        with auth_c2:
            if st.button(t("Log In"), type="primary"): st.session_state.auth_mode = "login"; st.rerun()
    else:
        st.markdown(f"<div class='profile-badge'>👤 <b>{st.session_state.user_name}</b> ({st.session_state.user_email})</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<hr style='margin: 1rem 0; border-color: #22c55e; opacity: 0.3;'>", unsafe_allow_html=True)

# --- 7. AUTHENTICATION PAGES ---
if st.session_state.auth_mode == "register":
    st.markdown(f"<h2 style='text-align:center; color:#4ade80;'>📝 {t('Create a New Account')}</h2>", unsafe_allow_html=True)
    with st.form("reg_form"):
        r_name = st.text_input(t("Full Name"))
        r_email = st.text_input(t("Email ID"))
        r_pass = st.text_input(t("Create Password"), type="password")
        r_addr = st.text_area(t("Full Address"))
        r_loc = st.text_input(t("Location (City/District)"))
        submitted = st.form_submit_button(f"🚀 {t('Sign Up Now')}")
        if submitted and r_name and r_email and r_pass:
            try:
                conn = sqlite3.connect('agri_khata.db')
                conn.execute("INSERT INTO users (name, email, password, address, location) VALUES (?,?,?,?,?)", (r_name, r_email, r_pass, r_addr, r_loc))
                conn.commit(); conn.close()
                st.success(t("Account Created Successfully! Please Log In."))
                time.sleep(1.5); st.session_state.auth_mode = "login"; st.rerun()
            except sqlite3.IntegrityError:
                st.error(t("Email ID already exists!"))
    if st.button(f"⬅️ {t('Go Back')}", type="secondary"): st.session_state.auth_mode = None; st.rerun()

elif st.session_state.auth_mode == "login":
    st.markdown(f"<h2 style='text-align:center; color:#4ade80;'>🔐 {t('Log In to ASES')}</h2>", unsafe_allow_html=True)
    col_log1, col_log2, col_log3 = st.columns([1,2,1])
    with col_log2:
        with st.form("login_form"):
            l_email = st.text_input(t("Email ID"))
            l_pass = st.text_input(t("Password"), type="password")
            if st.form_submit_button(f"🔑 {t('Log In')}"):
                conn = sqlite3.connect('agri_khata.db')
                c = conn.cursor()
                c.execute("SELECT name, email FROM users WHERE email=? AND password=?", (l_email, l_pass))
                user = c.fetchone()
                conn.close()
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_name = user[0]
                    st.session_state.user_email = user[1]
                    st.session_state.auth_mode = None
                    st.success(t("Login Successful!")); time.sleep(1); st.rerun()
                else: st.error(t("Invalid Email or Password!"))
    if st.button(f"⬅️ {t('Go Back')}", type="secondary"): st.session_state.auth_mode = None; st.rerun()

# --- 8. MAIN APP LOGIC ---
elif st.session_state.auth_mode is None:
    # NAVIGATION STRIP
    c_nav1, c_nav2, c_nav3, c_nav4, c_nav5, c_nav6, c_nav7 = st.columns(7)
    with c_nav1: 
        if st.button("🏠 DASHBOARD", type="primary" if st.session_state.module == "Dashboard" else "secondary"): st.session_state.module = "Dashboard"; st.rerun()
    with c_nav2: 
        if st.button("🌿 AGRI DOCTOR", type="primary" if st.session_state.module == "Agri Doctor" else "secondary"): st.session_state.module = "Agri Doctor"; st.rerun()
    with c_nav3: 
        if st.button("🧠 AGRI AI", type="primary" if st.session_state.module == "Agri AI" else "secondary"): st.session_state.module = "Agri AI"; st.rerun()
    with c_nav4: 
        if st.button("🏛️ KNOWLEDGE HUB", type="primary" if st.session_state.module == "Knowledge Hub" else "secondary"): st.session_state.module = "Knowledge Hub"; st.rerun()
    with c_nav5: 
        if st.button("📞 KISAN SAMPARK", type="primary" if st.session_state.module == "Kisan Sampark" else "secondary"): st.session_state.module = "Kisan Sampark"; st.rerun()
    with c_nav6: 
        if st.button("📉 PRICE TRENDS", type="primary" if st.session_state.module == "Price Trends" else "secondary"): st.session_state.module = "Price Trends"; st.rerun()
    with c_nav7: 
        if st.button("📒 AGRI LEDGER", type="primary" if st.session_state.module == "Agri Ledger" else "secondary"): st.session_state.module = "Agri Ledger"; st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Render Smart Context Guide
    display_smart_context(st.session_state.module)

    # SEARCH OVERRIDE
    def clear_search(): st.session_state.search_query_val = ""
    if st.session_state.search_query_val:
        st.markdown(f"<h3 class='anim-block d-1'>🔍 {t('Search Results for')}: '{st.session_state.search_query_val}'</h3>", unsafe_allow_html=True)
        found = False
        for crop, pests in pest_data.items():
            for p_name, p_det in pests.items():
                if st.session_state.search_query_val.lower() in p_name.lower() or st.session_state.search_query_val.lower() in crop.lower():
                    found = True
                    st.markdown(f"<div class='full-card anim-block d-2'><h3 style='color:#4ade80;'>🐛 {t(p_name)} ({t(crop)})</h3><p><b>{t('Description')}:</b> {t(p_det.get('simple_desc_en', ''))}</p><p><b>{t('Symptoms')}:</b> {t(p_det.get('symptoms_en', ''))}</p><p style='color:#FF8C00;'><b>{t('Remedy')}:</b> {t(p_det.get('organic_remedy_en', ''))}</p></div>", unsafe_allow_html=True)
        if not found: st.warning(t("No matching results found in our database."))
        st.button(f"❌ {t('CLEAR SEARCH & GO BACK')}", on_click=clear_search)

    else:
        # 🏠 DASHBOARD
        if st.session_state.module == "Dashboard":
            st.markdown(f"<div class='anim-block d-1' style='text-align: center;'><h1 style='color: #4ade80; font-size: 3rem;'>Agri Smart Ecosystem Solutions</h1><h3 style='color: #FF8C00;'>{t('Visual Precision Advisory & Smart Connectivity')}</h3><p style='color: #94a3b8; font-size: 1.1rem;'>{t('Integrated AI-Ecosystem bridging the Precision & Access Gap in Indian Agriculture.')}</p></div><hr style='border-color: #22c55e; opacity: 0.2;' class='anim-block d-2'>", unsafe_allow_html=True)
            d_col1, d_col2, d_col3 = st.columns(3)
            with d_col1: st.markdown(f"<div class='full-card anim-block d-2'><h2>🌿 {t('Agri Doctor')}</h2><p>{t('Visual diagnosis & troubleshooting for crops and machinery.')}</p></div>", unsafe_allow_html=True)
            with d_col2: st.markdown(f"<div class='full-card anim-block d-3'><h2>🧠 {t('Agri AI Engine')}</h2><p>{t('Vector-based Suitability Scores for precision agriculture.')}</p></div>", unsafe_allow_html=True)
            with d_col3: st.markdown(f"<div class='full-card anim-block d-4'><h2>📞 {t('Kisan Sampark')}</h2><p>{t('Direct Telephony marketplace for farm machinery access.')}</p></div>", unsafe_allow_html=True)

        # 🌿 AGRI DOCTOR 
        elif st.session_state.module == "Agri Doctor":
            if 'agri_tab' not in st.session_state: st.session_state.agri_tab = "Pest"
            t_col1, t_col2, t_col3 = st.columns(3)
            with t_col1:
                if st.button(t("🐛 Pest Diagnosis"), type="primary" if st.session_state.agri_tab == "Pest" else "secondary"): st.session_state.agri_tab = "Pest"; st.rerun()
            with t_col2:
                if st.button(t("🚜 Machinery & Infra"), type="primary" if st.session_state.agri_tab == "Machine" else "secondary"): st.session_state.agri_tab = "Machine"; st.rerun()
            with t_col3:
                if st.button(t("🩺 AI Image Scanner"), type="primary" if st.session_state.agri_tab == "AI" else "secondary"): st.session_state.agri_tab = "AI"; st.rerun()
            st.markdown("<hr style='border-color: #22c55e; opacity: 0.3;'>", unsafe_allow_html=True)
            
            if st.session_state.agri_tab == "Pest":
                crop_seasons = {"Wheat": "Rabi", "Chickpea": "Rabi", "Mustard": "Rabi", "Potato": "Rabi", "Rice": "Kharif", "Cotton": "Kharif", "Maize": "Kharif", "Groundnut": "Kharif", "Soybean": "Kharif", "Tomato": "All", "Sugarcane": "All"}
                c1, c2, c3 = st.columns(3)
                with c1: season = st.selectbox(t("1. CHOOSE SEASON"), [t("All"), t("Rabi"), t("Kharif"), t("Zaid")])
                eng_season = "All"
                for k, v in {"All": t("All"), "Rabi": t("Rabi"), "Kharif": t("Kharif"), "Zaid": t("Zaid")}.items():
                    if v == season: eng_season = k
                available_crops = [c for c in pest_data.keys() if eng_season == "All" or crop_seasons.get(c, "All") in [eng_season, "All"]]
                translated_crops = {t(c): c for c in available_crops}
                with c2: sel_crop_trans = st.selectbox(t("2. SELECT CROP"), list(translated_crops.keys()) if translated_crops else [t("N/A")])
                sel_crop = translated_crops.get(sel_crop_trans, "N/A")
                available_pests = list(pest_data[sel_crop].keys()) if sel_crop in pest_data else []
                translated_pests = {t(p): p for p in available_pests}
                with c3: sel_pest_trans = st.selectbox(t("3. SELECT PEST"), list(translated_pests.keys()) if translated_pests else [t("N/A")])
                sel_pest = translated_pests.get(sel_pest_trans, "N/A")

                if sel_pest != "N/A" and sel_crop != "N/A":
                    p_details = pest_data[sel_crop][sel_pest]
                    st.markdown(f"<div class='full-card anim-block d-2'><h3 style='color:#FF8C00; margin-bottom:0;'>📌 {t('About Pest')}: {t(sel_pest)} ({t(sel_crop)})</h3><hr class='thin-line'><p style='font-size:1.05rem;'>{t(p_details.get('simple_desc_en', ''))}</p><h3 style='color:#FF8C00; margin-bottom:0; margin-top:20px;'>⚠️ {t('Symptoms')}</h3><hr class='thin-line'><p style='font-size:1.05rem;'>{t(p_details.get('symptoms_en', ''))}</p></div>", unsafe_allow_html=True)
                    col_l, col_r = st.columns(2)
                    with col_l: st.markdown(f"<div class='organic-box anim-block d-3'><h3 style='color:#4ade80; margin-top:0;'>🍀 {t('Organic Solution')}</h3><hr class='thin-line'><p>{t(p_details.get('organic_remedy_en', ''))}</p></div>", unsafe_allow_html=True)
                    with col_r: st.markdown(f"<div class='inorganic-box anim-block d-4'><h3 style='color:#FF8C00; margin-top:0;'>🧪 {t('Inorganic/Chemical Solution')}</h3><hr class='thin-line'><p>{t(p_details.get('chemical_remedy_en', ''))}</p></div>", unsafe_allow_html=True)

            elif st.session_state.agri_tab == "Machine":
                st.markdown(f"### ⚙️ {t('Equipment Troubleshooting')}")
                if maint_data:
                    m1, m2 = st.columns(2)
                    translated_machines = {t(m): m for m in maint_data.keys()}
                    with m1: sel_machine_trans = st.selectbox(t("1. SELECT EQUIPMENT"), list(translated_machines.keys()))
                    machine = translated_machines.get(sel_machine_trans)
                    translated_issues = {t(i): i for i in maint_data[machine].keys()}
                    with m2: sel_issue_trans = st.selectbox(t("2. SELECT ISSUE"), list(translated_issues.keys()))
                    issue = translated_issues.get(sel_issue_trans)
                    m_details = maint_data[machine][issue]
                    st.markdown(f"<div class='full-card anim-block d-2'><h3 style='color:#FF8C00; margin-bottom:0;'>⚙️ {t('Issue')}: {t(issue)}</h3><hr class='thin-line'><p style='font-size:1.05rem;'><b>{t('Symptoms')}:</b> {t(m_details.get('symptoms_en', ''))}</p><h3 style='color:#4ade80; margin-bottom:0; margin-top:20px;'>🛠️ {t('Solution')}</h3><hr class='thin-line'><p style='font-size:1.05rem;'>{t(m_details.get('solution_en', ''))}</p></div>", unsafe_allow_html=True)
                
                st.markdown(f"<h3 style='color:#38bdf8; margin-top:30px;'>🏗️ {t('Infrastructure Resource Resilience')}</h3>", unsafe_allow_html=True)
                with st.expander(t("💧 Borewell Recharge & Maintenance Guide")):
                    st.write(t("1. Regularly flush the borewell to remove accumulated silt.\n2. Construct a proper rainwater recharge pit around the casing.\n3. Ensure electrical connections and pump voltage are checked monthly."))
                with st.expander(t("🚜 Tractor Basic Maintenance Schedule")):
                    st.write(t("1. Check engine oil and coolant levels before every heavy use.\n2. Clean the air filter weekly during dusty field operations.\n3. Grease all moving joints every 50 hours of operation."))

            elif st.session_state.agri_tab == "AI":
                st.markdown(f"### 🩺 {t('AI Image Consultation')}")
                
                # यहाँ से हमने API Key का इनपुट बॉक्स हमेशा के लिए हटा दिया है
                uploaded_file = st.file_uploader(t("Upload Crop or Machine Photo"), type=['jpg', 'png', 'jpeg'])
                
                if uploaded_file:
                    col_img_l, col_img_m, col_img_r = st.columns([1, 1.5, 1])
                    with col_img_m:
                        st.markdown("<div class='img-box anim-block d-2'>", unsafe_allow_html=True)
                        st.image(uploaded_file, use_container_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                    if st.button(t("⚡ START AI ANALYSIS"), type="primary"):
                        try:
                            import google.generativeai as genai
                            from PIL import Image
                            
                            # यह सीधे आपकी Cloud Secrets से Key ले लेगा
                            MY_API_KEY = st.secrets["GEMINI_API_KEY"]
                            genai.configure(api_key=MY_API_KEY)
                            
                            # मॉडल का बिल्कुल सही और स्टैंडर्ड नाम
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            
                            prompt = f"You are an expert agricultural AI. Analyze this image. Identify the crop disease/pest OR machinery issue. Provide the response strictly in {selected_lang} language. Format the response strictly with these exact headings: 'Diagnosis', 'Symptoms', 'Organic Remedy', 'Chemical Remedy'. Use emojis."
                            
                            with st.spinner(t("Analyzing Pixels...")): 
                                response = model.generate_content([prompt, Image.open(uploaded_file)])
                                
                            st.success(t("Analysis Complete!"))
                            st.markdown(f"<div class='full-card anim-block d-2'>{response.text}</div>", unsafe_allow_html=True)
                        except Exception as e: 
                            st.error(f"⚠️ API Error: {e}")
        # 🧠 AGRI AI 
        elif st.session_state.module == "Agri AI":
            if 'ai_mode' not in st.session_state: st.session_state.ai_mode = "Yield"
            m1, m2, m3 = st.columns(3)
            with m1: 
                if st.button(f"🌾 {t('Yield Optimizer')}", type="primary" if st.session_state.ai_mode == "Yield" else "secondary"): st.session_state.ai_mode = "Yield"; st.rerun()
            with m2: 
                if st.button(f"🦠 {t('Disease Predictor')}", type="primary" if st.session_state.ai_mode == "Disease" else "secondary"): st.session_state.ai_mode = "Disease"; st.rerun()
            with m3: 
                if st.button(f"📈 {t('Market Analyzer')}", type="primary" if st.session_state.ai_mode == "Market" else "secondary"): st.session_state.ai_mode = "Market"; st.rerun()
            st.markdown("<hr style='border-color: #22c55e; opacity: 0.3;'>", unsafe_allow_html=True)
            
            if st.session_state.ai_mode == "Yield":
                try:
                    from crop_engine_data import get_agri_dataframe, recommend_crops
                    df, le = get_agri_dataframe()
                    st.markdown(f"<div class='full-card anim-block d-3'><h3>📊 {t('Multi-Dimensional Field Parameters')}</h3></div>", unsafe_allow_html=True)
                    
                    ai_col1, ai_col2, ai_col3 = st.columns(3)
                    with ai_col1: season = st.selectbox(t("Season"), [t("Rabi"), t("Kharif"), t("Zaid")])
                    with ai_col2: soil = st.selectbox(t("Soil Type"), [t("Alluvial"), t("Black Soil"), t("Red Soil"), t("Sandy")])
                    with ai_col3: land_size = st.number_input(t("Land Size (Acres)"), min_value=1.0, value=1.0, step=0.5)
                    
                    budget_per_acre = st.select_slider(t("Investment Limit per Acre (₹)"), options=[5000, 10000, 15000, 20000, 30000, 50000])
                    total_budget = budget_per_acre * land_size

                    if st.button(t("🔮 RUN VECTOR SIMILARITY ANALYSIS"), type="primary"):
                        with st.spinner(t('Computing Suitability Score...')):
                            eng_soil = "Alluvial"
                            for k, v in {"Alluvial": t("Alluvial"), "Black Soil": t("Black Soil"), "Red Soil": t("Red Soil"), "Sandy": t("Sandy")}.items():
                                if v == soil: eng_soil = k
                            
                            recs = recommend_crops(df, le, eng_soil, budget_per_acre)
                            st.markdown(f"<div class='full-card anim-block d-1' style='border-left: 6px solid #4ade80;'><h2>✅ {t('Optimal Crop Match')}: {t(recs['Crop Name'])}</h2><p><b>{t('Estimated Total Cost for')} {land_size} {t('Acres')}:</b> ₹{recs['Cost per Acre'] * land_size}</p><p><b>{t('Ideal Sowing Month')}:</b> {t('Month')} {recs['Sowing Month']}</p></div>", unsafe_allow_html=True)
                except: st.warning(t("⚠️ 'crop_engine_data.py' not found."))
            else: st.info(f"💡 {t(st.session_state.ai_mode)} {t('module is actively learning from your region data. Coming Soon!')}")

        # 🏛️ KNOWLEDGE HUB 
        elif st.session_state.module == "Knowledge Hub":
            if 'know_tab' not in st.session_state: st.session_state.know_tab = "Schemes"
            k_c1, k_c2, k_c3, k_c4 = st.columns(4)
            with k_c1:
                if st.button(f"📋 {t('Govt. Schemes')}", type="primary" if st.session_state.know_tab == "Schemes" else "secondary"): st.session_state.know_tab = "Schemes"; st.rerun()
            with k_c2:
                if st.button(f"📚 {t('Crop Compare')}", type="primary" if st.session_state.know_tab == "Library" else "secondary"): st.session_state.know_tab = "Library"; st.rerun()
            with k_c3:
                if st.button(f"📄 {t('Seed Repository')}", type="primary" if st.session_state.know_tab == "Repo" else "secondary"): st.session_state.know_tab = "Repo"; st.rerun()
            with k_c4:
                if st.button(f"📅 {t('Crop Calendar')}", type="primary" if st.session_state.know_tab == "Calendar" else "secondary"): st.session_state.know_tab = "Calendar"; st.rerun()
            
            st.markdown("<hr style='border-color: #22c55e; opacity: 0.3;'>", unsafe_allow_html=True)
            
            if st.session_state.know_tab == "Schemes":
                try:
                    from schemes_db import get_state_schemes, get_central_schemes
                    from Locations import india_map
                    state_sel = st.selectbox(t("Select Your State"), sorted(india_map.keys()))
                    state_data = get_state_schemes()
                    if state_data.get(state_sel): st.markdown(f"<div class='full-card anim-block d-3'><h3 style='color:#4ade80;'>📍 {t('State Special')}: {t(state_sel)}</h3><h4>{t(state_data[state_sel]['name'])}</h4><p>{t(state_data[state_sel]['desc'])}</p><a href='{state_data[state_sel]['link']}' target='_blank'><button style='padding:8px 15px; background-color:#22c55e; color:#0A192F; border-radius:8px; font-weight:bold; border:none; cursor:pointer;'>👉 {t('Apply on Portal')}</button></a></div>", unsafe_allow_html=True)
                    st.markdown(f"### 🌍 {t('Central Government Schemes')}")
                    for scheme in get_central_schemes():
                        with st.expander(f"✨ {t(scheme['name'])}"):
                            st.write(t(scheme['desc']))
                            st.markdown(f"<a href='{scheme['link']}' target='_blank' style='color:#FF8C00;'>🌐 {t('View Official Website')}</a>", unsafe_allow_html=True)
                except: st.warning(t("⚠️ Ensure 'schemes_db.py' & 'Locations.py' are present."))

            elif st.session_state.know_tab == "Library":
                try:
                    from crop_master import all_crops
                    c_names = [c['Crop'] for c in all_crops]
                    ca, cb = st.columns(2)
                    crop_1 = ca.selectbox(t("Crop 1"), c_names, index=0)
                    crop_2 = cb.selectbox(t("Crop 2"), c_names, index=1 if len(c_names)>1 else 0)
                    d1, d2 = next(i for i in all_crops if i["Crop"] == crop_1), next(i for i in all_crops if i["Crop"] == crop_2)
                    st.table(pd.DataFrame({t("Feature"): [t("Category"), t("Soil"), t("Season"), t("Water"), t("Pest"), t("N-P-K")], t(crop_1): [t(d1['Type']), t(d1['Soil']), t(d1['Season']), t(d1['Water']), t(d1['Pest']), d1['N-P-K']], t(crop_2): [t(d2['Type']), t(d2['Soil']), t(d2['Season']), t(d2['Water']), t(d2['Pest']), d2['N-P-K']]}).set_index(t("Feature")))
                except: st.warning(t("⚠️ Ensure 'crop_master.py' is present."))

            elif st.session_state.know_tab == "Repo":
                st.markdown(f"<h3 class='anim-block d-2'>📄 {t('Seed & Fertilizer Guides (PDF)')}</h3>", unsafe_allow_html=True)
                def create_pdf(title, body_text):
                    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", 'B', 16)
                    pdf.cell(200, 10, txt=title, ln=True, align='C'); pdf.ln(10)
                    pdf.set_font("Arial", size=12); pdf.multi_cell(0, 10, txt=body_text)
                    return pdf.output(dest='S').encode('latin1')
                
                repo_col1, repo_col2 = st.columns(2)
                with repo_col1:
                    st.markdown(f"<div class='full-card anim-block d-3'><h4>🌾 {t('Wheat Seed Guide')}</h4><p>{t('High-yield varieties, sowing time, and seed treatment details.')}</p></div>", unsafe_allow_html=True)
                    wheat_pdf = create_pdf("Wheat Seed Guide - ASES", "Wheat Seed Guide\n\n1. Best Varieties: HD 2967, PBW 343, DBW 17.\n2. Sowing Time: Nov to Dec.\n3. Seed Rate: 40 kg per acre.\n4. Treatment: Treat seeds with Carboxin.\n\nAgri Smart Ecosystem Solutions (ASES)")
                    st.download_button(label=f"📥 {t('Download Wheat Guide (PDF)')}", data=wheat_pdf, file_name="Wheat_Guide_ASES.pdf", mime="application/pdf", type="primary")
                with repo_col2:
                    st.markdown(f"<div class='full-card anim-block d-4'><h4>🧪 {t('Fertilizer (Urea) Chart')}</h4><p>{t('Proper NPK ratios and Urea application timings for major crops.')}</p></div>", unsafe_allow_html=True)
                    urea_pdf = create_pdf("Urea Application Chart - ASES", "Fertilizer & Urea Chart\n\n1. Wheat: Apply 1/3rd Urea at sowing, 1/3rd at 21 days.\n2. Rice: Apply Nitrogen in 3 split doses.\n3. Pro-Tip: Avoid applying Urea on heavy dew.\n\nAgri Smart Ecosystem Solutions (ASES)")
                    st.download_button(label=f"📥 {t('Download Urea Chart (PDF)')}", data=urea_pdf, file_name="Urea_Chart_ASES.pdf", mime="application/pdf", type="primary")

            elif st.session_state.know_tab == "Calendar":
                st.markdown(f"<h3 class='anim-block d-2'>📅 {t('Dynamic Crop Timeline Planner')}</h3>", unsafe_allow_html=True)
                try:
                    from crop_master import all_crops
                    c_names = [c['Crop'] for c in all_crops]
                    sel_cal_crop = st.selectbox(t("Select Crop to Track"), c_names)
                    c_data = next((item for item in all_crops if item["Crop"] == sel_cal_crop), None)
                    if c_data:
                        st.markdown(f"""
                        <div class='full-card anim-block d-3'>
                            <h3 style='color:#4ade80;'>{t(sel_cal_crop)} ({t(c_data['Season'])} {t('Crop')})</h3>
                            <p><b>🌱 {t('Sowing Readiness')}:</b> {t('Prepare land 15 days prior to season start.')}</p>
                            <p><b>✂️ {t('Harvesting Timeline')}:</b> {t(c_data['Harvesting'])}</p>
                            <hr class='thin-line'>
                            <p style='color:#FF8C00;'><b>💡 {t('Agronomist Pro-Tip')}:</b> {t(c_data['Pro-Tip'])}</p>
                        </div>
                        """, unsafe_allow_html=True)
                except: st.warning(t("⚠️ Ensure 'crop_master.py' is present."))

        # 📞 KISAN SAMPARK 
        elif st.session_state.module == "Kisan Sampark":
            try:
                from Locations import india_map
                loc_col1, loc_col2 = st.columns(2)
                with loc_col1: state_sel = st.selectbox(t("Select State"), sorted(india_map.keys()), index=12)
                with loc_col2: dist_sel = st.selectbox(t("Select District"), sorted(india_map.get(state_sel, ["Indore"])), index=0)
            except: dist_sel = "Indore"
            
            category_trans = st.radio(t("Select Farming Task:"), [t("Preparation"), t("Sowing"), t("Harvesting")], horizontal=True)
            eng_cat = "Preparation"
            for k, v in {"Preparation": t("Preparation"), "Sowing": t("Sowing"), "Harvesting": t("Harvesting")}.items():
                if v == category_trans: eng_cat = k
            
            machines = {
                "Preparation": [("Rotavator", "🚜", "₹500/Hr", "Sunil Verma", "+919876543210"), ("Power Tiller", "⚙️", "₹400/Hr", "Rajesh Kumar", "+919876543211")], 
                "Sowing": [("Seed Drill", "🌱", "₹600/Hr", "Amit Singh", "+919876543212"), ("Transplanter", "🌾", "₹700/Hr", "Vikram Patel", "+919876543213")], 
                "Harvesting": [("Harvester", "🌾✨", "₹1500/Hr", "Ramesh Yadav", "+919876543214"), ("Thresher", "🌪️", "₹800/Hr", "Suresh Tiwari", "+919876543215")]
            }
            
            cols = st.columns(len(machines.get(eng_cat, [])))
            for idx, (m_name, icon, rate, owner, phone) in enumerate(machines.get(eng_cat, [])):
                with cols[idx]: 
                    st.markdown(f"""
                    <div class='full-card anim-block d-3'>
                        <h3 style='color:#4ade80;'>{icon} {t(m_name)}</h3>
                        <p><b>{t('Owner')}:</b> {t(owner)}<br><b>{t('Rate')}:</b> {rate}</p>
                        <a href='tel:{phone}' class='call-btn'>📞 {t('Call Now')}</a>
                    </div>
                    """, unsafe_allow_html=True)

        # 📉 PRICE TRENDS
        elif st.session_state.module == "Price Trends":
            try:
                from crop_master import all_crops
                from Locations import india_map
                col1, col2 = st.columns(2)
                with col1: sel_state = st.selectbox(t("State"), sorted(india_map.keys()), index=12)
                with col2: sel_c = st.selectbox(t("Commodity"), [c['Crop'] for c in all_crops] if all_crops else ["Wheat", "Rice"])
                if st.button(t("Get Live Price"), type="primary"):
                    data = requests.get("https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070", params={"api-key": "579b464db66ec23bdd0000019b64f520463c4fba468cc24026c3cff6", "format": "json", "filters[state]": sel_state, "filters[commodity]": sel_c}).json()
                    if "records" in data and data["records"]: st.success(t("✅ Data Fetched Successfully!")); st.metric(f"{t('Live Price in')} {t(data['records'][0]['market'])}", f"₹{data['records'][0]['modal_price']}/{t('Quintal')}")
                    else: st.info(f"{t('No live data available for')} {t(sel_c)} {t('in')} {t(sel_state)} {t('today. Showing annual prediction trend.')}")
                st.markdown("<div class='full-card anim-block d-3'>", unsafe_allow_html=True)
                st.plotly_chart(px.line(x=[t(m) for m in ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]], y=[2100, 2050, 2150, 2200, 2300, 2250, 2350, 2400, 2380, 2450, 2500, 2480], title=t("Annual Price Cycle Prediction")), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            except: st.warning(t("⚠️ Ensure 'crop_master.py', 'Locations.py' and 'plotly.express' are installed."))

        # 📒 AGRI LEDGER
        elif st.session_state.module == "Agri Ledger":
            if not st.session_state.logged_in:
                st.warning(t("🔒 Please Log In or Sign Up to access your private Agri Ledger."))
                if st.button(t("Log In Now"), type="primary"): st.session_state.auth_mode = "login"; st.rerun()
            else:
                conn = sqlite3.connect('agri_khata.db')
                df_khata = pd.read_sql_query(f"SELECT * FROM ledger WHERE user_key='{st.session_state.user_email}'", conn)
                conn.close()
                inc = df_khata[df_khata['type'].str.contains('Income')]['total'].sum() if not df_khata.empty else 0
                exp = df_khata[df_khata['type'].str.contains('Expense')]['total'].sum() if not df_khata.empty else 0
                st.markdown(f"<div class='full-card anim-block d-2'><h3 style='color:#4ade80;'>{t('Total Balance')}: ₹{inc - exp:,.2f}</h3><p>{t('Income')}: ₹{inc} | {t('Expenses')}: ₹{exp}</p></div>", unsafe_allow_html=True)
                if not df_khata.empty: st.dataframe(df_khata.drop(columns=['id', 'user_key']), use_container_width=True)
                with st.expander(f"➕ {t('Add New Entry')}"):
                    with st.form("add_f"):
                        t_type_trans = st.selectbox(t("Type"), [t("Income (Sales)"), t("Expense (Seeds/Labor/Machine)")])
                        t_type = "Income (Sales)" if t_type_trans == t("Income (Sales)") else "Expense (Seeds/Labor/Machine)"
                        itm = st.text_input(t("Item Name"))
                        amt = st.number_input(t("Amount (₹)"), min_value=0.0)
                        if st.form_submit_button(f"💾 {t('Save Entry')}"):
                            conn = sqlite3.connect('agri_khata.db')
                            conn.execute("INSERT INTO ledger (user_key, date, type, item, qty, total, season) VALUES (?,?,?,?,?,?,?)", (st.session_state.user_email, time.strftime("%Y-%m-%d"), t_type, itm, "1", amt, "General"))
                            conn.commit(); conn.close()
                            st.rerun()

# --- 9. SMART FOOTER & LOGOUT ---
if st.session_state.logged_in and st.session_state.auth_mode is None:
    st.markdown("<hr style='border-color: #22c55e; opacity: 0.3; margin-top: 50px;'>", unsafe_allow_html=True)
    foot_c1, foot_c2 = st.columns([5, 1])
    with foot_c1:
        st.markdown(f"<p style='color:#94a3b8; font-weight:bold;'>🌿 ASES: {t('Visual Precision Advisory & Smart Connectivity')}</p>", unsafe_allow_html=True)
    with foot_c2:
        if st.button(f"🚪 {t('Logout')}", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.user_name = ""
            st.session_state.user_email = ""
            st.session_state.auth_mode = None
            st.rerun()