# Deep Repository Audit

Date: 2026-09-15
Scope: existing SIH26102 repository, including backend, frontend, ML modules, database models, CSVs, and API integrations.

## Feature Matrix

| Feature | Current implementation | Data source/database | API/frontend | Status | Missing/fix |
|---|---|---|---|---|---|
| Auth | JWT login/register, bcrypt passwords, approval checks | `users`, `revoked_tokens`, audit logs | `/auth/*`, Login/Register | Real, previously SQLite UUID bug fixed | Add profile-scoped state/district onboarding |
| Works | SQLAlchemy `Work`, CSV importer, source IDs | MPLADS CSV -> `works` | `/works`, WorksRegistry, WorkDetail | Real source data | Add server search, pagination metadata, citizen/MP scope |
| Dashboard | Status/allocation/risk/grievance summary | `works`, grievances, releases | `/dashboard/summary` | Real but scope-aware work needed | Add all chart endpoints and role scope |
| CSV ingestion | Encoding/delimiter detection, cleaning, dedupe, upsert | `app.data_pipeline` | CLI | Real | Add import-run persistence and multi-file join reporting |
| Risk | Peer cost, age/status, duplicate similarity, grievances, compliance signals | `works`, grievances | `/ai/risk/{work_id}` | Calculated and explainable | Persist assessments and expose scoped alerts |
| Cost anomaly | Peer median allocation | `works` | `/ai/cost-anomalies` | Real where allocation peers exist | Expenditure anomaly unavailable without expenditure source |
| Delay | Basic date helper; source has recommendation dates only | `works` | Partial | Honest limitation needed | Do not label delayed without completion/expected-duration evidence |
| Duplicate detection | Text similarity grouped by state/category/constituency | work descriptions | `/ai/duplicates`, risk endpoint | Candidate-only | Persist clusters and reasons |
| Photo evidence | EXIF GPS, timestamp input, SHA-256 duplicate check, distance | uploaded photo + `photos` | `/photos/verify`, PhotoUpload | Real user evidence | Add size/type limits and project GPS import source |
| Grievances | Work validation, status, SLA deadline/history, escalation runner | `grievances`, `works` | `/grievances/*` | Real workflow | Add category schema, evidence, event notifications |
| Ratings | Five-factor rating and unique citizen/work constraint | `ratings`, `users`, `works` | `/ratings/` | Partial | Require completed work; add work/MP rating reads |
| MP leaderboard | Existing ratings-only endpoint and separate system score router | ratings or works/users | `/ratings/leaderboard`, `/leaderboard` | Confusing/overlapping | Replace with three explicit system leaderboards; ratings separate |
| Compliance | Deterministic category/risk checks | work fields | `/compliance/*` | Partial | SC/ST percentages unavailable without reference dataset |
| Fund release | Eligibility uses completion, utilization, grievances, compliance | releases/works/grievances | `/fund-release/*` | Real but expenditure unavailable | Show unavailable evidence rather than zero-as-fact |
| Chatbot | Keyword retrieval of work records plus grievance/fund counts | works/grievances/releases | `/chatbot/*`, ChatbotWidget | Grounded but basic | Add scoped state/MP retrieval and explicit no-match |
| Alerts/notifications | No first-class alert model/service | none | no complete API | Missing | Add persisted platform alert records |
| Satellite | No provider abstraction in current runtime | none | none | Missing | Return unconfigured, never fake verification |

## Mock/Synthetic Findings

- `seed.py` creates development-only accounts and three demo works; it is not the government data source.
- `ml/training/seed_from_dataful.py` creates synthetic photo/grievance training features. These must never be shown as government measurements.
- `ml/anomaly.py` has deterministic random state for reproducible model training and a manual synthetic test block; this is not production dashboard data.
- Existing analytics/compliance code had stale fields/static values and is being replaced with database queries.
- Frontend charts are API-backed in structure, but several endpoints/components still target stale fields or lack loading/empty/error states.

## Integration Gaps

1. `Work` has source provenance but no import-run table or full joined expenditure source.
2. CSV has no reliable expenditure, project GPS, completion date, SC/ST designation, or disaster reference fields.
3. Citizens currently call the generic works endpoint; state/district profile filters are not consistently enforced.
4. MP scope must use normalized constituency/source MP identity, not only ID columns that are absent from imported rows.
5. Official system performance must be separated from citizen satisfaction ratings.
6. Alerts, state/district leaderboards, rating read APIs, and scheduled SLA execution need completion.

## Verified API Surfaces

`/auth`, `/works`, `/photos`, `/grievances`, `/fund-release`, `/ai`, `/compliance`, `/chatbot`, `/dashboard`, `/ratings`, `/leaderboard`, `/api/analytics`, `/audit`.

## Verified Frontend Surfaces

Landing, Login, Register, Citizen, MP, District, State, Ministry, Analytics, WorkDetail; shared work registry, overview, charts, chatbot, compliance, grievances, fund release, photo verification, escalation.
