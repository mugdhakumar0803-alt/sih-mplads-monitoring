# Data Pipeline

`backend/app/data_pipeline.py` reads source CSVs, detects encoding/delimiter, cleans footer/missing rows, parses dates and currency, derives transparent categories, removes exact duplicates, assigns deterministic source IDs, and upserts `Work` records.

Run:

```bash
DATABASE_URL=sqlite:////absolute/path/local-dev.db \
PYTHONPATH=backend .venv/bin/python -m app.data_pipeline backend/app/ml/training/MPLADS.csv
```

PostgreSQL is the deployment target; SQLite is supported for local Docker-free development. Import output reports rows read, imported, updated, skipped, and duplicates. Fields absent from the source stay null.
