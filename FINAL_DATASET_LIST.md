# Final Dataset List — SIH26102 MPLADS Platform

Every dataset checked in this chat, sorted by what to actually do with it.

## ✅ ADD NOW — verified real, ready to ingest as-is

| # | Dataset | Rows | What it gives you |
|---|---|---|---|
| 1 | `MPLADS.csv` (already in repo) | 60,359 | Core work-level dataset — already ingested |
| 2 | `mp_master_18th_lok_sabha.csv` (built from your `All_Members.pdf`) | 544 | Current MP roster: name, party, constituency, state, status, terms — **fills the biggest gap that existed** |
| 3 | `mplads_fund_utilization_15thLS.csv` | 509 | MP-term fund entitlement/release/expenditure, 2009–2014, ₹ crore |
| 4 | `mplads_adr_prs_15thls.csv` | 509 | Same + legislator conduct data (attendance, criminal cases) — keep the conduct columns separate from financial ones |
| 5 | `india_pc_2019_boundaries.geojson` | 543 | Real constituency polygons — needs PostGIS added first to actually use |
| 6 | `historical_mplads_state_finance.csv` (from IJIRMF paper) | 37 | State-wise fund release/expenditure, FY2016-17 baseline |
| 7 | `historical_mplads_yearly_finance.csv` (from IJIRMF paper) | 24 | Year-wise fund release, 1993-94 to 2016-17 |
| 8 | `historical_mplads_state_works.csv` (from IJIRMF paper) | 27 | State-wise work count/cost, as of June 2019 |
| 9 | `historical_mplads_sector_works.csv` (from IJIRMF paper) | 14 | Category-wise work count/cost, as of June 2019 |

## ⚠️ ADD AS CITED CONTEXT ONLY — real, but not MPLADS-specific or not tabular

| Dataset | Why it can't be a compliance data source | Use it for |
|---|---|---|
| `sc_population_by_state_census2011.csv` | Census 2011, population % ≠ MPLADS allocation | State demographic context only, label as 2011 data |
| BehanBox article + NCDHR `DABA-2025-1.pdf` | Union Budget SC/ST sub-plan data, not MPLADS | A cited stat on the compliance dashboard (e.g. "nationally only ~4.5% of SC budget is targeted schemes — NCDHR 2026") |
| MoSPI EnviStats 2025, Component 4 | Real, current, official — but its actual figures are chart images, not extractable tables; also national-level only | Cited narrative stats (e.g. "lightning caused 2,887 deaths nationally in 2022") on a disaster-context panel, not a `disaster_events` table |

## ❌ DO NOT ADD — checked and rejected

| Dataset | Why rejected |
|---|---|
| `esakshi_geotagged_works_sample.csv` | Looks fabricated — sequential IDs, round numbers, no source URL. Never wire into a real dashboard |
| Kaggle "global natural calamities dataset" (`archive.zip`, NASA EONET) | 98.6% wildfires, ~15 genuine India events out of 5,393 rows, no severity/admin fields — wrong shape for force-majeure |

## 🕓 STILL NOT FOUND — genuinely required, not yet supplied by any link so far

- Official MPLADS fund/expenditure/UC-AC data at work level (the MPLADS portal itself, not yet confirmed bulk-downloadable)
- Reliable per-work GPS coordinates
- Real MPLADS-specific SC/ST allocation evidence (as opposed to general population % or Union Budget sub-plan data)
- Authoritative national-priority-area definition
- Historical, state+district+date-level disaster records suitable for matching individual project delays (the 13-row "Amount consented for Calamity" dataset your original blueprint mentioned, if you can locate it, or NCRB's primary "Accidental Deaths and Suicides in India" tables)
- Construction/material cost index (WPI, CPWD SOR, or state PWD SOR — not yet sourced)

## What to actually do tonight

Ingest rows 1–9 from the first table — that's your real, verified, ready
dataset stack. Cite the three "context only" sources where relevant on the
UI. Leave the "not found" items as an honest roadmap slide rather than
guessing at them.
