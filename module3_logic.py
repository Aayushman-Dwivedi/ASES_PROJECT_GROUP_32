import json
import streamlit as st

# --- 1. पेज कॉन्फ़िगरेशन और स्टाइलिंग ---
st.set_page_config(page_title="Agri-Doctor | ASES", layout="centered")

# CSS Fix: कार्ड को छोटा किया गया और टेक्स्ट का रंग फिक्स किया गया
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    
    .diagnosis-card {
        background-color: #ffffff;
        padding: 12px 18px; /* पैडिंग कम की गई */
        border-radius: 12px;
        border-left: 6px solid #2e7d32;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        color: #1b5e20 !important; /* टेक्स्ट का रंग डार्क ग्रीन फिक्स किया गया */
    }
    
    .diagnosis-card h3 {
        margin: 0px 0px 5px 0px !important;
        padding: 0px !important;
        color: #1b5e20 !important;
    }

    .diagnosis-card p {
        margin: 0px !important;
        font-size: 0.95rem;
        line-height: 1.4;
        color: #333333 !important; /* डिस्क्रिप्शन का रंग डार्क ग्रे */
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. डेटा लोड करना ---
def load_pest_data():
    with open('pests.json', 'r', encoding='utf-8') as file:
        return json.load(file)

pest_data = load_pest_data()

season_mapping = {
    "Kharif (Monsoon: Jun - Oct)": ["Rice", "Cotton", "Maize", "Sugarcane"],
    "Rabi (Winter: Nov - Apr)": ["Wheat", "Tomato"],
    "Zaid (Summer: Mar - Jun)": ["Maize", "Tomato"]
}

# --- 3. UI/UX: Header & Toggle ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("👨‍⚕️ Agri-Doctor")
with col2:
    st.write("") # स्पैसर
    lang_hi = st.toggle("हिंदी", value=False)

# --- 4. फिल्टर सेक्शन ---
selected_season = st.selectbox("🌦️ " + ("मौसम" if lang_hi else "Season"), list(season_mapping.keys()))

if selected_season:
    available_crops = season_mapping[selected_season]
    valid_crops = [crop for crop in available_crops if crop in pest_data]
    selected_crop = st.selectbox("🌱 " + ("फसल" if lang_hi else "Crop"), valid_crops)

    if selected_crop:
        pest_list = list(pest_data[selected_crop].keys())
        selected_pest = st.selectbox("🐛 " + ("बीमारी" if lang_hi else "Pest/Disease"), pest_list)

        if selected_pest:
            details = pest_data[selected_crop][selected_pest]
            
            desc = details.get("simple_desc_hi" if lang_hi else "simple_desc_en", "")
            symp = details.get("symptoms_hi" if lang_hi else "symptoms_en", "")
            chem = details.get("chemical_remedy_hi" if lang_hi else "chemical_remedy_en", "")
            org = details.get("organic_remedy_hi" if lang_hi else "organic_remedy_en", "")

            # --- 5. डिस्प्ले कार्ड (छोटा और भरा हुआ) ---
            st.markdown(f"""
                <div class="diagnosis-card">
                    <h3>📋 {selected_pest}</h3>
                    <p>{desc}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # एक्सपैंडर्स
            with st.expander("🔍 " + ("लक्षण" if lang_hi else "Symptoms")):
                st.write(symp)
            
            with st.expander("🧪 " + ("रासायनिक उपचार" if lang_hi else "Chemical Treatment")):
                st.error(chem)
                
            with st.expander("🍃 " + ("जैविक उपचार" if lang_hi else "Organic Solution")):
                st.success(org)

st.sidebar.info("Module C: Resilience & Domain Specialist\n\nStatus: 50% Complete")