# Windows (PowerShell) setup script for OpenRouter TTS
# Run: .\setup.ps1 sk-or-v1-YOUR_API_KEY

param(
    [string]$ApiKey
)

if (-not $ApiKey) {
    Write-Host ""
    Write-Host "========================================================================"
    Write-Host " OpenRouter TTS - Windows Setup"
    Write-Host "========================================================================"
    Write-Host ""
    Write-Host "Usage: .\setup.ps1 YOUR_OPENROUTER_API_KEY"
    Write-Host ""
    Write-Host "Example:"
    Write-Host "  .\setup.ps1 sk-or-v1-YOUR_KEY_HERE"
    Write-Host ""
    Write-Host "Get your API key from: https://openrouter.ai/keys"
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "========================================================================"
Write-Host " OpenRouter TTS - Windows Setup"
Write-Host "========================================================================"
Write-Host ""

# [1] Set environment variable
Write-Host "[1/4] Setting environment variable for this session..."
$env:OPENROUTER_API_KEY = $ApiKey
[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", $ApiKey, "User") | Out-Null
Write-Host "       ✓ API key configured (persistent in user environment)"

# [2] Create outputs directory
Write-Host "[2/4] Creating outputs directory..."
if (-not (Test-Path "outputs")) {
    New-Item -ItemType Directory -Path "outputs" -Force | Out-Null
}
Write-Host "       ✓ outputs/ ready"

# [3] Test connection
Write-Host "[3/4] Testing OpenRouter connection..."
try {
    python -c "from tts_remote import RemoteTTSClient; c = RemoteTTSClient(); print('       ✓ Connection successful')" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Connection test failed"
    }
} catch {
    Write-Host "       ✗ Connection test failed (check API key?)"
    exit 1
}

# [4] Run demo
Write-Host "[4/4] Running demo TTS synthesis..."
try {
    python tts_remote.py --text "OpenRouter TTS is working on Windows" --format mp3 | Out-Null
} catch {
    Write-Host "       ✗ Demo synthesis failed"
    exit 1
}
Write-Host "       ✓ Demo synthesis complete"

Write-Host ""
Write-Host "========================================================================"
Write-Host " Setup complete!"
Write-Host "========================================================================"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Try: python tts_remote.py --text 'Your text here'"
Write-Host "  2. Or:  python tts_remote.py --help"
Write-Host "  3. Check outputs/ folder for generated audio files"
Write-Host ""
Write-Host "To use in your own code:"
Write-Host "  from tts_remote import RemoteTTSClient"
Write-Host "  client = RemoteTTSClient()"
Write-Host "  audio = client.synthesize(`'Hello world`')"
Write-Host "  output_path = client.save_audio(audio)"
Write-Host ""
