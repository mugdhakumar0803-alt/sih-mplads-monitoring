# Required Datasets and Honest Fallbacks

| Dataset needed | Why | Required columns | Current availability | Fallback |
|---|---|---|---|---|
| MP master | Stable MP identity, house, term, constituency mapping | mp_id, name, house, state, constituency, term | Missing | Use source MP text; mark identity uncertain |
| Expenditure/payments | Utilization and financial anomaly | work_id, sanctioned_amount, expenditure_amount, date | Missing | Show `Data unavailable`; do not calculate utilization |
| District/constituency map | Hierarchical citizen/official scoping | state, district, constituency, normalized IDs | Partial text only | Use normalized source constituency/state |
| Project coordinates | GPS/photo and map verification | work_id, latitude, longitude | Missing | Return cannot verify location |
| SC/ST reference | Statutory allocation checks | area, designation, population/eligible allocation | Missing | Return not computable |
| Disaster/calamity | Fair delay attribution | district, event type, start, end | Optional module only | Show force-majeure verification unavailable |
| Official evidence index | Evidence freshness and verification | work_id, photo/evidence ID, capture time | User-generated only | Show no verified evidence |
| Satellite provider | Satellite verification | provider credentials, coordinates, imagery | Not configured | Show satellite verification not configured |
