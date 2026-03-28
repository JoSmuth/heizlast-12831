# heizlast-12831

Heizlastberechnung nach DIN EN 12831-1 / DIN/TS 12831-1.

## Features

- **Transmissionswärmeverluste** (inkl. Erdreich, Wärmebrücken)
- **Lüftungswärmeverluste** (Infiltration, Anlagen, WRG)
- **Zeitkonstante und Temperaturkorrektur** nach DIN EN 12831-1
- **Aufheizzuschlag** für schnelle Aufheizung
- **Web-GUI** für interaktive Berechnungen
- **CLI** für automatisierte Berechnungen

## Installation

### Mit pip

```bash
pip install heizlast-12831
```

### Mit virtualenv (empfohlen)

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
pip install -e ".[web]"
```

## Schnellstart

### Windows: Doppelklick auf `start.bat`

Die Web-GUI startet automatisch und öffnet den Browser unter http://localhost:8000

### Linux/Mac: `./start.sh`

```bash
chmod +x start.sh
./start.sh
```

## Start-Varianten

| Methode | Befehl | Beschreibung |
|---------|--------|--------------|
| **Doppelklick (Windows)** | `start.bat` | Einfachster Weg für Windows |
| **Doppelklick (Linux/Mac)** | `./start.sh` | Einfachster Weg für Unix |
| **Make** | `make start` | Startet Web-GUI mit Hot-Reload |
| **CLI Entry Point** | `heizlast-web` | Nach pip install verfügbar |
| **Python Module** | `python -m uvicorn heizlast.web.app:app --reload` | Volle Kontrolle |
| **Docker** | `docker build -t heizlast . && docker run -p 8000:8000 heizlast` | Container-Deployment |

## CLI verwenden

```bash
heizlast calculate examples/wolfsburg_efh.json
```

## Entwicklung

### Tests ausführen

```bash
make test        # Alle Tests
make test-cov    # Tests mit Coverage-Report
```

### Paket installieren

```bash
make install     # Installiert alle Dependencies
```

### Aufräumen

```bash
make clean
```

## Docker

```bash
docker build -t heizlast-12831 .
docker run -p 8000:8000 heizlast-12831
```

## Lizenz

MIT
