#!/bin/bash
# Heizlast-Rechentool Web-GUI starten
# ====================================

cd "$(dirname "$0")"

echo "Starte Heizlast Web-GUI..."
echo ""
echo "Die Web-GUI ist erreichbar unter: http://localhost:8000"
echo "Drücke Strg+C zum Beenden."
echo ""

# Prüfe ob Paket installiert ist
if ! pip show heizlast-12831 > /dev/null 2>&1; then
    echo "Installiere Paket..."
    pip install -e .
fi

# Browser öffnen (falls möglich)
if command -v xdg-open &> /dev/null; then
    sleep 2 && xdg-open "http://localhost:8000" &
elif command -v open &> /dev/null; then
    sleep 2 && open "http://localhost:8000" &
fi

# Server starten
python3 -m uvicorn heizlast.web.app:app --reload --host 0.0.0.0 --port 8000
