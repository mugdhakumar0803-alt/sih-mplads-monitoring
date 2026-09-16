from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.work import Work


def test_application_imports():
    from app.main import app

    paths = {getattr(route, "path", None) for route in app.routes}
    assert "/health" in paths
    assert "/ai/duplicates" in app.openapi()["paths"]


def test_seeded_database_contains_demo_data():
    db = SessionLocal()
    try:
        assert db.query(Work).count() > 0
        assert db.query(User).filter(User.role == UserRole.MP).count() >= 1
    finally:
        db.close()