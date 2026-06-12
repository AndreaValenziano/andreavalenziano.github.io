@echo off
REM Wrapper Windows per risolvi2.py: crea il venv al primo avvio e lancia lo script.
setlocal
set DIR=%~dp0

if not exist "%DIR%.venv" (
    echo Primo avvio: creo il virtualenv e installo le dipendenze...
    py -m venv "%DIR%.venv" || python -m venv "%DIR%.venv"
    "%DIR%.venv\Scripts\pip" install -q -r "%DIR%requirements.txt"
)

"%DIR%.venv\Scripts\python" "%DIR%risolvi2.py" %*
endlocal
