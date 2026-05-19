"""
Fish Audio TTS Client (Free Tier Alternative)
"""
import os
import time
import requests
import msgpack
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
FISH_AUDIO_API_KEY = os.getenv("FISH_AUDIO_API_KEY")
FISH_AUDIO_BASE_URL = "https://api.fish.audio/v1"
OUTPUT_DIR = Path.cwd() / "outputs"

class FishAudioClient:
    """Client for Fish Audio TTS and Voice Cloning API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or FISH_AUDIO_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/msgpack"
        }

    def save_audio(self, audio_bytes: bytes, prefix: str = "fish") -> str:
        """Save audio bytes to file in the outputs directory"""
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"{prefix}_{timestamp}.mp3"
        
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        
        return str(output_path)

    def clone_voice(self, clip_bytes: bytes, name: str = "Cloned Voice", language: str = "en") -> str:
        """
        Create a persistent voice model from audio bytes and return the voice_id.
        In Fish Audio, this corresponds to creating a 'model'.
        """
        url = f"{FISH_AUDIO_BASE_URL}/model"
        
        # Fish Audio expects multipart for model creation usually, 
        # but let's see if we can use the simpler instant cloning 
        # by just returning the bytes as a 'pseudo' voice_id or similar.
        # Actually, for the 2-step flow in app.py, we'll create a model.
        
        files = {
            'voices': ('reference.wav', clip_bytes, 'audio/wav')
        }
        data = {
            'title': name,
            'visibility': 'private',
            'type': 'tts'
        }
        
        # We need to use multipart/form-data for model creation
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(url, headers=headers, files=files, data=data)
        
        if response.status_code != 201:
            # If model creation fails or is not allowed on free tier, 
            # we might want to fall back to instant cloning.
            # But for now, let's try model creation.
            raise RuntimeError(f"Fish Audio Cloning Error {response.status_code}: {response.text}")
            
        return response.json().get("id")

    def synthesize(
        self,
        text: str,
        voice_id: str,
        format: str = "mp3",
        latency: str = "normal"
    ) -> bytes:
        """
        Synthesize text to speech using a specific voice_id (model_id).
        """
        url = f"{FISH_AUDIO_BASE_URL}/tts"
        
        payload = {
            "text": text,
            "reference_id": voice_id,
            "format": format,
            "latency": latency
        }
        
        # Use msgpack for efficiency as supported by Fish Audio
        packed_data = msgpack.packb(payload)
        response = requests.post(url, headers=self.headers, data=packed_data)
        
        if response.status_code != 200:
            raise RuntimeError(f"Fish Audio Synthesis Error {response.status_code}: {response.text}")
            
        return response.content

    def synthesize_instant(
        self,
        text: str,
        clip_bytes: bytes,
        reference_text: str = "",
        format: str = "mp3"
    ) -> bytes:
        """
        One-step zero-shot cloning (Instant cloning).
        Best for free tier to avoid hitting model creation limits.
        """
        url = f"{FISH_AUDIO_BASE_URL}/tts"
        
        payload = {
            "text": text,
            "format": format,
            "references": [
                {
                    "audio": clip_bytes,
                    "text": reference_text
                }
            ]
        }
        
        packed_data = msgpack.packb(payload)
        response = requests.post(url, headers=self.headers, data=packed_data)
        
        if response.status_code != 200:
            raise RuntimeError(f"Fish Audio Instant Cloning Error {response.status_code}: {response.text}")
            
        return response.content
