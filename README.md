# Universal AI Voice Assistant (mimicAI)

A powerful, multi-provider AI Voice Assistant capable of **Text-to-Speech (TTS)**, **Translation**, **Speech-to-Text (STT)**, and **Zero-Shot Voice Cloning**. This project is optimized for deployment on **Vercel** and includes local support for **Apple Silicon (MLX)** models.

## 🚀 Key Features

-   **Web UI (FastAPI)**: A modern, responsive dashboard for interacting with all AI services.
-   **Multi-Provider TTS**: Integrated with **Sarvam AI**, **OpenRouter**, **Cartesia**, and **Fish Audio**.
-   **Voice Assistant**: Browser-based recording that transcribes, translates, and speaks back in a target language.
-   **Zero-Shot Voice Cloning**: Clone any voice instantly from a 5-10 second audio clip.
-   **Apple Silicon Optimized**: Local manager for running Qwen3-TTS models using Apple's MLX framework.

---

## ☁️ Deployment (Vercel)

This project is designed to be hosted on Vercel as a FastAPI application.

### 1. Environment Variables
You **must** configure the following environment variables in your Vercel Dashboard (**Settings > Environment Variables**):

| Key | Description |
|-----|-------------|
| `SARVAM_API_KEY` | Your API key from [Sarvam AI](https://www.sarvam.ai/) |
| `OPENROUTER_API_KEY` | Your API key from [OpenRouter](https://openrouter.ai/) |
| `CARTESIA_API_KEY` | Your API key from [Cartesia AI](https://cartesia.ai/) |
| `FISH_AUDIO_API_KEY` | Your API key from [Fish Audio](https://fish.audio/) |

### 2. Entry Point
Vercel uses `index.py` as the main entry point for the FastAPI application.

---

## 💻 Local Usage

### 1. Setup
```bash
git clone https://github.com/chiruchirag520/mimicAI.git
cd mimicAI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Web Interface
To run the FastAPI web server locally:
```bash
uvicorn index.py:app --reload
```
Open `http://127.0.0.1:8000` in your browser.

### 3. Local TTS (MLX / Apple Silicon)
To use the local MLX-powered TTS features (Qwen3-TTS):
```bash
pip install -r requirements-local.txt
python local_manager.py
```
*Note: This requires a Mac with M1/M2/M3/M4 chip.*

---

## 📂 Project Structure

-   `index.py`: Main FastAPI application and Web UI (optimized for Vercel).
-   `local_manager.py`: CLI manager for local MLX models.
-   `sarvam_tts.py`, `cartesia_tts.py`, etc.: Provider-specific client implementations.
-   `requirements.txt`: Lightweight dependencies for Vercel deployment.
-   `requirements-local.txt`: Heavy dependencies for local machine learning.

---

## 🛠️ Troubleshooting

-   **NoneType Error**: This usually means an API key is missing. Ensure all Environment Variables are set in Vercel.
-   **Push Blocked**: GitHub Push Protection prevents committing API keys. Always use Environment Variables or `.env` files (which are git-ignored).

---

**If this project helped you, please give it a ⭐ star!**
