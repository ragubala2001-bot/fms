# AI Translator — Enterprise Translation Platform

A fully working, enterprise-grade AI translation platform powered by OpenAI API, built with Django, Django Channels, and WebSockets.

## Features

- **Realtime Text Translation** — Stream translations live as you type, ChatGPT-style
- **Auto Language Detection** — Automatically detects source language using OpenAI
- **100+ Languages** — Full support with searchable dropdown (native + English names)
- **Voice Translation** — Microphone input with live speech-to-text and translation
- **File Translation** — PDF, DOCX, PPTX, XLSX, TXT, CSV, JSON, XML, HTML, Markdown, SRT
- **OCR Image Translation** — Extract text from images and translate using OpenAI Vision
- **Zero Storage** — Privacy-first: nothing is stored, everything processes in-memory
- **Premium UI** — Glassmorphism design inspired by DeepL, ChatGPT, Linear, Vercel

## Tech Stack

- **Backend:** Django 6, Django REST Framework, Django Channels, Redis, WebSocket
- **AI Engine:** OpenAI API (GPT-4o-mini for translation, detection, OCR)
- **Frontend:** Django Templates, Tailwind CSS (CDN), Vanilla JavaScript
- **Realtime:** WebSocket streaming with Django Channels + Redis

## Quick Start

### Prerequisites

- Python 3.10+
- Redis server
- OpenAI API key

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd fms

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export REDIS_URL="redis://localhost:6379/0"

# Run migrations
python manage.py migrate

# Start Redis (in another terminal)
redis-server

# Run the server with Daphne (ASGI)
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

Then open http://localhost:8000 in your browser.

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Main translator UI |
| `/api/languages/` | GET | List all supported languages |
| `/api/detect/` | POST | Detect language of text |
| `/api/translate/` | POST | Translate text (non-streaming) |
| `/api/translate/file/` | POST | Translate uploaded file |
| `/api/file/preview/` | POST | Preview file content |
| `/api/ocr/translate/` | POST | OCR extract + translate image |
| `/ws/translate/` | WebSocket | Realtime streaming translation |

## Architecture

```
translator/
├── services/
│   ├── openai_service.py    # OpenAI API integration
│   ├── file_service.py      # File processing & translation
│   ├── ocr_service.py       # OCR image processing
│   └── language_data.py     # 100+ language definitions
├── consumers.py             # WebSocket consumers
├── views.py                 # REST API views
├── serializers.py           # DRF serializers
├── urls.py                  # URL routing
├── routing.py               # WebSocket routing
└── templates/translator/
    └── index.html           # Premium UI
```

## Privacy

Zero storage architecture — no database tables, no file storage, no translation history. All data processes in-memory and is discarded after the response.
