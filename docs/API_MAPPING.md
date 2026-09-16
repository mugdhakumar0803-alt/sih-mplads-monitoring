# API Mapping

## Current API surface

| Area | Endpoint | Status |
|---|---|---|
| Auth | `/auth/login`, `/auth/register`, `/auth/logout` | Implemented |
| Works | `/works`, `/works/{work_id}` | Implemented |
| Dashboard | `/dashboard/summary`, `/dashboard/status-distribution` | Implemented |
| Compliance | `/compliance/check/{work_id}`, `/compliance/dashboard` | Implemented |
| AI | `/ai/duplicates`, `/ai/risk/{work_id}` | Partial |
| Photos | `/photos/verify`, `/photos/upload` | Partial |
| Grievances | `/grievances`, `/grievances/{id}` | Partial |
| Fund release | `/fund-release`, `/fund-release/{id}` | Partial |
| Ratings | `/ratings` | Partial |
| Chatbot | `/chatbot` | Partial |
| Leaderboard | `/leaderboard` | Partial |
| Alerts | `/alerts` | Partial |

## Missing API contracts

The following end-to-end APIs are not yet implemented against real data sources:
- GIS boundary APIs
- project GPS validation APIs
- MP master API
- district and state geometry APIs
- disaster feed APIs
- national-priority-area metadata API
- financial ledger APIs

Every API must be backed by live database queries or return a clear unavailable state. No screen should display fabricated values.
