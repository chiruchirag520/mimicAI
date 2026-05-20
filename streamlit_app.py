import streamlit as st
import os
import sys
import time
from pathlib import Path
from streamlit_mic_recorder import mic_recorder

# Ensure local modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sarvam_tts import SarvamAIClient
from tts_remote import RemoteTTSClient
from cartesia_tts import CartesiaAudioClient
from fish_tts import FishAudioClient

# Page configuration
st.set_page_config(
    page_title="Universal AI Voice Assistant",
    page_icon="🎙️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .status-box { padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; }
    .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .info { background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎙️ Universal AI Voice Assistant")
st.markdown("Integrated **Translation**, **STT**, and **TTS** powered by Sarvam AI & OpenRouter.")

# Initialize Client
sarvam = SarvamAIClient()

# Sidebar
st.sidebar.title("🛠️ Tools & Modes")
app_mode = st.sidebar.radio(
    "Choose Feature",
    ["TTS (Direct)", "Translate & Speak", "Voice Assistant (STT -> Translate -> TTS)", "Voice Cloning (Zero-Shot)"]
)

# Language Mapping
LANG_MAP = {
    "English": "en-IN",
    "Kannada": "kn-IN",
    "Hindi": "hi-IN",
    "Bengali": "bn-IN",
    "Malayalam": "ml-IN",
    "Marathi": "mr-IN",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Gujarati": "gu-IN",
    "Punjabi": "pa-IN"
}

# Voice Options for Sarvam AI
SARVAM_VOICES = {
    "Male": ["shubh", "aditya", "ashutosh", "rahul", "rohan", "amit", "dev", "ratan", "varun", "manan", "sumit", "kabir", "aayan", "advait", "anand", "tarun", "sunny", "mani", "gokul", "vijay", "mohit", "rehan", "soham"],
    "Female": ["ritu", "priya", "neha", "pooja", "simran", "kavya", "ishita", "shreya", "roopa", "tanya", "shruti", "suhani", "kavitha", "rupali", "niharika"]
}

# --- MODE 1: TTS DIRECT ---
if app_mode == "TTS (Direct)":
    st.header("🔊 Text-to-Speech")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        text = st.text_area("Enter text", height=150)
    
    with col2:
        provider = st.selectbox("Provider", ["Sarvam AI (Free)", "OpenRouter"])
        if provider == "Sarvam AI (Free)":
            target_lang = st.selectbox("Language", list(LANG_MAP.keys()), index=0)
            voice_gender = st.radio("Voice Gender", ["Male", "Female"])
            voice = st.selectbox("Voice Name", SARVAM_VOICES[voice_gender])
        else:
            voice = st.selectbox("Voice", ["alloy", "echo", "fable", "onyx", "nova", "shimmer"], index=4)
        speed = st.slider("Speed", 0.5, 2.0, 1.0)

    if st.button("Generate Audio"):
        if text:
            try:
                with st.spinner("Processing..."):
                    if provider == "Sarvam AI (Free)":
                        audio = sarvam.synthesize(text, lang_code=LANG_MAP[target_lang], voice=voice, speed=speed)
                    else:
                        client = RemoteTTSClient()
                        audio = client.synthesize(text, voice=voice, speed=speed)
                    
                    st.audio(audio)
                    st.download_button("Download", audio, "audio.wav" if provider=="Sarvam AI (Free)" else "audio.mp3")
            except Exception as e:
                st.error(f"Error: {e}")

# --- MODE 2: TRANSLATE & SPEAK ---
elif app_mode == "Translate & Speak":
    st.header("🌐 Translate & Speak")
    col1, col2 = st.columns(2)
    
    with col1:
        source_text = st.text_area("Enter English Text", placeholder="Type here in English...", height=150)
        source_lang = "en-IN"
        
    with col2:
        target_lang_name = st.selectbox("Translate to", list(LANG_MAP.keys()), index=1) # Default to Kannada
        target_lang = LANG_MAP[target_lang_name]
        voice_gender = st.radio("Voice Gender", ["Male", "Female"])
        voice = st.selectbox("Voice Name", SARVAM_VOICES[voice_gender])

    if st.button("Translate and Play"):
        if source_text:
            try:
                with st.spinner("Translating..."):
                    translated = sarvam.translate(source_text, source_lang=source_lang, target_lang=target_lang)
                    if not translated:
                        st.warning("Translation returned empty result.")
                        st.stop()
                    st.info(f"**Translated ({target_lang_name}):** {translated}")
                
                with st.spinner("Generating Audio..."):
                    audio = sarvam.synthesize(translated, lang_code=target_lang, voice=voice)
                    saved_path = sarvam.save_audio(audio, prefix=f"translate_{target_lang_name}")
                    st.audio(audio)
                    st.download_button("Download Audio", audio, os.path.basename(saved_path))
                    st.success(f"Done! Audio saved to `{os.path.basename(saved_path)}`")
            except Exception as e:
                st.error(f"Error: {e}")

# --- MODE 3: VOICE ASSISTANT ---
elif app_mode == "Voice Assistant (STT -> Translate -> TTS)":
    st.header("🤖 Voice Assistant (STT -> Translate -> TTS)")
    st.markdown("Record your voice, transcribe it, translate it, and play it back in another language.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Record Voice")
        audio_record = mic_recorder(
            start_prompt="Click to Record",
            stop_prompt="Stop Recording",
            just_once=True,
            key='recorder'
        )
        
        st.subheader("2. Settings")
        input_lang_name = st.selectbox("My Language", list(LANG_MAP.keys()), index=0)
        output_lang_name = st.selectbox("Target Language", list(LANG_MAP.keys()), index=1) # Default to Kannada
        
    with col2:
        if audio_record:
            st.audio(audio_record['bytes'])
            if st.button("Process Voice"):
                try:
                    # Step 1: STT
                    with st.spinner("Transcribing..."):
                        transcript = sarvam.speech_to_text(audio_record['bytes'], lang_code=LANG_MAP[input_lang_name])
                        if not transcript or not transcript.strip():
                            st.warning("Could not understand the audio. Please try recording again more clearly.")
                            st.stop()
                        st.write(f"**You said:** {transcript}")
                    
                    # Step 2: Translate if languages differ
                    if input_lang_name != output_lang_name:
                        with st.spinner(f"Translating to {output_lang_name}..."):
                            final_text = sarvam.translate(transcript, source_lang=LANG_MAP[input_lang_name], target_lang=LANG_MAP[output_lang_name])
                            if not final_text:
                                st.warning("Translation failed. Please try again.")
                                st.stop()
                            st.info(f"**Translation:** {final_text}")
                    else:
                        final_text = transcript
                    
                    # Step 3: TTS
                    with st.spinner("Generating Response Audio..."):
                        audio = sarvam.synthesize(final_text, lang_code=LANG_MAP[output_lang_name])
                        saved_path = sarvam.save_audio(audio, prefix=f"assistant_{output_lang_name}")
                        st.audio(audio)
                        st.download_button("Download Response", audio, os.path.basename(saved_path))
                        st.success(f"Complete! Audio saved to `{os.path.basename(saved_path)}`")
                        
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please record some audio first.")

# --- MODE 4: VOICE CLONING ---
elif app_mode == "Voice Cloning (Zero-Shot)":
    st.header("👥 Zero-Shot Voice Cloning")
    st.markdown("Provide a 5-10 second audio sample to clone any voice instantly.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Reference Voice")
        upload_type = st.radio("Reference Source", ["Record Now", "Upload File (.wav)"])
        
        ref_audio_bytes = None
        if upload_type == "Record Now":
            rec = mic_recorder(start_prompt="Record Reference Voice", stop_prompt="Stop Recording", just_once=True, key='clone_rec')
            if rec:
                ref_audio_bytes = rec['bytes']
        else:
            uploaded_file = st.file_uploader("Upload reference WAV", type=["wav"])
            if uploaded_file:
                ref_audio_bytes = uploaded_file.read()
                
        if ref_audio_bytes:
            st.audio(ref_audio_bytes)
            
    with col2:
        st.subheader("2. Synthesis Settings")
        clone_provider = st.selectbox("Cloning Provider", ["Fish Audio (Free Tier)", "Cartesia AI (Paid Tier)"])
        clone_text = st.text_area("Text to speak in cloned voice", placeholder="Enter the text you want the cloned voice to say...", height=120)
        
        if clone_provider == "Fish Audio (Free Tier)":
            ref_transcript = st.text_input("Reference Transcript (What is being said in the sample?)", placeholder="Optional but recommended for better quality")
            st.info("💡 **Fish Audio** provides a generous free tier for voice cloning.")
        else:
            clone_lang = st.selectbox("Language", ["en", "es", "fr", "de", "zh", "ja"], index=0)
            st.info("🚀 **Cartesia AI** offers ultra-low latency but requires a paid subscription for cloning.")
        
    if st.button("🎭 Clone and Synthesize"):
        if not ref_audio_bytes:
            st.error("Please provide a reference audio sample first!")
        elif not clone_text:
            st.error("Please enter the text to synthesize!")
        else:
            try:
                if clone_provider == "Fish Audio (Free Tier)":
                    with st.spinner("Fish Audio: Processing zero-shot clone..."):
                        client = FishAudioClient()
                        audio = client.synthesize_instant(
                            text=clone_text,
                            clip_bytes=ref_audio_bytes,
                            reference_text=ref_transcript if 'ref_transcript' in locals() else ""
                        )
                        saved_path = client.save_audio(audio, prefix="cloned_fish")
                        st.success(f"✅ Voice Cloned Successfully via Fish Audio! Saved to `{os.path.basename(saved_path)}`")
                else:
                    with st.spinner("Cartesia: Cloning voice..."):
                        client = CartesiaAudioClient()
                        
                        # Step 1: Clone the voice to get an ID
                        voice_id = client.clone_voice(
                            clip_bytes=ref_audio_bytes,
                            name=f"Clone_{int(time.time())}",
                            language=clone_lang
                        )
                        
                    with st.spinner("Cartesia: Generating audio..."):
                        # Step 2: Synthesize using the new voice ID
                        audio = client.synthesize(
                            text=clone_text,
                            voice_id=voice_id,
                            language=clone_lang
                        )
                        saved_path = client.save_audio(audio, prefix="cloned_cartesia")
                        st.success(f"✅ Voice Cloned Successfully via Cartesia! Saved to `{os.path.basename(saved_path)}`")
                
                st.audio(audio)
                st.download_button("Download Cloned Speech", audio, os.path.basename(saved_path))
            except Exception as e:
                st.error(f"Error: {e}")

# Footer
st.markdown("---")
st.markdown("Powered by **Sarvam AI** APIs for Indian Languages. Text translation model: `mayura:v1`, STT model: `saaras:v3`, TTS model: `bulbul:v3`.")
