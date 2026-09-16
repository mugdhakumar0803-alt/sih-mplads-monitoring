# IJIRMF Paper + MoSPI EnviStats — Verification & What I Extracted

## 1. IJIRMF 2019 paper — real, and I extracted its 4 tables into CSVs

Confirmed real: a peer-reviewed comparative study of MPLADS vs SAGY
(Baldaniya & Bhoye, 2019), citing the real MPLADS Annual Report 2016-17 and
the official MPLADS portal's work-summary report (as on 13 June 2019). I
pulled all four of its data tables directly out of the PDF text — not
estimated, the actual published numbers — into four ready CSVs (attached):

- **`historical_mplads_state_finance.csv`** — 37 states/UTs + total: funds
  released, amount available, recommended, sanctioned, % sanctioned,
  expenditure, % utilised, unspent balance (all ₹ crore), as of MPLADS
  Annual Report 2016-17.
- **`historical_mplads_yearly_finance.csv`** — year-wise allocation, funds
  released, and cumulative release, 1993-94 through 2016-17.
- **`historical_mplads_state_works.csv`** — 27 states/UTs + total: sanctioned
  work cost (₹ lakh) and number of works sanctioned, as on 13 June 2019.
- **`historical_mplads_sector_works.csv`** — 14 work categories (drinking
  water, education, roads, sanitation, etc.) with sanctioned cost and work
  count, same date.

**Use these exactly as the earlier dataset plan describes** — as
`historical_mplads_*` baseline tables, kept separate from your live `Work`
table, for trend/baseline context (e.g. "state's historical utilization
rate vs. current"), not as current figures. Note the small inherent
inconsistency in the source paper itself: Table 3's total is 72,991 works
worth ₹2,828.7 crore while Table 4's total is 75,549 works worth ₹2,919.0
crore — the paper doesn't reconcile this, so carry both totals as-is rather
than picking one to "fix" the other.

## 2. MoSPI EnviStats India 2025, Component 4 — real, but no downloadable table data

This is genuine, current (2025) official government statistics — Ministry
of Statistics & Programme Implementation, sourced from IMD and NCRB's
"Accidental Deaths and Suicides in India 2022." It's a much better-quality
disaster source than the Kaggle EONET file I flagged earlier: it has
**heat wave/cold wave days by state (2010–2024)**, **year-wise deaths,
cattle loss, house damage, and cropped-area damage from natural extreme
events**, and **deaths by cause — lightning, heat stroke, floods,
cyclones, earthquakes, epidemics (2017–2022)**.

**The catch:** the actual data tables (Statements 4.01, 4.02, 4.06, 4.08)
are rendered as **charts/figures in the PDF, not extractable text tables**
— I could only pull the narrative numbers mentioned in the surrounding
text (e.g. peak lightning deaths: 2,887 in 2022; highest human toll:
5,677 deaths in 2013-14; highest cropped-area damage: 114.30 lakh hectares
in 2019-20). I can't give you a clean row-per-state-per-year CSV from this
PDF the way I could for the IJIRMF paper — the underlying figures would
need to come from the source data itself (NCRB's "Accidental Deaths and
Suicides in India" reports, or IMD directly), which the EnviStats report
cites but doesn't tabulate as plain text.

**What to actually do with it:**
- Use the narrative figures above as cited context (e.g. a "national
  disaster toll" stat on a compliance/force-majeure info panel), same
  treatment as the BehanBox/NCDHR SC-ST context data from before.
- If you want real tabular disaster data for `disaster_events`, go to the
  primary source it cites — NCRB's Accidental Deaths and Suicides in India
  report — rather than trying to scrape numbers out of this PDF's charts.
- This is still **national-level, not state+district+date-window level**,
  so it doesn't replace what `force_majeure.py` actually needs to match a
  specific project's delay to a specific event.

## 3. On the pasted dataset plan itself

The plan you pasted (dataset tiers, schema fields, `data/` folder layout)
is well-structured and consistent with what's actually missing in your
repo — I'd trust its schema design. Two corrections worth knowing before
you act on it:

- It cites `sansad.in/ls/members` and `sansad.in/ls/ipg/list-of-members` as
  a live source you can pull MP data from — in practice that page is
  JS-rendered and not fetchable as a flat file, which is exactly why the
  `All_Members.pdf` you gave me two turns ago (which I already converted
  to a clean CSV) is the more useful artifact — you already have that step
  done.
- It cites the official MPLADS portal for fund/UC/AC/expenditure data as if
  it's straightforwardly available — that portal likely requires
  session-based navigation per-MP/per-district rather than a bulk export,
  so treat "official MPLADS fund/expenditure data" as still **required,
  not yet in hand**, same status as in my last report.

Everything else in that plan (tiering, schema fields, the `data/raw` vs
`data/processed` split) is sound and you can proceed with it directly.
