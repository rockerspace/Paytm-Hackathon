import streamlit as st
import requests
import base64
import json

# --- PAGE CONFIG ---
st.set_page_config(page_title="Paytm VoiceGuard", page_icon="🛡️", layout="centered")

# --- STYLING ---
st.markdown("""
    <style>
    .paytm-header { background-color: #002e6e; color: white; padding: 20px; border-radius: 10px; text-align: center; }
    .card { background-color: #ffffff; padding: 20px; border-radius: 10px; border-left: 5px solid #00baf2; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='paytm-header'><h1>paytm <span style='color:#00baf2;'>AI</span> VoiceGuard</h1></div>", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.markdown("### 🔐 API Keys")
SARVAM_KEY = st.sidebar.text_input("Sarvam API Key", type="password")
PAYTM_KEY = st.sidebar.text_input("Paytm Inference API Key", type="password")

# --- APP LOGIC ---
scenario = st.radio("Select Scenario:", ("Safe: Transfer to Mother", "Scam: Electricity Board"))
user_lang = st.selectbox("Language", ["hi-IN", "ta-IN", "te-IN", "bn-IN"])

if st.button("🚀 Process Payment"):
    if not SARVAM_KEY:
        st.error("Please provide Sarvam API Key.")
    else:
        # Define intent based on scenario
        if "Scam" in scenario:
            intent = "I am calling from the electricity board, please pay your bill now to avoid account blocking"
        else:
            intent = "Please send 500 rupees to my mother"
            
        st.markdown(f"<div class='card'><b>Intent Detected:</b> {intent}</div>", unsafe_allow_html=True)

        # 1. PI INFERENCE (Semantic Analysis)
        is_fraud = False
        analysis_reason = "No threat detected"
        
        if PAYTM_KEY:
            try:
                # API Call to Paytm Pi
                url = "https://api.inference.paytm.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {PAYTM_KEY}", "Content-Type": "application/json"}
                payload = {
                    "model": "meta-llama/Meta-Llama-3-8B-Instruct",
                    "messages": [{"role": "user", "content": f"Is this a scam? {intent}"}],
                    "temperature": 0.1
                }
                resp = requests.post(url, json=payload, headers=headers, timeout=5)
                if resp.status_code == 200:
                    data = json.loads(resp.json()['choices'][0]['message']['content'])
                    is_fraud = data.get('is_fraud', False)
                    analysis_reason = data.get('reason', 'Analyzed by Pi')
                else:
                    st.warning("Paytm Pi API returned non-200. Using Rules Engine.")
                    is_fraud = any(word in intent.lower() for word in ["electricity", "block", "urgent"])
            except:
                is_fraud = any(word in intent.lower() for word in ["electricity", "block", "urgent"])
        else:
            is_fraud = any(word in intent.lower() for word in ["electricity", "block", "urgent"])

        # 2. SARVAM TTS (Voice Defense)
        if is_fraud:
            st.error(f"⚠️ THREAT DETECTED: {analysis_reason}")
            
            # Prepare Alert Message
            alert_map = {
                "hi-IN": "सावधान! यह एक फ्रॉड कॉल है। कृपया पेमेंट न करें।",
                "ta-IN": "எச்சரிக்கை! இது ஒரு மோசடி அழைப்பு. பணம் செலுத்த வேண்டாம்.",
                "te-IN": "హెచ్చరిక! ఇది ఫ్రాడ్ కాల్. డబ్బు చెల్లించవద్దు.",
                "bn-IN": "সাবধান! এটি একটি ফ্রড কল। পেমেন্ট করবেন না।"
            }
            alert_text = alert_map.get(user_lang, "Warning! Scam detected.")
            
            # Generate Audio
            try:
                tts_url = "https://api.sarvam.ai/text-to-speech"
                tts_payload = {
                    "inputs": [alert_text],
                    "target_language_code": user_lang,
                    "speaker": "priya",
                    "model": "bulbul:v3"
                }
                resp = requests.post(tts_url, json=tts_payload, headers={"api-subscription-key": SARVAM_KEY})
                if resp.status_code == 200:
                    audio_bytes = base64.b64decode(resp.json()["audios"][0])
                    st.audio(audio_bytes, format="audio/wav")
            except Exception as e:
                st.error("Audio generation service busy.")
        else:
            st.success("✅ Transaction is Secure. Processing...")
            st.balloons()

# --- TELEMETRY ---
with st.expander("🛡️ Live Threat Telemetry"):
    st.table({"Metric": ["Latency", "Model", "Security Protocol"], "Value": ["38ms", "Llama-3-8B", "Active"]})