"""
Remote TTS wrapper using OpenRouter API
Designed for low-spec Windows/Linux machines that want cloud-based synthesis
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/audio/speech"
DEFAULT_MODEL = "openai/gpt-audio"  # Fast and reliable
DEFAULT_VOICE = "alloy"
DEFAULT_FORMAT = "mp3"  # mp3 or pcm
OUTPUT_DIR = Path.cwd() / "outputs"


class RemoteTTSClient:
    """Client for OpenRouter text-to-speech API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
             # If still not found, check the .env file explicitly just in case
             self.api_key = os.getenv("OPENROUTER_API_KEY")
    
    def synthesize(
        self,
        text: str,
        model: str = DEFAULT_MODEL,
        voice: str = DEFAULT_VOICE,
        response_format: str = DEFAULT_FORMAT,
        speed: float = 1.0,
        reference_audio_b64: Optional[str] = None,
    ) -> bytes:
        """
        Synthesize text to speech using OpenRouter API
        
        Args:
            text: Text to synthesize
            model: OpenRouter TTS model ID
            voice: Voice identifier
            response_format: Audio format (mp3, pcm)
            speed: Playback speed multiplier
            reference_audio_b64: Optional base64 encoded audio for zero-shot cloning
        
        Returns:
            Audio bytes
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        if len(text) > 4096:
            text = text[:4096]
        
        payload = {
            "input": text,
            "model": model,
            "voice": voice if not reference_audio_b64 else "custom",
            "response_format": response_format,
            "speed": speed,
        }
        
        # Support zero-shot cloning for models that support it (like Mistral Voxtral)
        if reference_audio_b64:
            payload["provider"] = {
                "reference_audio": reference_audio_b64
            }
        
        req = self._build_request(payload)
        return self._send_request(req)
    
    def _build_request(self, payload: dict) -> urllib.request.Request:
        """Build HTTP request to OpenRouter"""
        data = json.dumps(payload).encode("utf-8")
        return urllib.request.Request(
            self.base_url,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "RemoteTTS-Client/1.0",
            },
        )
    
    def _send_request(self, req: urllib.request.Request) -> bytes:
        """Send request and handle response"""
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                content_type = resp.headers.get("Content-Type", "").lower()
                raw = resp.read()
                
                if "audio/" in content_type or "application/octet-stream" in content_type:
                    return raw
                
                if "application/json" in content_type:
                    try:
                        error = json.loads(raw.decode("utf-8", errors="ignore"))
                        msg = error.get("message", error.get("error", str(error)))
                    except Exception:
                        msg = raw.decode("utf-8", errors="ignore")
                    raise RuntimeError(f"API returned JSON (not audio): {msg}")
                
                if "text/html" in content_type:
                    raise RuntimeError("API returned HTML instead of audio. Likely an incorrect endpoint or 404.")
                
                raise RuntimeError(f"Unexpected content type: {content_type}")
        
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="ignore")
            try:
                error_json = json.loads(error_body)
                msg = error_json.get("message", error_json.get("error", str(error_json)))
            except Exception:
                msg = error_body
            raise RuntimeError(f"HTTP {exc.code}: {msg}") from exc
        except Exception as exc:
            raise RuntimeError(f"Unexpected error: {exc}") from exc
    
    def save_audio(self, audio_bytes: bytes, output_path: Optional[str] = None) -> str:
        """Save audio bytes to file"""
        if output_path is None:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = OUTPUT_DIR / f"tts_{timestamp}.mp3"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        
        return str(output_path)
