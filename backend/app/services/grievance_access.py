"""
Owner: Full-stack/Backend.
Location: backend/app/services/grievance_access.py

Two rules enforced here:
1. WHO CAN SEE WHAT — a citizen only ever sees their own filed grievances,
   plus public-status info on works generally. They NEVER see
   OFFICIAL_ONLY grievances (an MP's own escalation to the Ministry, for
   example) — those are filtered out entirely, not just hidden in the UI.
2. WHERE A GRIEVANCE STARTS — a citizen's grievance always starts at
   'district' (the normal ladder). An MP raising a concern starts higher
   up, since an MP escalating something to the Ministry shouldn't have
   to first pass through District and State, which are below an MP in
   the real hierarchy.
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..models.grievance import Grievance, GrievanceVisibility
from ..models.user import User, UserRole

# Where a grievance's SLA clock starts, based on who's filing it.
STARTING_LEVEL_BY_ROLE = {
    UserRole.CITIZEN: "district",
    UserRole.DISTRICT_OFFICIAL: "state",     # a district official escalating something starts one level up
    UserRole.STATE_OFFICIAL: "mp",
    UserRole.MP: "ministry",                  # an MP's own concern goes straight to the top
}

# Visibility, based on who's filing.
VISIBILITY_BY_ROLE = {
    UserRole.CITIZEN: GrievanceVisibility.PUBLIC,
    UserRole.DISTRICT_OFFICIAL: GrievanceVisibility.OFFICIAL_ONLY,
    UserRole.STATE_OFFICIAL: GrievanceVisibility.OFFICIAL_ONLY,
    UserRole.MP: GrievanceVisibility.OFFICIAL_ONLY,
}


def determine_filing_defaults(filer_role: UserRole) -> tuple[str, GrievanceVisibility]:
    """Call this when CREATING a grievance, to set the correct starting
    level and visibility based on who's actually filing it."""
    starting_level = STARTING_LEVEL_BY_ROLE.get(filer_role, "district")
    visibility = VISIBILITY_BY_ROLE.get(filer_role, GrievanceVisibility.PUBLIC)
    return starting_level, visibility


def get_visible_grievances_query(db: Session, current_user: User):
    """
    Call this instead of a raw db.query(Grievance) anywhere grievances are
    LISTED. This is the actual enforcement point — filtering happens in
    the database query itself, not after fetching everything and hoping
    the frontend hides the rest.
    """
    query = db.query(Grievance)

    if current_user.role == UserRole.CITIZEN:
        # Citizens see: their own filed grievances (any visibility), PLUS
        # any other PUBLIC grievance (for general transparency on works).
        # They never see another user's OFFICIAL_ONLY grievance.
        return query.filter(
            or_(
                Grievance.filed_by_user_id == current_user.id,
                Grievance.visibility == GrievanceVisibility.PUBLIC,
            )
        )

    if current_user.role == UserRole.DISTRICT_OFFICIAL:
        # District sees public citizen grievances in their own state,
        # plus official escalations that are currently sitting at their level.
        return query.filter(
            or_(
                Grievance.visibility == GrievanceVisibility.PUBLIC,
                Grievance.current_escalation_level == "district",
            )
        )

    # State/MP/Ministry roles: see everything relevant to their level and
    # above — for simplicity here, they see all grievances. Add
    # state/constituency filtering the same way as the works endpoints
    # once that scoping is wired in, so a State official only sees their
    # own state's cases, not the whole country's.
    return query


# --- Quick manual test ---
if __name__ == "__main__":
    level, visibility = determine_filing_defaults(UserRole.CITIZEN)
    print(f"Citizen files at: {level}, visibility: {visibility}")

    level, visibility = determine_filing_defaults(UserRole.MP)
    print(f"MP files at: {level}, visibility: {visibility}")