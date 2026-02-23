import streamlit as st
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Page config
st.set_page_config(
    page_title="AI Duygu Analizi",
    page_icon="🧠",
    layout="centered"
)

# Initialize session state for example selection
if 'example_text' not in st.session_state:
    st.session_state['example_text'] = ''

# Get configuration from environment
API_URL = f"http://{os.getenv('BACKEND_HOST', '127.0.0.1')}:{os.getenv('BACKEND_PORT', '8000')}/predict"
API_KEY = os.getenv("API_KEY")

st.title("🧠 AI Duygu Analizi")
st.write("Metnin duygu durumunu analiz edin")

# Check if API key is configured
if not API_KEY:
    st.error("⚠️ API anahtarı bulunamadı! Lütfen .env dosyasını kontrol edin.")
    st.stop()

# Sidebar with information
with st.sidebar:
    st.header("📊 Model Bilgisi")
    st.info(f"""
    **Model:** {os.getenv('MODEL_NAME', 'distilbert-base-uncased')}
    **Max Length:** {os.getenv('MAX_LENGTH', '512')}
    **Environment:** {os.getenv('ENVIRONMENT', 'development')}
    """)
    
    st.header("📝 Örnek Metinler")
    examples = [
        "Bugün hava çok güzel, kendimi harika hissediyorum!",
        "Bu film çok kötüydü, zaman kaybı.",
        "Yemekler lezzetliydi ama servis biraz yavaştı.",
        "Harika bir gün! Her şey mükemmel.",
        "Çok sinirliyim ve hayal kırıklığına uğradım."
    ]
    
    selected_example = st.selectbox(
        "Bir örnek seçin:",
        [""] + examples,
        key="example_selector"
    )
    
    if selected_example:
        st.session_state['example_text'] = selected_example

# Main content
text = st.text_area(
    "Metni girin:",
    value=st.session_state.get('example_text', ''),
    height=150,
    placeholder="Analiz edilecek metni buraya yazın..."
)

col1, col2 = st.columns([1, 5])
with col1:
    analyze_button = st.button("🔍 Analiz Et", type="primary", use_container_width=True)
with col2:
    clear_button = st.button("🗑️ Temizle", use_container_width=True)

if clear_button:
    st.session_state['example_text'] = ''
    st.rerun()

if analyze_button:
    if not text:
        st.warning("⚠️ Lütfen bir metin girin.")
    else:
        headers = {"x-api-key": API_KEY}
        try:
            with st.spinner("🔄 Analiz ediliyor..."):
                response = requests.post(
                    API_URL,
                    json={"text": text},
                    headers=headers,
                    timeout=10
                )

            if response.status_code == 200:
                result = response.json()
                st.success("✅ Analiz tamamlandı")
                
                # Create columns for metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    positive_pct = result['positive'] * 100
                    st.metric(
                        "😊 Pozitif", 
                        f"{positive_pct:.1f}%",
                        delta=None
                    )
                
                with col2:
                    negative_pct = result['negative'] * 100
                    st.metric(
                        "😠 Negatif", 
                        f"{negative_pct:.1f}%",
                        delta=None
                    )
                
                with col3:
                    st.metric(
                        "📏 Metin Uzunluğu",
                        result.get('text_length', len(text)),
                        delta=None
                    )
                
                # Progress bar
                st.progress(result['positive'])
                
                # Sentiment interpretation
                if result['positive'] > 0.6:
                    st.success("📈 **Çok Pozitif** - Metin oldukça olumlu bir duygu taşıyor!")
                elif result['positive'] > 0.4:
                    st.info("📊 **Nötr** - Metin dengeli bir duygu taşıyor.")
                else:
                    st.error("📉 **Negatif** - Metin olumsuz bir duygu taşıyor.")
                    
            elif response.status_code == 401:
                st.error("❌ API Anahtarı hatası! Lütfen API anahtarınızı kontrol edin.")
            else:
                st.error(f"❌ API hatası: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Backend sunucusuna bağlanılamadı!")
            st.info("💡 Backend'i başlatmak için: `uvicorn backend.app:app --reload`")
        except requests.exceptions.Timeout:
            st.error("❌ Sunucu yanıt vermedi. Lütfen tekrar deneyin.")
        except Exception as e:
            st.error(f"❌ Beklenmeyen bir hata oluştu: {str(e)}")

# Footer
st.markdown("---")
st.markdown("🚀 Powered by FastAPI + TensorFlow + Streamlit")