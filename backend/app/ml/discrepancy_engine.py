"""
Owner: AI/ML or Full-stack/Backend.
Location: backend/app/ml/discrepancy_engine.py

Honest design note: detecting "is a hand pump actually present in this
photo" is a real computer-vision task (object detection) that's a much
bigger lift than a hackathon allows to do reliably. So this does the
HONEST, buildable version instead: it doesn't try to look INSIDE the
photo — it cross-checks the STATUS CLAIMS against each other, which is
just as powerful for catching the exact pattern from the real Gujarat
CAG case (marked "Completed" while nothing was actually built).

Rule: if a work's official status is "Completed" and a citizen has
filed a grievance or evidence submission on that work claiming it's NOT
done, that is an automatic HIGH-PRIORITY discrepancy — no ML needed,
this is a plain, defensible logic contradiction worth surfacing loudly.
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DiscrepancyResult:
    has_discrepancy: bool
    severity: str  # "none", "medium", "high"
    reason: str


# Keywords that suggest a citizen's grievance is specifically disputing
# completion, not just complaining about quality or delay.
COMPLETION_DISPUTE_KEYWORDS = [
    "not built", "not installed", "not done", "not completed",
    "nothing there", "no work", "not visible", "not present",
    "empty site", "no construction", "hasn't started",
]


def check_completion_discrepancy(
    official_status: str,
    citizen_grievance_texts: list[str],
) -> DiscrepancyResult:
    """
    official_status: the work's current status field ("Completed", "Ongoing", etc.)
    citizen_grievance_texts: descriptions of ALL grievances filed on this
                              specific work (open or resolved — even a
                              resolved-but-disputed one is worth knowing)
    """
    if official_status != "Completed":
        return DiscrepancyResult(
            has_discrepancy=False,
            severity="none",
            reason="Work is not marked completed — no discrepancy to check",
        )

    disputing_grievances = [
        text for text in citizen_grievance_texts
        if any(keyword in text.lower() for keyword in COMPLETION_DISPUTE_KEYWORDS)
    ]

    if not disputing_grievances:
        return DiscrepancyResult(
            has_discrepancy=False,
            severity="none",
            reason="No citizen evidence disputes the completion claim",
        )

    return DiscrepancyResult(
        has_discrepancy=True,
        severity="high",
        reason=(
            f"Work is marked 'Completed' but {len(disputing_grievances)} citizen "
            f"grievance(s) specifically dispute that — this exact pattern (marked "
            f"complete, nothing actually built) matches a real documented MPLADS "
            f"fraud case"
        ),
    )


def check_photo_gap_discrepancy(
    official_status: str,
    days_since_last_photo: float | None,
    max_allowed_gap_days: int = 60,
) -> DiscrepancyResult:
    """
    Second, complementary check: a work marked "Completed" should have a
    RECENT completion photo. If it's been marked complete but the last
    photo is old (or missing), that's a lower-confidence but still
    worth-flagging discrepancy.
    """
    if official_status != "Completed":
        return DiscrepancyResult(has_discrepancy=False, severity="none", reason="Not marked completed")

    if days_since_last_photo is None:
        return DiscrepancyResult(
            has_discrepancy=True,
            severity="high",
            reason="Marked 'Completed' but no verification photo was ever uploaded",
        )

    if days_since_last_photo > max_allowed_gap_days:
        return DiscrepancyResult(
            has_discrepancy=True,
            severity="medium",
            reason=f"Marked 'Completed' but last photo is {days_since_last_photo:.0f} days old",
        )

    return DiscrepancyResult(has_discrepancy=False, severity="none", reason="Photo is recent enough")


# --- Quick manual test ---
if __name__ == "__main__":
    # Real-pattern test: marked complete, citizen says otherwise
    result = check_completion_discrepancy(
        official_status="Completed",
        citizen_grievance_texts=["This work is not visible at the site, nothing was built here."],
    )
    print(result)

    # No dispute — should be clean
    result2 = check_completion_discrepancy(
        official_status="Completed",
        citizen_grievance_texts=["The quality of the road is a bit poor but it exists."],
    )
    print(result2)

    result3 = check_photo_gap_discrepancy(official_status="Completed", days_since_last_photo=145)
    print(result3)