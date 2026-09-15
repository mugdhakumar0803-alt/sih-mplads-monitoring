"""
Approve a pending user account from the command line.

Why this exists: MP / District / State / Ministry / Admin accounts now
require approval before they can log in (see auth/routes.py). Approving
them normally would be an admin's job through an admin panel — but this
project doesn't have one yet, and you need a way to approve your FIRST
account (chicken-and-egg problem: no approved admin exists yet to approve
anyone). This script is that escape hatch for local development/demo.

Usage (run from the backend/ folder, with your venv active):
    python -m app.approve_user <username>
    python -m app.approve_user demo_mp
"""
import argparse

from .database import SessionLocal
from .models.user import User, ApprovalStatus


def approve(username: str) -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"No user found with username '{username}'.")
            return

        user.approval_status = ApprovalStatus.APPROVED
        user.is_active = True
        db.commit()
        print(f"Approved '{username}' (role: {user.role.value}). They can log in now.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("username", help="Username of the account to approve")
    args = parser.parse_args()
    approve(args.username)
