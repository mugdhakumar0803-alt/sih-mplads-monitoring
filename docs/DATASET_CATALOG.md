# Dataset Catalog

Audited on 2026-09-15.

## `backend/app/ml/training/MPLADS.csv`

- Physical rows: 60,360 including header; 60,359 data rows.
- Separator: semicolon.
- Columns: `MP NAME`, `WORK`, `CATEGORY`, `STATE`, `CONSTITUENCY`, `IDA`, `CITY`, `WARD`, `BLOCK`, `VILLAGE`, `RECOMMENDED DATE`, `ALLOCATION AMOUNT`, `IDA APPROVAL`, `STATUS`, `HOUSE`.
- Observed lifecycle values include `Unsanctioned`, `Sanctioned`, `Ongoing`, and `Completed`.
- Available: MP text, work description, state, constituency, locality text, recommendation date, allocation, IDA approval, status, house.
- Missing/unreliable: stable government work ID, expenditure, sanctioned amount, completion date, project GPS, explicit district in the header, SC/ST designation, disaster linkage.
- Used by: work ingestion, dashboard status/allocation metrics, category normalization, peer cost analysis, project search, MP/state scoping.

## `backend/app/ml/training/MPLADS 2.csv`

- Physical rows: 60,360 including header; 60,359 data rows.
- Same header and structure as `MPLADS.csv`; treated as a separate source candidate and not blindly merged.
- Used by: comparative source audit only until a reliable record join is configured.

## `mplads_training_set.csv` and `mplads_training_set 2.csv`

- 8,660 data rows each plus header.
- Columns: `work_id`, `cost_ratio_vs_category_median`, `progress_vs_elapsed_time_ratio`, `days_since_last_photo`, `citizen_grievance_count`.
- These are derived training artifacts, not government source data. Photo/grievance columns are synthetic in the training builder and must not be presented as observed evidence.

## Required joins and coverage

No reliable expenditure, MP master, district mapping, SC/ST allocation, calamity, coordinates, or satellite datasets are present in the audited repository. The importer preserves `source_dataset` and deterministic `source_record_id`; unmatched fields remain null.
