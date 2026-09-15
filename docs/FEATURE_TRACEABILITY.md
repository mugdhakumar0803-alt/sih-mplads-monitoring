# Feature Traceability

| SIH requirement | Data source | Backend | API | Frontend/role | Missing behavior |
|---|---|---|---|---|---|
| Real works | MPLADS CSV -> Work | data pipeline/WorkService | `/works` | registry/details/all roles | server returns empty state |
| MP scoping | authenticated User constituency/source identity | scope/query filters | `/works`, `/dashboard/summary` | MP dashboard | no assignment means no private works |
| Risk | allocation peers, dates, grievances, compliance | AI router | `/ai/risk/{id}` | project details/officials | unavailable signals omitted |
| GPS evidence | user-uploaded photo EXIF | photo router | `/photos/verify` | project details | cannot verify without GPS/project coordinates |
| Grievance SLA | user grievance + Work | grievance service | `/grievances/*` | citizen/official dashboards | timeline records breach |
| Ratings | citizen + completed Work | RatingService | `/ratings` | citizen/project/leaderboard | unfinished/duplicate rating blocked |
| Performance | Work/grievance/compliance evidence | leaderboard service | `/leaderboard/*` | state/MP/district views | unavailable components disclosed |
