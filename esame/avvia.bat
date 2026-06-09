@echo off
REM avvia.bat — Launcher Windows per risolvi.py (equivalente di avvia.sh su macOS).
REM Usa il virtualenv in esame\.venv; nessuna variabile d'ambiente macOS necessaria.
REM
REM Uso (backend Ollama — locale, offline, nessun costo):
REM   esame\avvia.bat --immagini quizdidattica\screen_esame --materia quizdidattica --backend ollama --modello qwen2.5:14b --top-k 8
REM
REM Uso (backend Claude — richiede ANTHROPIC_API_KEY):
REM   esame\avvia.bat --immagini quizdidattica\screen_esame --materia quizdidattica
REM   esame\avvia.bat --immagini quizdidattica\screen_esame --materia quizdidattica --modello sonnet
REM
REM Pre-requisiti Ollama (una tantum):
REM   ollama pull qwen2.5:14b       :: modello chat principale (~9 GB VRAM)
REM   ollama pull nomic-embed-text  :: modello embedding (~300 MB)

"%~dp0.venv\Scripts\python.exe" "%~dp0risolvi.py" %*
