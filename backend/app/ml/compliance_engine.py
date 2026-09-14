"""
Owner: AI/ML or Cybersecurity (this is deterministic rule logic, not
machine learning — no model, no training, just checking real numbers
against real published thresholds).
Location: backend/app/ml/compliance_engine.py

Two things this file does, and one thing it HONESTLY CANNOT do yet —
read the note near compute_sc_st_percent() below before presenting this
as fully complete to your team or in your demo.
"""
from dataclasses import dataclass

# Categories counted toward the mandatory 15% "national priority area"
# spend (drinking water, primary education, public health/sanitation,
# road connectivity) — this maps directly onto the categories your
# category_classifier.py already produces.
PRIORITY_AREA_CATEGORIES = {"drinking_water", "education", "health", "sanitation", "road"}

# Non-permissible work categories under MPLADS guidelines — checked
# against the WORK text itself, since these are things that should never
# be sanctioned regardless of category label.
NON_PERMISSIBLE_KEYWORDS = [
    "temple", "mosque", "church", "gurudwara", "religious",  # religious structures
    "cash award", "cash prize", "cash benefit", "donation",   # personal cash benefits
    "salary", "wages", "honorarium", "administrative expense",  # admin/salary spending
    "consumable", "stationery", "furniture purchase",          # consumables
]

SC_ALLOCATION_REQUIRED_PERCENT = 15.0
ST_ALLOCATION_REQUIRED_PERCENT = 7.5
PRIORITY_AREA_REQUIRED_PERCENT = 15.0


@dataclass
class CategoryValidationResult:
    is_permissible: bool
    reason: str


@dataclass
class ComplianceStatus:
    mp_name: str
    priority_area_percent: float
    priority_area_required_percent: float
    priority_area_on_track: bool
    sc_allocation_percent: float | None   # None = not computable yet, see note below
    st_allocation_percent: float | None   # None = not computable yet, see note below


def validate_work_category(work_text: str) -> CategoryValidationResult:
    """
    Deterministic check — run this BEFORE a work is sanctioned, not after.
    Catches obviously non-permissible categories before money is even
    allocated.
    """
    text_lower = work_text.lower()
    for keyword in NON_PERMISSIBLE_KEYWORDS:
        if keyword in text_lower:
            return CategoryValidationResult(
                is_permissible=False,
                reason=f"Contains non-permissible keyword: '{keyword}'",
            )
    return CategoryValidationResult(is_permissible=True, reason="No non-permissible keywords found")


def compute_priority_area_percent(mp_works: list[dict]) -> float:
    """
    mp_works: list of dicts, each with at least {"category": str, "sanctioned_amount": float}
    for ONE MP's works. Returns the percentage of their total allocation
    that went to priority-area categories.

    This IS fully computable right now, because your category_classifier.py
    already tells you which category each work belongs to.
    """
    total = sum(w["sanctioned_amount"] for w in mp_works)
    if total == 0:
        return 0.0
    priority_total = sum(
        w["sanctioned_amount"] for w in mp_works if w["category"] in PRIORITY_AREA_CATEGORIES
    )
    return round((priority_total / total) * 100, 2)


def compute_sc_st_percent(mp_works: list[dict]) -> tuple[None, None]:
    """
    HONEST GAP — READ THIS BEFORE USING THIS FUNCTION:

    Computing real SC/ST allocation percentages requires knowing which
    VILLAGES or CONSTITUENCIES are officially designated SC/ST areas.
    Neither your MPLADS.csv nor any dataset we've found so far contains
    that geographic designation — it would need to come from Census
    village-level SC/ST population data, or a state government's
    published list of SC/ST-designated areas, cross-referenced against
    the VILLAGE/CONSTITUENCY fields in your works data.

    Until that reference data is sourced and joined in, this function
    returns (None, None) deliberately — DO NOT fake a number here. Report
    this honestly in your demo as "priority-area compliance is fully
    live; SC/ST compliance is architecturally ready but needs one more
    reference dataset we're still sourcing" — that's a legitimate,
    professional thing to say, and it's much better than presenting a
    made-up percentage that falls apart under a judge's question.
    """
    return None, None


def get_mp_compliance_status(mp_name: str, mp_works: list[dict]) -> ComplianceStatus:
    priority_pct = compute_priority_area_percent(mp_works)
    sc_pct, st_pct = compute_sc_st_percent(mp_works)

    return ComplianceStatus(
        mp_name=mp_name,
        priority_area_percent=priority_pct,
        priority_area_required_percent=PRIORITY_AREA_REQUIRED_PERCENT,
        priority_area_on_track=priority_pct >= PRIORITY_AREA_REQUIRED_PERCENT,
        sc_allocation_percent=sc_pct,
        st_allocation_percent=st_pct,
    )


# --- Quick manual test ---
if __name__ == "__main__":
    print(validate_work_category("Construction of a temple renovation fund"))
    print(validate_work_category("Installing community drinking water plants"))
    print()

    sample_works = [
        {"category": "drinking_water", "sanctioned_amount": 200000},
        {"category": "road", "sanctioned_amount": 500000},
        {"category": "community_infrastructure", "sanctioned_amount": 300000},
    ]
    status = get_mp_compliance_status("Sample MP", sample_works)
    print(status)