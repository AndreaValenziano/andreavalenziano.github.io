#!/usr/bin/env bash
# Wrapper per risolvi2.py: crea il venv al primo avvio e lancia lo script.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"

# Serve Python >= 3.10: usa il più recente disponibile
PY=""
for cand in python3.13 python3.12 python3.11 python3.10 python3; do
    if command -v "$cand" >/dev/null 2>&1; then
        if "$cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
            PY="$cand"
            break
        fi
    fi
done
if [ -z "$PY" ]; then
    echo "⚠ Serve Python 3.10 o superiore (trovato: $(python3 --version 2>&1))" >&2
    exit 1
fi

if [ ! -d "$DIR/.venv" ]; then
    echo "Primo avvio: creo il virtualenv ($PY) e installo le dipendenze…"
    "$PY" -m venv "$DIR/.venv"
    "$DIR/.venv/bin/pip" install -q --upgrade pip
    "$DIR/.venv/bin/pip" install -q -r "$DIR/requirements.txt"
fi

exec "$DIR/.venv/bin/python" "$DIR/risolvi2.py" "$@"
