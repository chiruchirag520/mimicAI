"""
Sarvam AI TTS, Translation, and STT Client
"""
import json
import os
import time
import base64
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configuration
SARVAM_BASE_URL = "https://api.sarvam.ai"
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
DEFAULT_VOICE = "shubh"
DEFAULT_LANG = "en-IN"
OUTPUT_DIR = Path.cwd() / "outputs"


class SarvamAIClient:
    """Unified client for Sarvam AI services"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or SARVAM_API_KEY
        self.base_url = SARVAM_BASE_URL
    
    def synthesize(
        self,
        text: str,
        lang_code: str = DEFAULT_LANG,
        voice: str = DEFAULT_VOICE,
        speed: float = 1.0,
        sample_rate: int = 24000
    ) -> bytes:
        """Text-to-Speech"""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        payload = {
            "text": text,
            "target_language_code": lang_code,
            "speaker": voice,
            "model": "bulbul:v3",
            "speech_sample_rate": sample_rate,
            "pace": speed
        }
        
        req = self._build_request("/text-to-speech", payload)
        
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                response_json = json.loads(resp.read().decode("utf-8"))
                if "audios" in response_json and response_json["audios"]:
                    return base64.b64decode(response_json["audios"][0])
                raise RuntimeError("Unexpected response format from TTS API")
        except Exception as exc:
            raise RuntimeError(f"Sarvam TTS error: {exc}")

    def translate(
        self,
        text: str,
        source_lang: str = "en-IN",
        target_lang: str = "hi-IN",
        mode: str = "formal"
    ) -> str:
        """Text Translation"""
        if not text or not text.strip():
            return ""
            
        payload = {
            "input": text,
            "source_language_code": source_lang,
            "target_language_code": target_lang,
            "model": "mayura:v1",
            "mode": mode
        }
        
        req = self._build_request("/translate", payload)
        
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                response_json = json.loads(resp.read().decode("utf-8"))
                return response_json.get("translated_text", "")
        except Exception as exc:
            raise RuntimeError(f"Sarvam Translation error: {exc}")

    def speech_to_text(
        self,
        audio_content: bytes,
        lang_code: Optional[str] = None,
        mode: str = "transcribe"
    ) -> str:
        """Speech-to-Text (Transcription or Translation to English)"""
        # Using multipart/form-data for audio file upload
        from requests_toolbelt import MultipartEncoder
        import requests

        url = f"{self.base_url}/speech-to-text"
        
        fields = {
            'file': ('audio.wav', audio_content, 'audio/wav'),
            'model': 'saaras:v3',
            'mode': mode
        }
        if lang_code:
            fields['language_code'] = lang_code
            
        m = MultipartEncoder(fields=fields)
        
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": m.content_type,
            "User-Agent": "SarvamAI-Client/1.0"
        }
        
        try:
            response = requests.post(url, data=m, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("transcript", "")
        except Exception as exc:
            raise RuntimeError(f"Sarvam STT error: {exc}")

    def save_audio(self, audio_bytes: bytes, prefix: str = "sarvam") -> str:
        """Save audio bytes to file in the outputs directory"""
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"{prefix}_{timestamp}.wav"
        
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        
        return str(output_path)

    def _build_request(self, endpoint: str, payload: Dict[str, Any]) -> urllib.request.Request:
        data = json.dumps(payload).encode("utf-8")
        return urllib.request.Request(
            f"{self.base_url}{endpoint}",
            data=data,
            headers={
                "api-subscription-key": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": "SarvamAI-Client/1.0",
            },
        )
