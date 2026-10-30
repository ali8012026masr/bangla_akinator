# বাংলা জ্বিন (Bangla Akinator)

A probabilistic 20-questions guessing game for Bangladeshi and Bengali personalities, powered by Information Theory (Shannon Entropy), Bayesian inference with categorical likelihood models, and a curated crowd-learning loop.

## Tech Stack
- **Frontend:** Flutter (Android & Web) with Riverpod
- **Backend:** Python FastAPI & Uvicorn (async MongoDB driver)
- **Database:** MongoDB (Community Server / Atlas)
- **Typography:** Hind Siliguri / Noto Sans Bengali

## Repository Layout
```
bangla_akinator/
├── akinator_backend/     # Python FastAPI backend service
├── akinator_frontend/    # Flutter application
├── docs/                 # API contract, Data model, and Deployment guides
├── Docs/                 # Legacy notes and original planning documentation
├── AGENTS.md             # Coding instructions & architectural rules for AI agents
├── SPEC.md               # Technical specification
└── README.md             # This document
```

## Quick Start

### Prerequisites
- Python 3.11+
- Flutter SDK 3.x+
- MongoDB 7.0+ (running locally on port 27017 or remote Atlas URI)

### Backend Setup
```bash
cd akinator_backend
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
python scripts/seed_data.py
uvicorn app.main:app --reload --port 8000
```
Swagger API docs available at `http://localhost:8000/docs`.

### Frontend Setup
```bash
cd akinator_frontend
flutter pub get
flutter run -d chrome # Or run on Android emulator
```
