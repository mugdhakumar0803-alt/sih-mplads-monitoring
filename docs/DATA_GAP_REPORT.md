# Data Gap Report

This report answers the explicit data-availability questions required for the MPLADS monitoring platform.

## Availability status definitions

- AVAILABLE: verified in repo or from real source wiring
- PARTIAL: partly present but incomplete or not enough for the required use case
- MISSING: not currently available in the workspace or not yet ingested

## Core questions

| # | Requirement | Status | Why |
|---|---|---|---|
| 1 | MPLADS project/work data? | AVAILABLE | Verified real project rows exist in `backend/app/ml/training/MPLADS.csv`. |
| 2 | Sanction amount? | PARTIAL | The CSV contains `ALLOCATION AMOUNT`, not necessarily the same as official sanction amount, and no separate sanction ledger is present. |
| 3 | Expenditure? | MISSING | No expenditure or payment ledger exists in repo. `expenditure_amount` is nullable and no source file provides it. |
| 4 | Payments? | MISSING | No payment or installment ledger exists locally. |
| 5 | Utilization? | MISSING | Utilization can only be computed if release/expenditure data is present; currently it is not. |
| 6 | Work progress? | PARTIAL | Some status is present (`STATUS` field), but no actual progress percentage or milestone data appears in the real CSV. |
| 7 | Project status? | PARTIAL | `STATUS` is present, but no authoritative project lifecycle stages or completion metrics are included. |
| 8 | Implementing agency? | MISSING | No implementing agency table or source field is available in the repo. |
| 9 | Contractor information? | MISSING | No contractor master or contracts dataset is present. |
| 10 | Project latitude? | MISSING | No GPS/lat/longitude columns are present in the real CSV. |
| 11 | Project longitude? | MISSING | Same as above; no coordinate columns exist. |
| 12 | Geo-tagged evidence? | MISSING | No user photos or project GPS evidence were found in the repo. |
| 13 | MP master? | MISSING | No canonical MP master table or downloaded Digital Sansad export is present. |
| 14 | Parliamentary constituency geometry? | MISSING | No `.shp`, `.geojson`, or table data was found. |
| 15 | District geometry? | MISSING | No district shapefile or boundary dataset was found. |
| 16 | State geometry? | MISSING | No state boundary dataset was found in repository. |
| 17 | SC allocation/work data? | MISSING | No SC-specific work or demographic allocation dataset is present. |
| 18 | ST allocation/work data? | MISSING | Same as above; no ST-specific allocation or category evidence present. |
| 19 | National-priority-area data? | MISSING | No authoritative dataset or reference layer found. |
| 20 | Disaster data? | MISSING | No disaster feed or cached dataset found in repo. |
| 21 | Historical disaster data? | MISSING | No historical event database or archive is in local workspace. |
| 22 | Construction/material price data? | MISSING | No price index or material-cost dataset discovered. |
| 23 | Citizen grievances? | PARTIAL | Database models exist, but no real grievance records or source catalog were found in repo. |
| 24 | Citizen ratings? | PARTIAL | Database model exists, but no real citizen ratings dataset or integration is present. |
| 25 | Satellite data/provider? | MISSING | No satellite data source, provider key, or image verification module is configured. |

## Explanation by category

### Real data that exists
- MPLADS work records, including title, state, constituency, allocation amount, and recommended date
- Demo scripts and user roles for local testing
- Backend database model scaffolding for works, grievances, fund releases, ratings, and audits

### Real data that does not exist yet
- Taxpayer-funded expenditure data
- Project GPS
- MP master and constituency codes
- District/state GIS geometry
- SC/ST compliance datasets
- National-priority-area layers
- Disaster records and force-majeure feed
- Photo evidence
- Real citizen grievances and ratings

## Result

The repository is not yet a complete, data-backed monitoring platform. It has a solid data model and import pipeline for the MPLADS source CSV, but the spatial, financial, demographic, and evidence layers remain missing. The correct behavior is to preserve an explicit `UNAVAILABLE` state rather than fabricating values.
