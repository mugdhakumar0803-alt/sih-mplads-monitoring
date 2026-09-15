# Database configuration and session management
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from .config import settings

# Create database engine with PostGIS support
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=False,
)

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
