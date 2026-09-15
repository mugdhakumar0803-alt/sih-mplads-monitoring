"""Initialize tables and create development accounts."""
import argparse
from datetime import datetime

from .database import SessionLocal, init_db
from .auth.security import get_password_hash
from .models.user import User, UserRole
from .models.work import Work, WorkCategory, WorkStatus


DEMO_USERS = {
    "demo_citizen": UserRole.CITIZEN,
    "demo_mp": UserRole.MP,
    "demo_district": UserRole.DISTRICT_OFFICIAL,
    "demo_state": UserRole.STATE_OFFICIAL,
    "demo_ministry": UserRole.MINISTRY,
}

DEMO_WORKS = [
    ("W-DEMO-001", "Rampur Drinking Water Plant", WorkCategory.DRINKING_WATER, WorkStatus.ONGOING, 4200000),
    ("W-DEMO-002", "Tikonia Rural Road", WorkCategory.ROAD, WorkStatus.COMPLETED, 8500000),
    ("W-DEMO-003", "Jalesar Community Hall", WorkCategory.COMMUNITY_INFRASTRUCTURE, WorkStatus.SANCTIONED, 3000000),
]


def seed() -> None:
    init_db()
    db = SessionLocal()
    try:
        for username, role in DEMO_USERS.items():
            existing_user = db.query(User).filter(User.username == username).first()
            if existing_user:
                if username == "demo_mp" and not existing_user.constituency:
                    first_work = db.query(Work).order_by(Work.id).first()
                    if first_work:
                        existing_user.constituency = first_work.constituency
                        existing_user.state = first_work.state
                continue
            db.add(User(
                username=username,
                email=f"{username}@example.local",
                hashed_password=get_password_hash("Demo@12345"),
                role=role,
            ))
        for work_id, title, category, status, amount in DEMO_WORKS:
            if db.query(Work).filter(Work.work_id == work_id).first():
                continue
            db.add(Work(
                work_id=work_id,
                mp_name="Demo MP",
                work_title=title,
                category=category,
                state="Uttar Pradesh",
                constituency="Demo Constituency",
                allocation_amount=amount,
                status=status,
                recommended_date=datetime.utcnow(),
                risk_score=0.15 if status == WorkStatus.COMPLETED else 0.42,
                risk_level="low" if status == WorkStatus.COMPLETED else "medium",
                days_since_last_photo=12,
                citizen_grievance_count=0,
            ))
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    seed()
    print("Database initialized and demo users ensured.")