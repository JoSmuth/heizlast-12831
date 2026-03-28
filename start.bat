@echo off
REM Heizlast-Rechentool Web-GUI starten
REM ================================

cd /d "%~dp0"

echo Starte Heizlast Web-GUI...
echo.
echo Die Web-GUI oeffnet sich automatisch im Browser.
echo Druecke Strg+C zum Beenden.
echo.

REM Pruefe ob Paket installiert ist
pip show heizlast-12831 >nul 2>&1
if errorlevel 1 (
    echo Installiere Paket...
    pip install -e .
)

REM Browser oeffnen (nach kurzem Delay)
start "" "http://localhost:8000"

REM Server starten
python -m uvicorn heizlast.web.app:app --reload --host 0.0.0.0 --port 8000

pause
