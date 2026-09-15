# SIH MPLADS Monitoring & Accountability Platform

AI-powered MPLADS Monitoring and Accountability Platform developed for Smart India Hackathon.

## Problem

The platform aims to improve transparency, monitoring, accountability and anomaly detection in MPLADS-funded development works.

## Core Features

- AI-powered anomaly detection
- Duplicate work detection
- Project delay analysis
- Deterministic compliance checking
- Citizen project tracking
- Citizen grievance management
- Official vs citizen discrepancy detection
- Photo verification
- Fund release monitoring
- Digital signatures and audit trail
- Authority performance scoring
- Citizen RAG assistant

## Technology Stack

### Frontend

- React
- JavaScript
- HTML
- CSS

### Backend

- FastAPI
- Python
- PostgreSQL
- PostGIS

### AI / ML

- Scikit-learn
- Sentence Transformers
- NLP
- Machine Learning

### Security

- JWT
- Role-Based Access Control
- Password Hashing
- Digital Signatures

### DevOps

- Docker
- GitHub Actions

## Project Structure

```text
backend/
├── app/
│   ├── models/
│   ├── schemas/
│   ├── auth/
│   ├── signing/
│   ├── routers/
│   ├── services/
│   └── ml/
│
├── tests/
├── requirements.txt
└── README.md

## Data-driven MVP workflow

Start PostgreSQL and Redis with `docker compose up -d postgres redis`, then run from `backend/`:

```bash
../.venv/bin/python -m app.migrate_schema
../.venv/bin/python -m app.data_pipeline app/ml/training/MPLADS.csv
uvicorn app.main:app --reload --port 8000
```

The importer detects encoding and delimiter, validates required columns, cleans dates and amounts, removes exact duplicates, upserts by source record identity, and prints actual import statistics. It does not invent expenditure, completion dates, coordinates, photos, compliance values, or risk values when the source does not provide them.

Run the frontend with `npm install && npm run dev` from `frontend/`. API documentation is available at `http://127.0.0.1:8000/docs`.

Government CSV values are stored with `source_dataset` and `source_record_id`. Risk scores, duplicate candidates, SLA deadlines, compliance results, and authority scores are platform-generated. Photos and grievances are user-generated evidence. The current MPLADS CSV does not contain reliable project GPS, uploaded photographs, or complete expenditure data; those fields are displayed as unavailable until supplied.

See `docs/IMPLEMENTATION_AUDIT.md`, `docs/data-pipeline.md`, `docs/ai-methodology.md`, and `docs/feature-traceability.md`.

### Docker-free local demo

When PostgreSQL is not available, run the backend against SQLite from the repository root:

```bash
DATABASE_URL=sqlite:////Users/nandini/Desktop/sih-mplads-monitoring/local-dev.db \
/Users/nandini/Desktop/sih-mplads-monitoring/.venv/bin/python -m uvicorn app.main:app \
	--app-dir /Users/nandini/Desktop/sih-mplads-monitoring/backend \
	--host 127.0.0.1 --port 8000 --loop asyncio
```

Import into the same database with the matching absolute `DATABASE_URL`, then open `http://127.0.0.1:5173/` for the Vite frontend.
