from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import os
from sarvam_tts import SarvamAIClient
from tts_remote import RemoteTTSClient
from cartesia_tts import CartesiaAudioClient
from fish_tts import FishAudioClient

app = FastAPI(title="Universal AI Voice Assistant API")

# Initialize Clients
sarvam = SarvamAIClient()
remote = RemoteTTSClient()
cartesia = CartesiaAudioClient()
fish = FishAudioClient()

class TTSRequest(BaseModel):
    text: str
    provider: str = "sarvam" # sarvam, openrouter, cartesia, fish
    voice: Optional[str] = None
    lang_code: Optional[str] = "en-IN"
    speed: Optional[float] = 1.0

@app.get("/")
def read_root():
    return {"message": "Welcome to the Universal AI Voice Assistant API. Use /synthesize for TTS."}

@app.post("/synthesize")
async def synthesize(request: TTSRequest):
    try:
        if request.provider == "sarvam":
            audio = sarvam.synthesize(
                text=request.text, 
                lang_code=request.lang_code, 
                voice=request.voice or "shubh", 
                speed=request.speed
            )
            return Response(content=audio, media_type="audio/wav")
        
        elif request.provider == "openrouter":
            audio = remote.synthesize(
                text=request.text,
                voice=request.voice or "alloy",
                speed=request.speed
            )
            return Response(content=audio, media_type="audio/mp3")
        
        elif request.provider == "cartesia":
            if not request.voice:
                raise HTTPException(status_code=400, detail="Voice ID is required for Cartesia")
            audio = cartesia.synthesize(
                text=request.text,
                voice_id=request.voice
            )
            return Response(content=audio, media_type="audio/wav")
        
        elif request.provider == "fish":
            # For simplicity in API, we'll use a default voice or provided ID
            if not request.voice:
                 raise HTTPException(status_code=400, detail="Voice ID is required for Fish Audio")
            audio = fish.synthesize(
                text=request.text,
                voice_id=request.voice
            )
            return Response(content=audio, media_type="audio/mp3")
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {request.provider}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For Vercel, the variable 'app' is already exported at the top level.
