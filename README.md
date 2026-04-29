# Uptime Monitor

A website uptime monitoring system built with FastAPI, PostgreSQL, and HTMX.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set your DATABASE_URL
uvicorn app.main:app --reload
```

Tables are created automatically on first startup — no migration step needed.

Open http://localhost:8000 — dashboard auto-refreshes every 30 seconds.
Interactive API docs: http://localhost:8000/docs

## Log extraction API

```
GET /api/logs/
  ?website_id=1
  &from_dt=2024-01-01T00:00:00
  &to_dt=2024-01-31T23:59:59
  &is_up=false
  &limit=500
  &offset=0
```

## Project layout

app/
  main.py              — FastAPI app + scheduler setup
  core/config.py       — settings via .env
  db/base.py           — SQLAlchemy engine + session
  models/website.py    — Website + StatusLog ORM models
  schemas/website.py   — Pydantic schemas
  services/checker.py  — async HTTP checker
  services/stats.py    — uptime % calculation
  api/routes/
    websites.py        — CRUD + /api/websites/status
    logs.py            — /api/logs/ extraction endpoint
  templates/
    dashboard.html     — main page (HTMX polling)
    partials/status_cards.html — card grid partial
  static/css/style.css — dashboard styles
