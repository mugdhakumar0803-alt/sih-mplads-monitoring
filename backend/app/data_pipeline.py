"""Validated, repeatable import pipeline for MPLADS source CSV files."""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
from datetime import datetime
from pathlib import Path

from sqlalchemy import select

from .database import SessionLocal, init_db
from .models.work import Work, WorkCategory, WorkStatus

REQUIRED_COLUMNS = {
    "MP NAME", "WORK", "STATE", "CONSTITUENCY", "RECOMMENDED DATE",
    "ALLOCATION AMOUNT", "STATUS",
}

CATEGORY_TERMS = {
    WorkCategory.DRINKING_WATER: ("water", "hand pump", "tubewell", "borewell"),
    WorkCategory.ROAD: ("road", "pathway", "bridge", "culvert"),
    WorkCategory.STREET_LIGHTING: ("street light", "streetlight", "lighting"),
    WorkCategory.SANITATION: ("toilet", "sanitation", "sewerage", "waste"),
    WorkCategory.EDUCATION: ("school", "classroom", "education", "library", "anganwadi"),
    WorkCategory.HEALTH: ("hospital", "dispensary", "health center", "health centre"),
    WorkCategory.ELECTRIFICATION: ("electric", "electrification", "transformer"),
    WorkCategory.SPORTS: ("playground", "stadium", "sports", "gymnasium"),
    WorkCategory.IRRIGATION: ("irrigation", "canal", "check dam", "pond"),
    WorkCategory.COMMUNITY_INFRASTRUCTURE: ("community", "panchayat", "cremation"),
}


def _read_rows(path: Path) -> tuple[list[dict[str, str]], str]:
    encodings = ("utf-8-sig", "utf-16", "latin-1")
    last_error = None
    for encoding in encodings:
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                sample = handle.read(4096)
                handle.seek(0)
                dialect = csv.Sniffer().sniff(sample, delimiters=";,\t,")
                rows = list(csv.DictReader(handle, dialect=dialect))
                return rows, dialect.delimiter
        except (UnicodeDecodeError, csv.Error) as error:
            last_error = error
    raise ValueError(f"Could not parse {path}: {last_error}")


def _clean(value) -> str | None:
    value = re.sub(r"\s+", " ", str(value or "")).strip()
    if not value or value.lower() in {"nan", "none", "na", "n/a", "grand total"}:
        return None
    return value


def _amount(value) -> float | None:
    cleaned = _clean(value)
    if cleaned is None:
        return None
    cleaned = re.sub(r"[^0-9.-]", "", cleaned)
    try:
        return float(cleaned)
    except ValueError:
        return None


def _date(value) -> datetime | None:
    cleaned = _clean(value)
    if not cleaned:
        return None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None


def _category(title: str) -> WorkCategory:
    text = title.lower()
    for category, terms in CATEGORY_TERMS.items():
        if any(term in text for term in terms):
            return category
    return WorkCategory.COMMUNITY_INFRASTRUCTURE


def _status(value: str) -> WorkStatus:
    normalized = (_clean(value) or "").lower()
    for status in WorkStatus:
        if status.value.lower() == normalized:
            return status
    return WorkStatus.UNSANCTIONED


def _source_id(row: dict[str, str], ordinal: int) -> str:
    raw = "|".join(_clean(row.get(key)) or "" for key in ("MP NAME", "WORK", "STATE", "CONSTITUENCY", "RECOMMENDED DATE"))
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]
    return f"{ordinal:08d}-{digest}"


def import_file(path: str | Path, replace_source: bool = False) -> dict:
    source = Path(path)
    rows, delimiter = _read_rows(source)
    if not rows:
        return {"source_dataset": source.name, "delimiter": delimiter, "read": 0, "imported": 0, "skipped": 0, "duplicates": 0}
    columns = set(rows[0])
    missing = REQUIRED_COLUMNS - columns
    if missing:
        raise ValueError(f"{source.name} missing columns: {', '.join(sorted(missing))}")

    init_db()
    db = SessionLocal()
    stats = {"source_dataset": source.name, "delimiter": delimiter, "read": len(rows), "imported": 0, "updated": 0, "skipped": 0, "duplicates": 0}
    seen = set()
    try:
        if replace_source:
            db.query(Work).filter(Work.source_dataset == source.name).delete(synchronize_session=False)
        for ordinal, row in enumerate(rows, 1):
            title = _clean(row.get("WORK"))
            state = _clean(row.get("STATE"))
            constituency = _clean(row.get("CONSTITUENCY"))
            recommended = _date(row.get("RECOMMENDED DATE"))
            amount = _amount(row.get("ALLOCATION AMOUNT"))
            source_id = _source_id(row, ordinal)
            if not title or not state or not constituency or not recommended or amount is None:
                stats["skipped"] += 1
                continue
            dedupe_key = (title.casefold(), state.casefold(), constituency.casefold(), recommended.date())
            if dedupe_key in seen:
                stats["duplicates"] += 1
                continue
            seen.add(dedupe_key)
            values = {
                "work_id": f"MPLADS-{source.name[:8].upper()}-{ordinal:08d}",
                "mp_name": _clean(row.get("MP NAME")) or "Data unavailable",
                "work_title": title,
                "category": _category(title),
                "state": state,
                "constituency": constituency,
                "district": _clean(row.get("DISTRICT")),
                "block": _clean(row.get("BLOCK")),
                "village": _clean(row.get("VILLAGE")),
                "ward": _clean(row.get("WARD")),
                "location": " / ".join(filter(None, (_clean(row.get("CITY")), _clean(row.get("BLOCK")), _clean(row.get("VILLAGE"))))) or None,
                "status": _status(row.get("STATUS")),
                "allocation_amount": amount,
                "sanctioned_amount": _amount(row.get("SANCTIONED AMOUNT")),
                "expenditure_amount": _amount(row.get("EXPENDITURE")),
                "ida_approval": _clean(row.get("IDA APPROVAL")),
                "recommended_date": recommended,
                "source_dataset": source.name,
                "source_record_id": source_id,
            }
            existing = db.execute(select(Work).where(Work.source_dataset == source.name, Work.source_record_id == source_id)).scalar_one_or_none()
            if existing:
                for key, value in values.items():
                    if key not in {"work_id"}:
                        setattr(existing, key, value)
                stats["updated"] += 1
            else:
                db.add(Work(**values))
                stats["imported"] += 1
            if (stats["imported"] + stats["updated"]) % 500 == 0:
                db.commit()
        db.commit()
        return stats
    finally:
        db.close()


def import_paths(paths: list[str], replace_source: bool = False) -> list[dict]:
    return [import_file(path, replace_source=replace_source) for path in paths]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import MPLADS CSV files into PostgreSQL")
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--replace-source", action="store_true")
    args = parser.parse_args()
    for result in import_paths([str(path) for path in args.paths], args.replace_source):
        print(result)
