# Project Guidelines — Bangla Akinator (বাংলা জ্বিন)

## Tech Stack
- **Frontend:** Flutter (Dart) — Android primary, Flutter Web secondary for development
- **Backend:** Python 3.11+ with FastAPI & Uvicorn
- **Database:** MongoDB (using Motor / PyMongo Async driver)
- **State Management:** Flutter Riverpod (strict, no Provider)
- **Typography:** Google Fonts — Hind Siliguri / Noto Sans Bengali

## Coding Rules
- Do NOT install unapproved third-party dependencies without review.
- Keep components modular — separate repositories, services, schemas, and endpoints.
- Never write entire features into a single monolithic file.
- All Bangla text MUST use proper Unicode (UTF-8). Never use ASCII transliteration or mojibake.
- All API responses must specify `utf-8` charset support for Bengali text.
- Use `async/await` consistently across backend database and network operations; never block the event loop.
- Validate all incoming API inputs using strict Pydantic models.
- Always run automated tests and linting (`pytest` for backend, `flutter analyze` for frontend) before considering a task done.
- Use clear, descriptive English variable and function names with inline docstrings explaining scoring math.

## Architectural Boundaries
- Backend layers:
  - `app/api/`: Routing (`router.py`) and schemas (`schemas.py`)
  - `app/core/`: Configuration (`config.py`), DB lifespan (`database.py`), errors, and logging
  - `app/models/`: Domain enums and data types (`domain.py`)
  - `app/repositories/`: Pure database access (`characters.py`, `questions.py`, `sessions.py`)
  - `app/services/`: Pure business logic (`game_engine.py`, `question_selection.py`, `contribution_service.py`)
- Frontend layers:
  - `lib/core/`: App configuration, Bengali theme, error types
  - `lib/models/`: Domain models and immutable state models
  - `lib/repositories/`: Remote API clients
  - `lib/providers/`: Riverpod state notifiers
  - `lib/screens/`: UI views
  - `lib/widgets/`: Reusable UI components
- All runtime credentials and environment options must reside in `.env` (never commit real credentials).
- The frontend API base URL must be configurable at build time (e.g. via `--dart-define=API_BASE_URL=...`).

## Testing & Quality Gates
- Game engine tests must be isolated and testable without a live database.
- Unit tests must cover all 5 answer values (`YES`, `PROBABLY_YES`, `UNKNOWN`, `PROBABLY_NO`, `NO`).
- Seed data must be verified using `validate_seed_data.py`.
- No task is complete without passing its corresponding phase acceptance gate.
