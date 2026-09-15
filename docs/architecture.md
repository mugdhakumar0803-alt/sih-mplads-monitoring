# Architecture

The application uses a React/Vite frontend and a FastAPI/SQLAlchemy backend. The frontend calls backend APIs only; government CSVs are imported by `python -m app.data_pipeline` into PostgreSQL. Analytics, risk, compliance, grievance SLA, fund release, and chatbot retrieval operate on database records.

The platform distinguishes three sources:

- Government source data: work descriptions, locations, allocation, status, and dates present in the CSV.
- Platform-generated data: risk signals, anomaly ratios, duplicate candidates, SLA deadlines, and performance scores.
- User evidence: uploaded photos and citizen grievances.

Missing source fields remain null and are shown as unavailable.