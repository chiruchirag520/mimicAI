from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import Response, HTMLResponse
from pydantic import BaseModel
from typing import Optional
import os
import base64
from sarvam_tts import SarvamAIClient
from tts_remote import RemoteTTSClient
from cartesia_tts import CartesiaAudioClient
from fish_tts import FishAudioClient

app = FastAPI(title="Universal AI Voice Assistant")

# Initialize Clients
sarvam = SarvamAIClient()
remote = RemoteTTSClient()
cartesia = CartesiaAudioClient()
fish = FishAudioClient()

# --- HTML Frontend ---
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Universal AI Voice Assistant</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <style>
        :root {
            --primary: #4361ee;
            --secondary: #3f37c9;
            --bg: #f8f9fa;
            --card-bg: #ffffff;
            --text: #2b2d42;
        }
        body { background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; padding-top: 2rem; }
        .container { max-width: 900px; }
        .card { border: none; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-bottom: 2rem; }
        .nav-pills .nav-link { color: var(--text); border-radius: 10px; padding: 0.8rem 1.5rem; margin-right: 0.5rem; }
        .nav-pills .nav-link.active { background-color: var(--primary); }
        .btn-primary { background-color: var(--primary); border: none; padding: 0.8rem 2rem; border-radius: 10px; }
        .btn-primary:hover { background-color: var(--secondary); }
        .status-badge { font-size: 0.8rem; padding: 0.4rem 0.8rem; border-radius: 20px; }
        #audio-preview { width: 100%; margin-top: 1rem; }
        .spinner-border { width: 1.5rem; height: 1.5rem; display: none; }
        .recording-pulse {
            width: 12px; height: 12px; background: red; border-radius: 50%;
            display: inline-block; margin-right: 8px; animation: pulse 1s infinite;
            display: none;
        }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="text-center mb-5">
            <h1>🎙️ Universal AI Voice Assistant</h1>
            <p class="text-muted">Powered by Sarvam AI, OpenRouter, Cartesia & Fish Audio</p>
        </div>

        <ul class="nav nav-pills mb-4 justify-content-center" id="pills-tab" role="tablist">
            <li class="nav-item">
                <button class="nav-link active" id="pills-tts-tab" data-bs-toggle="pill" data-bs-target="#pills-tts">TTS Direct</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="pills-translate-tab" data-bs-toggle="pill" data-bs-target="#pills-translate">Translate & Speak</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="pills-assistant-tab" data-bs-toggle="pill" data-bs-target="#pills-assistant">Voice Assistant</button>
            </li>
            <li class="nav-item">
                <button class="nav-link" id="pills-clone-tab" data-bs-toggle="pill" data-bs-target="#pills-clone">Voice Cloning</button>
            </li>
        </ul>

        <div class="tab-content" id="pills-tabContent">
            <!-- TTS Direct -->
            <div class="tab-pane fade show active" id="pills-tts">
                <div class="card p-4">
                    <h3>🔊 Text-to-Speech</h3>
                    <div class="mb-3">
                        <label class="form-label">Enter Text</label>
                        <textarea id="tts-text" class="form-control" rows="4" placeholder="Type something..."></textarea>
                    </div>
                    <div class="row g-3 mb-4">
                        <div class="col-md-6">
                            <label class="form-label">Provider</label>
                            <select id="tts-provider" class="form-select">
                                <option value="sarvam">Sarvam AI (Free)</option>
                                <option value="openrouter">OpenRouter (Remote)</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Language / Voice</label>
                            <select id="tts-voice" class="form-select">
                                <option value="en-IN:shubh">English (Shubh)</option>
                                <option value="hi-IN:shubh">Hindi (Shubh)</option>
                                <option value="kn-IN:shubh">Kannada (Shubh)</option>
                                <option value="alloy">OpenRouter: Alloy</option>
                                <option value="nova">OpenRouter: Nova</option>
                            </select>
                        </div>
                    </div>
                    <button onclick="generateTTS()" class="btn btn-primary">
                        <span class="spinner-border spinner-border-sm" id="tts-spinner"></span>
                        Generate Audio
                    </button>
                    <div id="tts-result" class="mt-3"></div>
                </div>
            </div>

            <!-- Translate & Speak -->
            <div class="tab-pane fade" id="pills-translate">
                <div class="card p-4">
                    <h3>🌐 Translate & Speak</h3>
                    <div class="mb-3">
                        <label class="form-label">English Text</label>
                        <textarea id="trans-text" class="form-control" rows="4" placeholder="Type in English..."></textarea>
                    </div>
                    <div class="row g-3 mb-4">
                        <div class="col-md-6">
                            <label class="form-label">Translate To</label>
                            <select id="trans-lang" class="form-select">
                                <option value="hi-IN">Hindi</option>
                                <option value="kn-IN">Kannada</option>
                                <option value="bn-IN">Bengali</option>
                                <option value="ta-IN">Tamil</option>
                                <option value="te-IN">Telugu</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Voice Gender</label>
                            <select id="trans-voice" class="form-select">
                                <option value="shubh">Male (Shubh)</option>
                                <option value="ritu">Female (Ritu)</option>
                            </select>
                        </div>
                    </div>
                    <button onclick="translateAndSpeak()" class="btn btn-primary">
                        <span class="spinner-border spinner-border-sm" id="trans-spinner"></span>
                        Translate & Play
                    </button>
                    <div id="trans-result" class="mt-3"></div>
                </div>
            </div>

            <!-- Voice Assistant -->
            <div class="tab-pane fade" id="pills-assistant">
                <div class="card p-4 text-center">
                    <h3>🤖 Voice Assistant</h3>
                    <p>Record your voice to transcribe and translate</p>
                    <div class="mb-4">
                        <button id="record-btn" class="btn btn-outline-danger btn-lg rounded-circle p-4">
                            <i class="bi bi-mic-fill"></i>
                        </button>
                        <div class="mt-2">
                            <span class="recording-pulse"></span>
                            <span id="record-status">Click to start recording</span>
                        </div>
                    </div>
                    <div class="row g-3 mb-4 text-start">
                        <div class="col-md-6">
                            <label class="form-label">Input Language</label>
                            <select id="ast-in-lang" class="form-select">
                                <option value="en-IN">English</option>
                                <option value="hi-IN">Hindi</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Output Language</label>
                            <select id="ast-out-lang" class="form-select">
                                <option value="kn-IN">Kannada</option>
                                <option value="hi-IN">Hindi</option>
                                <option value="en-IN">English</option>
                            </select>
                        </div>
                    </div>
                    <div id="ast-result" class="mt-3 text-start"></div>
                </div>
            </div>

            <!-- Voice Cloning -->
            <div class="tab-pane fade" id="pills-clone">
                <div class="card p-4">
                    <h3>🎭 Zero-Shot Voice Cloning</h3>
                    <div class="mb-3">
                        <label class="form-label">Reference Audio (.wav)</label>
                        <input type="file" id="clone-file" class="form-control" accept=".wav">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Text to speak</label>
                        <textarea id="clone-text" class="form-control" rows="3" placeholder="What should the cloned voice say?"></textarea>
                    </div>
                    <div class="mb-4">
                        <label class="form-label">Provider</label>
                        <select id="clone-provider" class="form-select">
                            <option value="fish">Fish Audio (Free)</option>
                            <option value="cartesia">Cartesia AI (Paid)</option>
                        </select>
                    </div>
                    <button onclick="cloneVoice()" class="btn btn-primary">
                        <span class="spinner-border spinner-border-sm" id="clone-spinner"></span>
                        Clone & Synthesize
                    </button>
                    <div id="clone-result" class="mt-3"></div>
                </div>
            </div>
        </div>
        
        <footer class="text-center mt-5 mb-5 text-muted">
            <hr>
            <p>Integrated Translation, STT, and TTS System</p>
        </footer>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Helper to show audio
        function displayAudio(containerId, blob, filename) {
            const url = URL.createObjectURL(blob);
            const container = document.getElementById(containerId);
            container.innerHTML = `
                <div class="alert alert-success mt-3">
                    <strong>Success!</strong> Audio generated.
                    <audio controls id="audio-preview" class="mt-2" src="${url}"></audio>
                    <a href="${url}" download="${filename}" class="btn btn-sm btn-outline-success mt-2">Download ${filename}</a>
                </div>
            `;
        }

        // --- TTS Direct ---
        async function generateTTS() {
            const text = document.getElementById('tts-text').value;
            const provider = document.getElementById('tts-provider').value;
            const voiceVal = document.getElementById('tts-voice').value;
            const spinner = document.getElementById('tts-spinner');
            
            if(!text) return alert("Enter text");
            
            spinner.style.display = 'inline-block';
            try {
                const [lang, voice] = voiceVal.includes(':') ? voiceVal.split(':') : [null, voiceVal];
                const res = await fetch('/synthesize', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        text, provider, 
                        voice: voice,
                        lang_code: lang || 'en-IN'
                    })
                });
                if(!res.ok) throw new Error(await res.text());
                const blob = await res.blob();
                displayAudio('tts-result', blob, 'speech.wav');
            } catch(e) {
                document.getElementById('tts-result').innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
            } finally {
                spinner.style.display = 'none';
            }
        }

        // --- Translate & Speak ---
        async function translateAndSpeak() {
            const text = document.getElementById('trans-text').value;
            const targetLang = document.getElementById('trans-lang').value;
            const voice = document.getElementById('trans-voice').value;
            const spinner = document.getElementById('trans-spinner');

            if(!text) return alert("Enter text");
            
            spinner.style.display = 'inline-block';
            try {
                const res = await fetch('/translate-speak', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        text, target_lang: targetLang, voice
                    })
                });
                if(!res.ok) throw new Error(await res.text());
                const data = await res.json();
                
                // Show translation text
                let resultHtml = `<div class="alert alert-info"><strong>Translation:</strong> ${data.translated_text}</div>`;
                document.getElementById('trans-result').innerHTML = resultHtml;
                
                // Fetch audio
                const audioRes = await fetch(`/get-audio/${data.audio_id}`);
                const blob = await audioRes.blob();
                
                const url = URL.createObjectURL(blob);
                const audioDiv = document.createElement('div');
                audioDiv.innerHTML = `<audio controls class="w-100 mt-2" src="${url}" autoplay></audio>`;
                document.getElementById('trans-result').appendChild(audioDiv);
            } catch(e) {
                document.getElementById('trans-result').innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
            } finally {
                spinner.style.display = 'none';
            }
        }

        // --- Voice Assistant (Recording) ---
        let mediaRecorder;
        let audioChunks = [];
        const recordBtn = document.getElementById('record-btn');
        const recordStatus = document.getElementById('record-status');
        const pulse = document.querySelector('.recording-pulse');

        recordBtn.onclick = async () => {
            if (mediaRecorder && mediaRecorder.state === "recording") {
                mediaRecorder.stop();
                recordBtn.classList.replace('btn-danger', 'btn-outline-danger');
                recordStatus.innerText = "Processing...";
                pulse.style.display = 'none';
            } else {
                audioChunks = [];
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
                mediaRecorder.onstop = processAssistantVoice;
                mediaRecorder.start();
                recordBtn.classList.replace('btn-outline-danger', 'btn-danger');
                recordStatus.innerText = "Recording... Click to Stop";
                pulse.style.display = 'inline-block';
            }
        };

        async function processAssistantVoice() {
            const blob = new Blob(audioChunks, { type: 'audio/wav' });
            const inLang = document.getElementById('ast-in-lang').value;
            const outLang = document.getElementById('ast-out-lang').value;
            
            const formData = new FormData();
            formData.append('file', blob);
            formData.append('in_lang', inLang);
            formData.append('out_lang', outLang);

            try {
                const res = await fetch('/assistant', {
                    method: 'POST',
                    body: formData
                });
                if(!res.ok) throw new Error(await res.text());
                const data = await res.json();
                
                document.getElementById('ast-result').innerHTML = `
                    <div class="card p-3 bg-light">
                        <p><strong>You said:</strong> ${data.transcript}</p>
                        <p><strong>Translated:</strong> ${data.translation}</p>
                        <audio controls class="w-100" src="data:audio/wav;base64,${data.audio_b64}" autoplay></audio>
                    </div>
                `;
                recordStatus.innerText = "Click to start recording";
            } catch(e) {
                document.getElementById('ast-result').innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
                recordStatus.innerText = "Error. Try again.";
            }
        }

        // --- Voice Cloning ---
        async function cloneVoice() {
            const fileInput = document.getElementById('clone-file');
            const text = document.getElementById('clone-text').value;
            const provider = document.getElementById('clone-provider').value;
            const spinner = document.getElementById('clone-spinner');

            if(!fileInput.files[0] || !text) return alert("Select a file and enter text");

            spinner.style.display = 'inline-block';
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('text', text);
            formData.append('provider', provider);

            try {
                const res = await fetch('/clone', {
                    method: 'POST',
                    body: formData
                });
                if(!res.ok) throw new Error(await res.text());
                const blob = await res.blob();
                displayAudio('clone-result', blob, 'cloned_speech.wav');
            } catch(e) {
                document.getElementById('clone-result').innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
            } finally {
                spinner.style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

# --- API Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def get_index():
    return HTML_CONTENT

class TTSRequest(BaseModel):
    text: str
    provider: str = "sarvam"
    voice: Optional[str] = None
    lang_code: Optional[str] = "en-IN"
    speed: Optional[float] = 1.0

@app.post("/synthesize")
async def synthesize(request: TTSRequest):
    try:
        if request.provider == "sarvam":
            audio = sarvam.synthesize(request.text, lang_code=request.lang_code, voice=request.voice or "shubh")
            return Response(content=audio, media_type="audio/wav")
        else:
            audio = remote.synthesize(request.text, voice=request.voice or "alloy")
            return Response(content=audio, media_type="audio/mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class TranslateRequest(BaseModel):
    text: str
    target_lang: str
    voice: str

# In-memory store for audio (since Vercel is stateless)
audio_store = {}

@app.post("/translate-speak")
async def translate_speak(request: TranslateRequest):
    try:
        # Translate
        translated = sarvam.translate(request.text, target_lang=request.target_lang)
        
        # Synthesize
        audio = sarvam.synthesize(translated, lang_code=request.target_lang, voice=request.voice)
        
        audio_id = str(len(audio_store) + 1)
        audio_store[audio_id] = audio
        
        return {
            "translated_text": translated,
            "audio_id": audio_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-audio/{audio_id}")
async def get_audio(audio_id: str):
    if audio_id in audio_store:
        return Response(content=audio_store[audio_id], media_type="audio/wav")
    raise HTTPException(status_code=404, detail="Audio not found")

@app.post("/assistant")
async def assistant(file: UploadFile = File(...), in_lang: str = Form(...), out_lang: str = Form(...)):
    try:
        audio_bytes = await file.read()
        
        # STT
        transcript = sarvam.speech_to_text(audio_bytes, lang_code=in_lang)
        
        # Translate
        final_text = transcript
        if in_lang != out_lang:
            final_text = sarvam.translate(transcript, source_lang=in_lang, target_lang=out_lang)
            
        # TTS
        audio = sarvam.synthesize(final_text, lang_code=out_lang)
        
        return {
            "transcript": transcript,
            "translation": final_text,
            "audio_b64": base64.b64encode(audio).decode('utf-8')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clone")
async def clone(file: UploadFile = File(...), text: str = Form(...), provider: str = Form(...)):
    try:
        audio_bytes = await file.read()
        
        if provider == "fish":
            audio = fish.synthesize_instant(text=text, clip_bytes=audio_bytes)
            return Response(content=audio, media_type="audio/mp3")
        else:
            voice_id = cartesia.clone_voice(clip_bytes=audio_bytes)
            audio = cartesia.synthesize(text=text, voice_id=voice_id)
            return Response(content=audio, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For Vercel, the variable 'app' is the entry point
