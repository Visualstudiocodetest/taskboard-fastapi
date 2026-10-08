# TaskBoard

Small task-management backend (projects containing tasks) with a minimal web front end.
Made for the "Projet Backend : sujet libre" assignment.

## Stack and why
- **FastAPI**: automatic validation, clear error codes, free docs at `/docs`.
- **SQLAlchemy + PyMySQL / MySQL**: relational data (project 1—N tasks) with a real foreign key and cascade delete.
- **Pydantic**: input validation (lengths, priority 1–3, blank strings rejected).
- **Vanilla HTML/JS** front end served by the API (`static/index.html`), no build step.

## Architecture
Layered, with dependencies pointing inward (routers -> services -> repositories -> DB):
- `routers/`: HTTP only (parse request, call a service, return a response).
- `services.py`: business rules; raises domain errors (`exceptions.py`), never `HTTPException`.
- `repositories.py`: all SQL (Repository pattern); list queries use one JOIN instead of N+1.
- `dependencies.py`: dependency injection that builds service + repositories per request.
- `main.py`: app wiring and the single mapping from domain errors to HTTP status codes.

SOLID: each layer has one responsibility (S); new error types or routers are added without editing existing code (O);
services depend on repository interfaces so they can be tested with fakes (`tests/test_services.py`) (D).

## Setup
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
mysql -uroot -p -e "CREATE DATABASE taskboard; CREATE DATABASE taskboard_test;"
.venv/bin/uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000 (UI) or http://127.0.0.1:8000/docs (API docs).
Copy `.env.example` to `.env` and fill in your MySQL credentials (`DATABASE_URL`, `TEST_DATABASE_URL`). `.env` is git-ignored.
Tables are created automatically at startup.

## Endpoints
| Method | Path | Notes |
|---|---|---|
| GET/POST | `/api/projects` | list / create (409 on duplicate name) |
| GET/PUT/DELETE | `/api/projects/{id}` | full CRUD; delete cascades to tasks |
| GET/POST | `/api/projects/{id}/tasks` | list (`?done=true/false`, `limit`, `offset`) / create |
| PATCH/DELETE | `/api/tasks/{id}` | partial update / delete |

Errors: 404 unknown id, 409 duplicate project name, 422 invalid data.

## Tests
```bash
.venv/bin/python -m pytest
```
Uses the separate `taskboard_test` database (wiped on each test).

## AI usage
Claude Code (Anthropic) generated the first version of this code from the assignment PDF.
I must read and understand every file before the oral defence.
