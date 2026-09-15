# Feature Traceability

| SIH capability | Backend | API | Frontend | Input/output |
|---|---|---|---|---|
| Real MPLADS ingestion | `app.data_pipeline` | Import CLI | Dashboard | Source CSV to `Work` rows |
| KPI dashboard | Dashboard router | `/dashboard/summary` | OverviewStats | Database work/status/allocation fields |
| Project details | Works router | `/works/{work_id}` | WorkDetail | Imported work and user evidence |
| Explainable risk | AI detection router | `/ai/risk/{work_id}` | WorkDetail | Peer amounts, dates, grievances, compliance |
| Cost anomaly | AI detection router | `/ai/cost-anomalies` | Analytics consumers | State/category peer allocation |
| Photo evidence | Photos router | `/photos/verify` | PhotoUpload | User-uploaded EXIF image |
| Grievance SLA | Grievance service/router | `/grievances/file`, `/grievances/run-sla-check` | Grievance panels | Project grievance and seven-day SLA |
| Compliance | Compliance router/engine | `/compliance/check/{work_id}` | ComplianceTracker | Work category and risk rules |
| Fund gate | Fund release service | `/fund-release/eligibility/{work_id}` | FundReleaseGate | Release, work, grievance, compliance records |
| Grounded assistant | Chatbot router | `/chatbot/ask` | ChatbotWidget | Retrieved database work/grievance/fund records |