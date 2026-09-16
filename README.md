# SIH MPLADS Monitoring & Accountability Platform

## Repository status

This repository is a strong foundation for an MPLADS monitoring platform, but it is not yet a complete end-to-end, fully data-backed implementation.

The current evidence shows:
- one real MPLADS project dataset is present in [backend/app/ml/training/MPLADS.csv](backend/app/ml/training/MPLADS.csv)
- no authoritative GIS shapefiles, MP master export, or financial ledger were found in the local workspace
- the application uses database-backed patterns, but missing datasets must remain explicitly unavailable rather than fabricated

## Exact setup commands

### 1. Frontend

```bash
cd /Users/somyatiwari/Desktop/sih-mplads-monitoring/frontend
npm install
npm run build
npm run dev -- --host 0.0.0.0 --port 5173
```

### 2. Backend (local venv)

```bash
cd /Users/somyatiwari/Desktop/sih-mplads-monitoring/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the API

```bash
cd /Users/somyatiwari/Desktop/sih-mplads-monitoring/backend
source .venv/bin/activate
export DATABASE_URL=sqlite:////Users/somyatiwari/Desktop/sih-mplads-monitoring/local-dev.db
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Import the real MPLADS CSV

```bash
cd /Users/somyatiwari/Desktop/sih-mplads-monitoring/backend
source .venv/bin/activate
python -m app.data_pipeline app/ml/training/MPLADS.csv
```

### 5. Docker stack

```bash
cd /Users/somyatiwari/Desktop/sih-mplads-monitoring
docker compose up -d postgres redis
```

Then run the backend and frontend using the configured environment variables from `.env.example`.

## Core principles

- never invent GPS coordinates
- never invent expenditure or sanctions
- never invent MP identity or constituency geometry
- never invent disaster events
- never fabricate citizen ratings or evidence
- if a dataset is missing, expose an explicit unavailable state

## Main repo contents

- backend: FastAPI, SQLAlchemy, ML modules, models, routers
- frontend: React + Vite app
- docs: audit and dataset documentation
- data: raw and processed data directories

## Audit documents

The repository audit and gap analysis are stored in:
- [docs/DEEP_REPOSITORY_AUDIT.md](docs/DEEP_REPOSITORY_AUDIT.md)
- [docs/DATASET_INVENTORY.md](docs/DATASET_INVENTORY.md)
- [docs/REQUIRED_DATASETS.md](docs/REQUIRED_DATASETS.md)
- [docs/DATA_GAP_REPORT.md](docs/DATA_GAP_REPORT.md)
- [docs/GIS_DATASET_AUDIT.md](docs/GIS_DATASET_AUDIT.md)
- [docs/DATA_LINEAGE.md](docs/DATA_LINEAGE.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/API_MAPPING.md](docs/API_MAPPING.md)
- [docs/ML_PIPELINE.md](docs/ML_PIPELINE.md)
- [docs/DEMO_FLOW.md](docs/DEMO_FLOW.md)
- [docs/FEATURE_GAP_REPORT.md](docs/FEATURE_GAP_REPORT.md)
- [docs/FINAL_IMPLEMENTATION_STATUS.md](docs/FINAL_IMPLEMENTATION_STATUS.md)

## Current project status

The current implementation is partial and data-limited, not complete. It can support a real data-import foundation, but it cannot claim full end-to-end GIS, financial, MP, or disaster functionality without the missing datasets.
