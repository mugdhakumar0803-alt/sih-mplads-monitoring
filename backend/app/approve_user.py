"""Approve a pending account for a local demo or administrator workflow."""
import argparse

from .database import SessionLocal
from .models.user import ApprovalStatus, User


def approve(username: str) -> bool:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return False
        user.approval_status = ApprovalStatus.APPROVED
        db.commit()
        return True
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("username")
    args = parser.parse_args()
    if not approve(args.username):
        raise SystemExit(f"User not found: {args.username}")