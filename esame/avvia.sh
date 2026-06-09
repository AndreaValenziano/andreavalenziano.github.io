#!/usr/bin/env bash
# avvia.sh — Wrapper che imposta DYLD_LIBRARY_PATH per il bug libexpat su macOS
# e poi esegue risolvi.py con tutti gli argomenti passati.
#
# Uso (backend Claude — default, richiede ANTHROPIC_API_KEY):
#   ./esame/avvia.sh --immagini ./img --materia quizgrammatica
#   ./esame/avvia.sh --immagini ./img --materia quizdidattica --modello sonnet
#
# Uso (backend Ollama — locale, gratuito, nessun rate limit):
#   ./esame/avvia.sh --immagini ./img --materia quizgrammatica --backend ollama
#   ./esame/avvia.sh --immagini ./img --materia quizdidattica --backend ollama
#
# Pre-requisiti Ollama (una tantum):
#   ollama pull qwen2.5:7b          # già presente
#   ollama pull nomic-embed-text    # modello embedding (~270 MB)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export DYLD_LIBRARY_PATH="/opt/homebrew/opt/expat/lib:${DYLD_LIBRARY_PATH:-}"

exec "${SCRIPT_DIR}/.venv/bin/python3" "${SCRIPT_DIR}/risolvi.py" "$@"
