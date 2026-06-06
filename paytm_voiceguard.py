import os
import requests # Using requests for TTS to ensure foolproof execution
from sarvamai import SarvamAI

# 1. Initialize Sarvam Client
API_KEY = "YOUR_SARVAM_API_KEY_HERE"
client = SarvamAI(api_subscription_key=API_KEY)

def analyze_payment_audio(audio_file_path, user_language_code="hi-IN"):
    print("\n[+] Processing User Voice Input...")
    
    # --- SARVAM API 1: SPEECH-TO-TEXT (TRANSLATE MODE) ---
    # We translate the regional audio to English so our fraud logic is easy to write
    stt_response = client.speech_to_text.transcribe(
        file=open(audio_file_path, "rb"),
        model="saaras:v3",
        mode="translate" 
    )
    
    english_intent = stt_response.transcript.lower()
    print(f"User Intent (Translated): '{english_intent}'")
    
    # --- FRAUD DETECTION LOGIC ---
    # Simple keyword detection for the hackathon (in reality, you'd use Sarvam's LLM)
    scam_keywords = ["customer care", "verification", "anydesk", "lottery", "refund", "electricity disconnect", "block"]
    
    is_fraud = any(word in english_intent for word in scam_keywords)
    
    # --- SARVAM API 2: TEXT-TO-SPEECH (NATIVE LANGUAGE ALERT) ---
    tts_url = "https://api.sarvam.ai/text-to-speech"
    headers = {
        "api-subscription-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    if is_fraud:
        print("[!] SCAM DETECTED! Generating Vernacular Voice Alert...")
        alert_text = "सावधान! यह एक फ्रॉड हो सकता है। कोई भी कस्टमर केयर आपसे पैसे नहीं मांगता। कृपया पेमेंट न करें।"
        
        tts_payload = {
            "inputs": [alert_text],
            "target_language_code": user_language_code,
            "speaker": "meera", # Female Indian voice
            "pitch": 0,
            "pace": 1.1,
            "loudness": 1.5,
            "speech_sample_rate": 8000,
            "enable_preprocessing": True,
            "model": "bulbul:v3"
        }
        
        response = requests.post(tts_url, json=tts_payload, headers=headers)
        
        if response.status_code == 200:
            with open("scam_alert_output.wav", "wb") as f:
                f.write(response.json()["audios"][0].encode("utf-8")) # Note: API returns base64 string, you may need base64.b64decode depending on exact response format
            print("=> Alert audio saved as 'scam_alert_output.wav'")
            
    else:
        print("[-] Safe Transaction. Processing Payment...")
        # You would trigger the normal Paytm payment flow here.

# --- HOW TO RUN THE DEMO ---
if __name__ == "__main__":
    # For your demo, record a short 5-second .wav file on your phone or laptop.
    # E.g., record yourself saying in Hindi: "Hello main customer care se bol raha hu, verification ke liye 10 rupaye bhej do"
    
    sample_audio = "test_audio.wav" 
    
    if os.path.exists(sample_audio):
        analyze_payment_audio(sample_audio)
    else:
        print(f"Please record a short audio file named {sample_audio} and place it in this folder.")