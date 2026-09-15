# Data Pipeline

Run from `backend/`:

```bash
../.venv/bin/python -m app.data_pipeline app/ml/training/MPLADS.csv
```

The importer detects encoding and delimiter, removes footer/empty rows, cleans amounts and dates, normalizes whitespace, derives a transparent category from work text, removes exact duplicates within a source, and upserts by deterministic source dataset/record identifiers. It prints read, imported, updated, skipped, and duplicate counts.

The current source CSV contains no reliable expenditure, sanction-date, completion-date, or project-GPS columns. Those values are not inferred by the importer.