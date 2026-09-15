# Database configuration and session management
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from .config import settings

engine_options = {
    "pool_pre_ping": True,
    "echo": False,
}
if settings.database_url.startswith("sqlite"):
    engine_options.update({
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    })

# PostgreSQL remains the deployment database; SQLite is supported for local demos.
engine = create_engine(settings.database_url, **engine_options)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for ORM models
Base = declarative_base()


def get_db():
    """Dependency for getting database session in API endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create local tables; production deployments should use migrations."""
    from .models import fund_release, grievance, photo, user, work, rating
    Base.metadata.create_all(bind=engine)
