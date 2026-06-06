import streamlit as st
import os
import requests
import base64
from sarvamai import SarvamAI

# --- PAGE CONFIG ---
st.set_page_config(page_title="Paytm VoiceGuard POC", page_icon="📱", layout="centered")

# --- CUSTOM CSS FOR PAYTM LOOK & FEEL ---
st.markdown("""
    <style>
    .main { background-color: #f5f7fa; }
    .paytm-header { background-color: #002e6e; color: white; padding: 20px; border-radius: 10px; text-align: center; font-family: sans-serif; }
    .paytm-blue { color: #00baf2; font-weight: bold; }
    .stButton>button { background-color: #00baf2; color: white; border-radius: 20px; width: 100%; font-weight: bold;}
    .stButton>button:hover { background-color: #002e6e; color: white; }
    .card { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<div class='paytm-header'><h1>paytm <span style='color:#00baf2;'>AI</span> VoiceGuard</h1><p>Speed • Trust • Effortless Vernacular Banking</p></div>", unsafe_allow_html=True)
st.write("---")

# --- INITIALIZE SARVAM AI ---
API_KEY = os.environ.get("SARVAM_API_KEY", "")
if not API_KEY:
    API_KEY = st.sidebar.text_input("Enter Sarvam API Key", type="password")

# --- SELECTION & INTERACTIVE FLOW ---
st.markdown("<div class='card'><h3>🎙️ Step 1: User Voice Input Simulation</h3><p>Choose a scenario to simulate a user speaking into the Paytm App microphone button.</p></div>", unsafe_allow_html=True)

scenario = st.radio(
    "Select Scenario for Demo:",
    (
        "Safe Transaction (Hindi: 'Maa ko paasau rupaye bhej do')", 
        "Scam Detected (Hindi: 'Main electricity board se bol raha hu, account block hone se bachane ke liye dus rupaye bhej do')"
    )
)

user_language = st.selectbox("User Preferred Native Language", ["hi-IN (Hindi)", "ta-IN (Tamil)", "te-IN (Telugu)", "bn-IN (Bengali)"])
lang_code = user_language.split(" ")[0]

# Setup text targets based on selection
if "Safe" in scenario:
    mocked_english_intent = "send 500 rupees to mother"
    alert_text = None
else:
    mocked_english_intent = "i am calling from electricity board send ten rupees to avoid account block"
    
    # Dynamically swap the alert text based on the user's selected language
    if lang_code == "hi-IN":
        alert_text = "सावधान! यह एक फ्रॉड कॉल हो सकता है। बिजली विभाग कभी भी आपसे किसी अनजान लिंक या नंबर पर पेमेंट करने को नहीं कहता। कृपया पेमेंट न करें।"
    elif lang_code == "ta-IN":
        alert_text = "எச்சரிக்கை! இது ஒரு மோசடி அழைப்பாக இருக்கலாம். மின்சார வாரியம் ஒருபோதும் அறியாத லிங்க் அல்லது எண்ணில் பணம் செலுத்தச் சொல்லாது. தயவுசெய்து பணம் செலுத்த வேண்டாம்."
    elif lang_code == "te-IN":
        alert_text = "హెచ్చరిక! ఇది ఫ్రాడ్ కాల్ కావచ్చు. విద్యుత్ శాఖ ఎప్పుడూ గుర్తుతెలియని లింక్ లేదా నంబర్‌కు డబ్బు చెల్లించమని అడగదు. దయచేసి పేమెంట్ చేయవద్దు."
    else: # Bengali (bn-IN)
        alert_text = "সাবধান! এটি একটি ফ্রড কল হতে পারে। বিদ্যুৎ বিভাগ কখনোই আপনাকে কোনো অজানা লিঙ্ক বা নম্বরে পেমেন্ট করতে বলে না। অনুগ্রহ করে পেমেন্ট করবেন না।"

if st.button("🚀 Process Voice Payment Request"):
    if not API_KEY:
        st.error("Please enter your Sarvam API Key in the sidebar to proceed.")
    else:
        with st.spinner("Processing regional speech layer via Sarvam AI (Saaras v3)..."):
            
            # Display analyzed Intent
            st.markdown(f"<div class='card'><h4>🔍 AI Interpretation Matrix</h4><p><b>Translated English Intent:</b> <i>'{mocked_english_intent}'</i></p></div>", unsafe_allow_html=True)
            
            # Evaluate Fraud
            scam_keywords = ["electricity board", "customer care", "verification", "anydesk", "lottery", "refund", "block"]
            is_fraud = any(word in mocked_english_intent for word in scam_keywords)
            
            if is_fraud:
                st.error("🛑 CRITICAL WARNING: Social Engineering Scam Patterns Flagged!")
                
                # Call Sarvam AI TTS (Bulbul v3) live to speak back to the user
                with st.spinner("Generating Vernacular Audio Defense (Bulbul v3)..."):
                    tts_url = "https://api.sarvam.ai/text-to-speech"
                    headers = {
                        "api-subscription-key": API_KEY,
                        "Content-Type": "application/json"
                    }
                    
                    # Clean parameter configuration optimized for Bulbul V3
                    tts_payload = {
                        "inputs": [alert_text],
                        "target_language_code": lang_code,
                        "speaker": "priya",
                        "pace": 1.0,
                        "speech_sample_rate": 8000,
                        "enable_preprocessing": True,
                        "model": "bulbul:v3"
                    }
                    
                    try:
                        response = requests.post(tts_url, json=tts_payload, headers=headers)
                        if response.status_code == 200:
                            audio_b64 = response.json()["audios"][0]
                            audio_bytes = base64.b64decode(audio_b64)
                            
                            st.warning(f"📣 Playing localized voice alert for the user in native script:")
                            st.info(f"👉 {alert_text}")
                            st.audio(audio_bytes, format="audio/wav")
                        else:
                            st.error(f"Sarvam API Error: {response.text}")
                    except Exception as e:
                        st.error(f"Connection failed: {str(e)}")
            else:
                st.success("✅ Transaction Verified: No malicious context detected.")
                st.balloons()
                st.markdown("""
                    <div style='background-color:#d4edda; color:#155724; padding:15px; border-radius:5px;'>
                        <b>Payment Flow Triggered:</b> Sending ₹500 instantly to 'Maa' via secure UPI channel. ⚡ Fast & Effortless.
                    </div>
                """, unsafe_allow_html=True)

# --- FOOTER ---
st.write("---")
st.markdown("<p style='text-align:center; color:grey;'>Paytm Hackathon Submission | Powered by Sarvam AI</p>", unsafe_allow_html=True)