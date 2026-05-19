"""
Cartesia AI TTS Client
"""
import os
import time
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")
CARTESIA_BASE_URL = "https://api.cartesia.ai"
OUTPUT_DIR = Path.cwd() / "outputs"

class CartesiaAudioClient:
    """Client for Cartesia AI TTS and Voice Cloning API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or CARTESIA_API_KEY
        self.headers = {
            "Cartesia-Version": "2024-06-10",
            "Authorization": f"Bearer {self.api_key}"
        }

    def save_audio(self, audio_bytes: bytes, prefix: str = "cartesia") -> str:
        """Save audio bytes to file in the outputs directory"""
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"{prefix}_{timestamp}.wav"
        
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        
        return str(output_path)

    def clone_voice(self, clip_bytes: bytes, name: str = "Cloned Voice", language: str = "en") -> str:
        """
        Clone a voice from audio bytes and return the voice_id.
        """
        url = f"{CARTESIA_BASE_URL}/voices/clone"
        
        files = {
            'clip': ('reference.wav', clip_bytes, 'audio/wav')
        }
        data = {
            'name': name,
            'language': language
        }
        
        # Note: We don't set Content-Type for multipart requests as requests handles it
        response = requests.post(url, headers=self.headers, files=files, data=data)
        
        if response.status_code != 200:
            raise RuntimeError(f"Cartesia Cloning Error {response.status_code}: {response.text}")
            
        return response.json().get("id")

    def synthesize(
        self,
        text: str,
        voice_id: str,
        model_id: str = "sonic-latest",
        language: str = "en",
        sample_rate: int = 44100
    ) -> bytes:
        """
        Synthesize text to speech using a specific voice_id.
        Returns the full audio bytes (non-streaming for simplicity in this integration).
        """
        url = f"{CARTESIA_BASE_URL}/tts/bytes"
        
        payload = {
            "model_id": model_id,
            "transcript": text,
            "voice": {
                "mode": "id",
                "id": voice_id
            },
            "output_format": {
                "container": "wav",
                "encoding": "pcm_f32le",
                "sample_rate": sample_rate
            },
            "language": language
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            raise RuntimeError(f"Cartesia Synthesis Error {response.status_code}: {response.text}")
            
        return response.content
