import streamlit as st
import joblib
import pandas as pd
import gdown
import os

# ຕັ້ງຄ່າໜ້າຈໍ Dashboard
st.set_page_config(page_title="IoT Soil & Air Quality", layout="wide")
st.title("🌱 ລະບົບຕິດຕາມຄຸນນະພາບດິນ ແລະ ອາກາດ Real-time (AI)")

# ---ເພີ່ມ Font ພາສາລາວ (CSS) ---
st.markdown("""
    <style>
    /* ນຳເຂົ້າຟອນ Phetsarath ຈາກ Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Phetsarath&display=swap');

    /* ປ່ຽນຟອນຂອງທຸກໆຕົວອັກສອນໃນໜ້າເວັບ */
    html, body, [class*="css"], .stText, h1, h2, h3, h4, h5, h6, p, span, label {
        font-family: 'Phetsarath OT+Time New Roman','Phetsarath', 'Saysettha OT', sans-serif !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ໂຫລດ Model ຈາກ Google Drive (ເພີ່ມລະບົບດາວໂຫລດອັດຕະໂນມັດ)
@st.cache_resource
def load_model():
    # ⚠️ ເອົາ ID ໄຟລ໌ Google Drive ຂອງທ່ານມາປ່ຽນໃສ່ບ່ອນນີ້ເດີ້
    file_id = "YOUR_GOOGLE_DRIVE_FILE_ID_HERE" 
    model_path = "my_iot_model.pkl"
    
    # ຖ້າໃນເຊີເວີຍັງບໍ່ມີໄຟລ໌ model ໃຫ້ດາວໂຫລດມາທັນທີ
    if not os.path.exists(model_path):
        with st.spinner("ກຳລັງໂຫລດ AI Model ຈາກ Google Drive... กรุณารอสักครู่"):
            url = f'https://drive.google.com/uc?id={file_id}'
            gdown.download(url, model_path, quiet=False)
            
    return joblib.load(model_path)

model = load_model()

# ຟັງຊັນຈັດກຸ່ມ (Good, Moderate, Poor)
def get_status_info(value, metric_type):
    if metric_type == "air":
        if value <= 12: return "Good", "🟢 ດີຫຼາຍ", "#2ecc71"
        elif value <= 14: return "Moderate", "🟡 ປານກາງ", "#f1c40f"
        else: return "Poor", "🔴 ບໍ່ດີ (ອັນຕະລາຍ)", "#e74c3c"
    elif metric_type == "soil":
        if value < 20: return "Poor", "🔴 ແຫ້ງແລ້ງເກີນໄປ", "#e74c3c"
        elif value <= 40: return "Moderate", "🟡 ປານກາງ", "#f1c40f"
        else: return "Good", "🟢 ຊຸ່ມຊື່ນດີ", "#2ecc71"

# Sidebar ສຳລັບຈຳລອງຄ່າ IoT
st.sidebar.header("🔌 ຄ່າຈາກເຊັນເຊີ IoT (ປັດຈຸບັນ)")
t = st.sidebar.slider("ອຸນຫະພູມຂອງອາກາດ (t)", 10.0, 45.0, 25.0)
h = st.sidebar.slider("ຄວາມຊຸ່ມຊື່នຂອງອາກາດ (h)", 10.0, 100.0, 80.0)
pm1 = st.sidebar.slider("ຝຸ່ນ PM1", 5, 20, 11)
pm10 = st.sidebar.slider("ຝຸ່ນ PM10", 5, 30, 14)
temperature = st.sidebar.slider("ອຸນຫະພູມຂອງດິນ", 15.0, 35.0, 21.0)
EC = st.sidebar.slider("ຄ່າ EC ໃນດິນ", 0.0, 5.0, 1.9)
pH = st.sidebar.slider("ຄ່າ pH ໃນດິນ", 4.0, 9.0, 5.3)
nitrogen = st.sidebar.slider("ຄ່າ Nitrogen (N)", 0.0, 10.0, 0.5)
phosphorus = st.sidebar.slider("ຄ່າ Phosphorus (P)", 0.0, 10.0, 4.6)
potassium = st.sidebar.slider("ຄ່າ Potassium (K)", 0.0, 10.0, 4.4)
phw = st.sidebar.slider("ຄ່າ pH ຂອງນ້ຳ", 4.0, 9.0, 5.4)
tds = st.sidebar.slider("ຄ່າ TDS ຂອງນ້ຳ", 50.0, 300.0, 113.0)

input_data = pd.DataFrame([{
    'temperature': temperature, 'EC': EC, 'pH': pH,
    'nitrogen': nitrogen, 'phosphorus': phosphorus, 'potassium': potassium,
    't': t, 'h': h, 'pm1': pm1, 'pm10': pm10, 'phw': phw, 'tds': tds
}])

prediction = model.predict(input_data)
pred_pm25 = float(prediction[0][0])
pred_soil_hum = float(prediction[0][1])

air_label, air_text, air_color = get_status_info(pred_pm25, "air")
soil_label, soil_text, soil_color = get_status_info(pred_soil_hum, "soil")

col1, col2 = st.columns(2)
with col1:
    st.subheader("🌤️ ຄຸນນະພາບອາກາດ")
    st.markdown(f'<div style="background-color:{air_color}; padding:20px; border-radius:10px; text-align:center;"><h2 style="color:white; margin:0;">{air_text}</h2><p style="color:white; font-size:20px; margin:10px 0 0 0;">ຄ່າ PM2.5: <b>{pred_pm25:.2f} µg/m³</b></p></div>', unsafe_allow_html=True)
with col2:
    st.subheader("🌱 ຄຸນນະພາບດິນ")
    st.markdown(f'<div style="background-color:{soil_color}; padding:20px; border-radius:10px; text-align:center;"><h2 style="color:white; margin:0;">{soil_text}</h2><p style="color:white; font-size:20px; margin:10px 0 0 0;">ຄວາມຊຸ່ມຊື່ນດິນ: <b>{pred_soil_hum:.2f} %</b></p></div>', unsafe_allow_html=True)