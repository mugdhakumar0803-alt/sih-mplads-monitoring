# Dataset Inventory

Date: 2026-09-16
Status: Evidence-based repository audit only. No drive dataset files were present in the local workspace at the time of inspection, so this inventory covers all files that actually exist in the repository and any known external sources that remain unintegrated.

## Repository inventory

| Filename | Type | Size | Source | Description | Columns / attributes | Rows / pages | Date / year | Geographic coverage | Primary key / candidate identifier | Relevance | Classification | Recommended storage | Recommended table | Priority |
|---|---:|---:|---|---|---|---:|---|---|---|---|---|---|---|---|
| backend/app/ml/training/MPLADS.csv | CSV | 15.8 MB | MPLADS training dataset in repo | Real MPLADS work listing imported into the platform | MP NAME, WORK, CATEGORY, STATE, CONSTITUENCY, IDA, CITY, WARD, BLOCK, VILLAGE, RECOMMENDED DATE, ALLOCATION AMOUNT, IDA APPROVAL, STATUS, HOUSE | 60,359 | 2024+ | India, multi-state | MP NAME + WORK + STATE + CONSTITUENCY + RECOMMENDED DATE + allocation | High | A | data/raw/ | works | Must integrate |
| backend/app/ml/training/MPLADS 2.csv | CSV | 15.8 MB | Duplicate copy of same dataset | Duplicate same source, likely second copy during repo history | Same as above | 60,359 | 2024+ | India, multi-state | same as above | High | D | data/raw/duplicate/ | works | Reject |
| backend/app/ml/training/mplads_training_set.csv | CSV | 427 KB | ML training subset | Smaller derived ML dataset, not operational project master | 1 column, likely text or label | 8,660 | not explicit | not meaningful as geometry or governance data | text sample ID | Medium | C | data/processed/ml/ | training_samples | Optional |
| backend/app/ml/training/mplads_training_set 2.csv | CSV | 427 KB | Duplicate copy of ML training subset | Duplicate copy of the same training sample | same as above | 8,660 | not explicit | not meaningful | text sample ID | Medium | D | data/raw/duplicate/ | training_samples | Reject |
| backend/app/seed.py | Python script | tiny | local demo | Generates hardcoded demo users and works | username, role, work labels | N/A | N/A | demo only | generated IDs | Not operational | E | N/A | N/A | Reject |
| backend/app/seed_real_data.py | Python script | tiny | repo local ingestion script | Populates `works` table from real MPLADS CSV | imported rows, MP users, work IDs | N/A | N/A | India | work_id | High | B | data/processed/ingest/ | works | Useful reference |

## External sources known but not presently present in this workspace

| Source | Status | Evidence | Reason |
|---|---|---|---|
| Digital Sansad Lok Sabha MP info | Required, not present | Referenced in project requirements; no local export, script, or API snapshot found | Needs explicit ingestion from official source |
| DataMeet parliamentary shapefiles | Required, not present | No `.shp`, `.dbf`, `.prj`, `.shx`, or GeoJSON files found in workspace | GIS layer missing |
| State/district boundary shapefiles | Required, not present | No GIS boundary files found in workspace | Spatial validation missing |
| SC/ST reference data | Required, not present | No state/territory demographic files found locally | Compliance rules remain unverified |
| NDMA SACHET feeds | Required, optional external feed | Not in repo; no cached files found | Force-majeure assessment blocked |
| NASA EarthData / FRED | Optional or external reference | no local cache or script found | no direct integration |
| Drive folder files | Not visible in workspace | no files matching CSV/XLSX/PDF/SHP/etc. were found | no local drive inventory available yet |

## Classification summary

- A — MUST INTEGRATE: real MPLADS dataset in `backend/app/ml/training/MPLADS.csv`
- B — USEFUL REFERENCE: `seed_real_data.py` and import pipeline logic
- C — OPTIONAL: ML training subset files
- D — DUPLICATE: second copies of dataset files
- E — IRRELEVANT: demo seeding scripts not production data
- F — NEEDS HUMAN VERIFICATION: any future drive-exported files not yet inspected

## Recommended integration decision

The only dataset that warrants immediate ingestion is the repo’s real MPLADS CSV. Everything else in the current workspace is either a duplicate, an ML training sample, or a demo script. No GIS or financial datasets were discovered, and no authoritative MP master or boundary files are present locally.
