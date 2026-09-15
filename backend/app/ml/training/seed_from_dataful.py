"""
Owner: AI/ML.
Location: backend/app/ml/training/seed_from_dataful.py

Rewritten to match your REAL downloaded file exactly:
  MP NAME;WORK;CATEGORY;STATE;CONSTITUENCY;IDA;CITY;WARD;BLOCK;VILLAGE;
  RECOMMENDED DATE;ALLOCATION AMOUNT;IDA APPROVAL;STATUS;HOUSE
failed the first time anyone opened this file)
"""
import pandas as pd
from datetime import datetime
import numpy as np
import os
from pathlib import Path

from ..category_classifier import classify_work_category

# Only these statuses represent works with real progress information —
# "Unsanctioned" rows are just proposals, not yet real projects.
USABLE_STATUSES = {"Sanctioned", "Ongoing", "Completed"}

# Same idea as before — typical duration per category, in days. Adjust
# these once you've looked at real Completed works' actual durations.
DEFAULT_TYPICAL_DURATION_DAYS = {
    "drinking_water": 90,
    "road": 180,
    "community_infrastructure": 270,
    "education": 365,
    "sanitation": 120,
    "electrification": 150,
    "health": 200,
    "sports": 150,
    "irrigation": 200,
    "street_lighting": 60,
}
FALLBACK_DURATION_DAYS = 180


def load_raw_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";")
    df["RECOMMENDED DATE"] = pd.to_datetime(df["RECOMMENDED DATE"], errors="coerce")
    df = df.dropna(subset=["RECOMMENDED DATE", "ALLOCATION AMOUNT", "WORK"])
    df = df[df["STATUS"].isin(USABLE_STATUSES)].copy()
    return df


def add_real_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ignores the file's own near-useless CATEGORY column entirely — derives
    a real one from the WORK text instead. This is the slow step (runs a
    small model on every row), so it prints progress every 500 rows.
    """
    categories = []
    for i, work_text in enumerate(df["WORK"]):
        categories.append(classify_work_category(work_text))
        if (i + 1) % 500 == 0:
            print(f"Categorized {i + 1}/{len(df)} rows...")
    df["derived_category"] = categories
    return df


def compute_cost_ratio(df: pd.DataFrame) -> pd.Series:
    group_median = df.groupby(["derived_category", "STATE"])["ALLOCATION AMOUNT"].transform("median")
    return df["ALLOCATION AMOUNT"] / group_median


def compute_progress_ratio(df: pd.DataFrame) -> pd.Series:
    """
    Sanctioned  -> approved but no progress yet, so treat as low progress (0.1)
    Completed   -> 1.0 regardless of how long it took
    Ongoing     -> compare elapsed time since RECOMMENDED DATE against the
                   typical duration for that category
    """
    today = pd.Timestamp(datetime.now())
    elapsed_days = (today - df["RECOMMENDED DATE"]).dt.days.clip(lower=1)
    expected_days = df["derived_category"].map(DEFAULT_TYPICAL_DURATION_DAYS).fillna(FALLBACK_DURATION_DAYS)

    ratio = pd.Series(index=df.index, dtype=float)
    ratio[df["STATUS"] == "Completed"] = 1.0
    ratio[df["STATUS"] == "Sanctioned"] = 0.1
    ongoing_mask = df["STATUS"] == "Ongoing"
    ratio[ongoing_mask] = (expected_days[ongoing_mask] / elapsed_days[ongoing_mask]).clip(upper=1.0)
    return ratio


def add_synthetic_verification_features(df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Same approach as before — days_since_last_photo and grievance_count
    don't exist in any government dataset, so we simulate plausible values
    until your own platform starts generating real ones."""
    rng = np.random.default_rng(seed)
    n = len(df)
    df = df.copy()
    df["days_since_last_photo"] = rng.exponential(scale=20, size=n).clip(0, 365)
    df["citizen_grievance_count"] = rng.poisson(lam=0.3, size=n)

    suspicious_idx = df.sample(frac=0.05, random_state=seed).index
    df.loc[suspicious_idx, "days_since_last_photo"] = rng.uniform(120, 300, size=len(suspicious_idx))
    df.loc[suspicious_idx, "citizen_grievance_count"] = rng.integers(2, 6, size=len(suspicious_idx))
    return df


def build_training_set(raw_csv_path: str, output_csv_path: str) -> pd.DataFrame:
    df = load_raw_csv(raw_csv_path)
    print(f"Loaded {len(df)} usable rows (Sanctioned/Ongoing/Completed only)")

    df = add_real_category(df)
    df["cost_ratio_vs_category_median"] = compute_cost_ratio(df)
    df["progress_vs_elapsed_time_ratio"] = compute_progress_ratio(df)
    df = add_synthetic_verification_features(df)

    df["work_id"] = ["WRK-" + str(i).zfill(6) for i in range(len(df))]

    training_columns = [
        "work_id",
        "cost_ratio_vs_category_median",
        "progress_vs_elapsed_time_ratio",
        "days_since_last_photo",
        "citizen_grievance_count",
    ]
    training_df = df[training_columns].dropna()
    training_df.to_csv(output_csv_path, index=False)
    print(f"Wrote {len(training_df)} training rows to {output_csv_path}")
    return training_df


if __name__ == "__main__":
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Point this at wherever you saved your real MPLADS.csv download
    build_training_set(
        raw_csv_path=str(script_dir / "MPLADS.csv"),
        output_csv_path=str(script_dir / "mplads_training_set.csv"),
    )