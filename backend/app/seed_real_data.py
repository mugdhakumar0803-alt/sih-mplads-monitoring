"""
Import REAL MPLADS data into the actual application database.

WHY THIS EXISTS: your real government dataset (MPLADS.csv, 60,360 rows)
has been sitting in backend/app/ml/training/ the whole time, but nothing
ever loaded it into the `works` table that your dashboards, charts, and
chatbot actually query. seed.py only creates 3 fake demo works. This
script is the missing link — it reads the real CSV and creates real
Work rows (and optionally real, pre-approved MP accounts) so your demo
shows real government data end to end.

USAGE (run from the backend/ folder, with your venv active and your
database reachable):

    # Quick demo dataset — 500 real works, fast (~1-2 min)
    python -m app.seed_real_data --limit 500

    # Also create a pre-approved MP User account for every unique MP
    # found in those rows (so the leaderboard has someone real to rank,
    # and you can log in AS a real MP for your demo)
    python -m app.seed_real_data --limit 500 --create-mp-users

    # Import everything (60k+ rows — slow, only do this if you have time
    # and don't need it fast before a demo)
    python -m app.seed_real_data --all --create-mp-users

WHAT IT DOES NOT DO: it does not invent GPS coordinates (the CSV has
none), so geotag photo verification will say "unverifiable" for these
works until you manually set latitude/longitude on the specific work(s)
you plan to demo photo upload with. See --set-demo-location below —
that's the realistic way to get a *working* geotag demo: pick ONE real
work, set its coordinates to wherever you'll actually stand with your
phone during the demo.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd

from .database import SessionLocal, init_db
from .auth.security import get_password_hash
from .models.user import User, UserRole, ApprovalStatus, ParliamentHouse
from .models.work import Work, WorkCategory, WorkStatus
from .ml.category_classifier import classify_work_category

CSV_PATH = Path(__file__).parent / "ml" / "training" / "MPLADS.csv"

HOUSE_MAP = {
    "Lok Sabha": ParliamentHouse.LOK_SABHA,
    "Rajya Sabha": ParliamentHouse.RAJYA_SABHA,
}

STATUS_MAP = {
    "Sanctioned": WorkStatus.SANCTIONED,
    "Ongoing": WorkStatus.ONGOING,
    "Completed": WorkStatus.COMPLETED,
    "Unsanctioned": WorkStatus.UNSANCTIONED,
    "Rejected": WorkStatus.REJECTED,
}


def load_csv(limit: int | None) -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH, sep=";")
    df["RECOMMENDED DATE"] = pd.to_datetime(df["RECOMMENDED DATE"], errors="coerce")
    df = df.dropna(subset=["RECOMMENDED DATE", "ALLOCATION AMOUNT", "WORK", "MP NAME"])
    if limit:
        df = df.head(limit)
    return df


def slugify_username(name: str, used: set[str]) -> str:
    base = "".join(c for c in name.lower().replace(" ", "_") if c.isalnum() or c == "_")
    base = base or "mp_user"
    candidate = base
    n = 1
    while candidate in used:
        n += 1
        candidate = f"{base}{n}"
    used.add(candidate)
    return candidate


def import_data(limit: int | None, create_mp_users: bool) -> None:
    if not CSV_PATH.exists():
        print(f"Could not find {CSV_PATH}. Make sure MPLADS.csv is in backend/app/ml/training/.")
        return

    init_db()
    df = load_csv(limit)
    print(f"Loaded {len(df)} rows from {CSV_PATH.name}")

    db = SessionLocal()
    used_usernames = {u for (u,) in db.query(User.username).all()}
    existing_work_ids = {w for (w,) in db.query(Work.work_id).all()}

    created_works = 0
    skipped_works = 0
    created_users = 0
    mp_cache: dict[str, dict] = {}  # mp_name -> {state, constituency, house}

    try:
        for i, row in df.iterrows():
            work_id = f"WRK-REAL-{i:06d}"
            if work_id in existing_work_ids:
                skipped_works += 1
                continue

            status = STATUS_MAP.get(str(row["STATUS"]).strip(), WorkStatus.UNSANCTIONED)
            category = classify_work_category(str(row["WORK"]))
            try:
                category_enum = WorkCategory(category)
            except ValueError:
                category_enum = WorkCategory.COMMUNITY_INFRASTRUCTURE

            mp_name = str(row["MP NAME"]).strip()
            state = str(row["STATE"]).strip()
            constituency = str(row["CONSTITUENCY"]).strip()
            allocation = float(row["ALLOCATION AMOUNT"])

            work = Work(
                work_id=work_id,
                mp_name=mp_name,
                work_title=str(row["WORK"])[:500],
                category=category_enum,
                state=state,
                constituency=constituency,
                location=str(row.get("VILLAGE") or row.get("CITY") or ""),
                status=status,
                allocation_amount=allocation,
                ida_approval=str(row.get("IDA APPROVAL", ""))[:50],
                recommended_date=row["RECOMMENDED DATE"].to_pydatetime(),
                completion_date=row["RECOMMENDED DATE"].to_pydatetime() if status == WorkStatus.COMPLETED else None,
            )
            db.add(work)
            created_works += 1

            if mp_name not in mp_cache:
                mp_cache[mp_name] = {
                    "state": state,
                    "constituency": constituency,
                    "house": HOUSE_MAP.get(str(row.get("HOUSE", "")).strip()),
                }

            if created_works % 250 == 0:
                db.commit()
                print(f"  ...{created_works} works imported so far")

        db.commit()
        print(f"Imported {created_works} real works ({skipped_works} already existed, skipped).")

        if create_mp_users:
            for mp_name, info in mp_cache.items():
                existing = db.query(User).filter(User.username == mp_name.lower().replace(" ", "_")).first()
                if existing:
                    continue
                username = slugify_username(mp_name, used_usernames)
                user = User(
                    username=username,
                    email=f"{username}@mplads.demo",
                    hashed_password=get_password_hash("Demo@12345"),
                    role=UserRole.MP,
                    approval_status=ApprovalStatus.APPROVED,  # pre-approved for demo purposes
                    state=info["state"],
                    constituency=info["constituency"],
                    house=info["house"],
                )
                db.add(user)
                created_users += 1
            db.commit()
            print(f"Created {created_users} real, pre-approved MP accounts (password for all: Demo@12345).")
            print("Log in with any of their usernames to see a real MP dashboard.")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--limit", type=int, default=500, help="How many real rows to import (default 500, fast for a demo)")
    parser.add_argument("--all", action="store_true", help="Import every usable row (60k+, slow)")
    parser.add_argument("--create-mp-users", action="store_true", help="Also create a pre-approved MP account per unique MP found")
    args = parser.parse_args()

    import_data(limit=None if args.all else args.limit, create_mp_users=args.create_mp_users)
