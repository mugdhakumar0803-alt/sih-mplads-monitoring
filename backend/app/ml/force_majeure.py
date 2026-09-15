"""
Owner: AI/ML or Cybersecurity (deterministic data lookup, not ML).
Location: backend/app/ml/force_majeure.py

Uses your REAL uploaded dataset (Amount_consented_for_Calamity.csv) —
official records of MPs who consented to divert MPLADS funds toward
declared national calamities (floods, landslides, etc.). If a work's
responsible MP appears in this list around the time a delay is being
evaluated, the delay should NOT count against that official's
performance score.

Honest limitation: this real dataset only has 13 rows and is MP-linked,
not district/village-linked — meaning it tells you "this MP's
constituency had a declared calamity around this date," not "this exact
work site was directly affected." That's a reasonable approximation for
a prototype, not a precise geographic match — say this plainly if asked,
same as the SC/ST data gap.
"""
from __future__ import annotations

import pandas as pd
from dataclasses import dataclass
from datetime import datetime, timedelta

CALAMITY_CSV_PATH = "backend/app/ml/training/Amount_consented_for_Calamity.csv"

# How long after a calamity's consent date a delay is still considered
# potentially calamity-related. Adjust based on typical MPLADS work
# durations — 180 days is a reasonable starting assumption.
CALAMITY_GRACE_PERIOD_DAYS = 180


@dataclass
class ForceMajeureCheck:
    is_excused: bool
    reason: str
    matched_calamity: str | None = None


def load_calamity_data(csv_path: str = CALAMITY_CSV_PATH) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["Date of Consent"] = pd.to_datetime(df["Date of Consent"], format="%d-%b-%Y", errors="coerce")
    return df


def check_force_majeure(
    mp_name: str,
    delay_evaluation_date: datetime,
    calamity_df: pd.DataFrame,
) -> ForceMajeureCheck:
    """
    Call this BEFORE penalizing a work's delay in any risk score or
    performance metric. mp_name should match the "Hon'ble Members of
    Parliament" column format in your real data as closely as possible —
    names in this dataset are inconsistently formatted (some "Shri X",
    some all-caps, some plain), so exact matching will miss some real
    cases. A fuzzy/normalized match is a reasonable upgrade later.
    """
    mp_matches = calamity_df[
        calamity_df["Hon'ble Members of Parliament"].str.strip().str.lower()
        == mp_name.strip().lower()
    ]

    if mp_matches.empty:
        return ForceMajeureCheck(is_excused=False, reason="No calamity consent found for this MP")

    for _, row in mp_matches.iterrows():
        consent_date = row["Date of Consent"]
        if pd.isna(consent_date):
            continue
        window_end = consent_date + timedelta(days=CALAMITY_GRACE_PERIOD_DAYS)
        if consent_date <= delay_evaluation_date <= window_end:
            return ForceMajeureCheck(
                is_excused=True,
                reason=f"MP consented to calamity relief during this period: {row['Calamity Name']}",
                matched_calamity=row["Calamity Name"],
            )

    return ForceMajeureCheck(
        is_excused=False,
        reason="MP has calamity consent(s) on record, but none within the relevant time window",
    )


# --- Quick manual test ---
if __name__ == "__main__":
    df = load_calamity_data()
    print(f"Loaded {len(df)} calamity consent records")

    # Real example from your actual data
    result = check_force_majeure(
        mp_name="Shri Gurjeet Singh Aujla",
        delay_evaluation_date=datetime(2026, 1, 15),
        calamity_df=df,
    )
    print(result)

    # An MP with no calamity record
    result2 = check_force_majeure(
        mp_name="Someone Not In The List",
        delay_evaluation_date=datetime(2026, 1, 15),
        calamity_df=df,
    )
    print(result2)