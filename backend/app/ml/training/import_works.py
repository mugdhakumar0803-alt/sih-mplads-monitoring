"""Import government MPLADS CSV rows into the works table."""
from datetime import datetime
from pathlib import Path
import re

import pandas as pd

from ...database import SessionLocal, init_db
from ...models.work import Work, WorkCategory, WorkStatus


CATEGORY_KEYWORDS = {
    "drinking_water": ("drinking water", "hand pump", "tubewell", "water supply", "borewell"),
    "road": ("road", "pathway", "bridge", "culvert"),
    "street_lighting": ("street light", "streetlight", "solar light", "lighting"),
    "sanitation": ("toilet", "sanitation", "sewerage", "waste management"),
    "education": ("school", "classroom", "education", "library", "anganwadi"),
    "health": ("hospital", "dispensary", "health center", "health centre"),
    "community_infrastructure": ("community hall", "community center", "panchayat", "cremation"),
    "electrification": ("electrification", "electric", "power supply", "transformer"),
    "sports": ("playground", "stadium", "sports", "gymnasium"),
    "irrigation": ("irrigation", "canal", "check dam", "pond", "water harvesting"),
}


def classify_category(title: str) -> WorkCategory:
    text = title.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return WorkCategory(category)
    return WorkCategory.COMMUNITY_INFRASTRUCTURE


def parse_status(value: str) -> WorkStatus:
    normalized = str(value).strip().lower()
    return next(
        (status for status in WorkStatus if status.value.lower() == normalized),
        WorkStatus.UNSANCTIONED,
    )


def clean(value) -> str | None:
    value = str(value).strip()
    return value if value and value.lower() not in {"nan", "none"} else None


def import_works(csv_path: str, replace: bool = False) -> int:
    init_db()
    frame = pd.read_csv(csv_path, sep=";", dtype=str)
    required = {"MP NAME", "WORK", "STATE", "CONSTITUENCY", "RECOMMENDED DATE", "ALLOCATION AMOUNT", "STATUS"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing CSV columns: {', '.join(sorted(missing))}")

    db = SessionLocal()
    imported = 0
    try:
        if replace:
            db.query(Work).delete()
        for index, row in frame.iterrows():
            title = clean(row["WORK"])
            state = clean(row["STATE"])
            constituency = clean(row["CONSTITUENCY"])
            recommended = pd.to_datetime(row["RECOMMENDED DATE"], errors="coerce")
            amount = pd.to_numeric(row["ALLOCATION AMOUNT"], errors="coerce")
            if not title or not state or not constituency or pd.isna(recommended) or pd.isna(amount):
                continue
            work_id = f"MPLADS-{index + 1:06d}"
            if db.query(Work).filter(Work.work_id == work_id).first():
                continue
            location = " / ".join(filter(None, [clean(row.get("CITY")), clean(row.get("WARD")), clean(row.get("BLOCK")), clean(row.get("VILLAGE"))]))
            db.add(Work(
                work_id=work_id,
                mp_name=clean(row["MP NAME"]) or "Unknown MP",
                work_title=title,
                category=classify_category(title),
                state=state,
                constituency=constituency,
                location=location or None,
                status=parse_status(row["STATUS"]),
                allocation_amount=float(amount),
                ida_approval=clean(row.get("IDA APPROVAL")),
                recommended_date=recommended.to_pydatetime(),
            ))
            imported += 1
            if imported % 500 == 0:
                db.commit()
        db.commit()
    finally:
        db.close()
    return imported


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", nargs="?", default=str(Path(__file__).with_name("MPLADS.csv")))
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    print(f"Imported {import_works(args.csv, replace=args.replace)} works")