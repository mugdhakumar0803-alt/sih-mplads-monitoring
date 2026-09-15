"""
Owner: Full-stack/Backend.
Location: backend/app/services/sla_engine.py

Real SLA timing and automatic escalation — this is what should replace
the current escalate_grievance() in grievance_service.py, which just
flips a manual True/False switch with no timer or ladder logic.

Import this into grievance_service.py and call check_and_escalate()
whenever a grievance is read (e.g. on every GET request, or via a
scheduled job if your team sets one up) — it's a pure function, no
side effects except returning what the grievance's state SHOULD be,
so grievance_service.py stays in charge of actually saving it.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta

SLA_WINDOW_DAYS = 7

# The escalation ladder, in order. When a grievance breaches its SLA at
# one level, it moves to the next one in this list.
ESCALATION_LADDER = ["district", "state", "mp", "ministry"]


@dataclass
class SlaStatus:
    current_level: str
    sla_deadline: datetime
    days_remaining: float
    is_breached: bool
    should_escalate_to: str | None  # None if already at the top (ministry) or not breached


def compute_sla_status(
    filed_at: datetime,
    current_level: str,
    last_escalated_at: datetime | None = None,
) -> SlaStatus:
    """
    filed_at: when the grievance was originally created
    current_level: one of ESCALATION_LADDER — where it sits right now
    last_escalated_at: when it last moved to current_level (use filed_at
                        if it has never been escalated, i.e. still at 'district')
    """
    clock_start = last_escalated_at or filed_at
    deadline = clock_start + timedelta(days=SLA_WINDOW_DAYS)
    now = datetime.utcnow()

    days_remaining = (deadline - now).total_seconds() / 86400
    is_breached = now > deadline

    should_escalate_to = None
    if is_breached and current_level in ESCALATION_LADDER:
        current_index = ESCALATION_LADDER.index(current_level)
        if current_index < len(ESCALATION_LADDER) - 1:
            should_escalate_to = ESCALATION_LADDER[current_index + 1]
        # If already at "ministry" and still breached, should_escalate_to
        # stays None on purpose — per Section 3H of the blueprint, the
        # SLA clock stops auto-escalating at the top of the ladder and
        # just reports how overdue it is instead.

    return SlaStatus(
        current_level=current_level,
        sla_deadline=deadline,
        days_remaining=round(days_remaining, 1),
        is_breached=is_breached,
        should_escalate_to=should_escalate_to,
    )


def check_and_escalate(grievance) -> tuple[str, bool]:
    """
    Convenience wrapper for grievance_service.py — pass in your Grievance
    ORM object (needs .filed_at / .created_at, .current_escalation_level
    or similar, and optionally .last_escalated_at). Adjust the attribute
    names below to match your actual Grievance model's real field names.

    Returns (new_level, was_escalated) — grievance_service.py should save
    new_level back onto the grievance if was_escalated is True.
    """
    status = compute_sla_status(
        filed_at=getattr(grievance, "filed_at", None) or grievance.created_at,
        current_level=getattr(grievance, "current_escalation_level", "district"),
        last_escalated_at=getattr(grievance, "last_escalated_at", None),
    )

    if status.should_escalate_to:
        return status.should_escalate_to, True
    return status.current_level, False


# --- Quick manual test ---
if __name__ == "__main__":
    # A grievance filed 8 days ago at district level — should be breached and ready to escalate
    filed = datetime.utcnow() - timedelta(days=8)
    status = compute_sla_status(filed_at=filed, current_level="district")
    print(status)

    # A grievance filed 2 days ago — well within SLA, no escalation
    filed_recent = datetime.utcnow() - timedelta(days=2)
    status2 = compute_sla_status(filed_at=filed_recent, current_level="district")
    print(status2)

    # Already at ministry, still breached — should NOT try to escalate further
    filed_old = datetime.utcnow() - timedelta(days=10)
    status3 = compute_sla_status(filed_at=filed_old, current_level="ministry")
    print(status3)