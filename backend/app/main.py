from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from app.routers import analytics

from app.database import Base, engine, init_db, SessionLocal
from app.models.user import User
from app.models.work import Work
from app.seed import seed
from app.models.grievance import Grievance
from app.models.fund_release import FundReleaseRecord
from app.models.audit import AuditLog
from app.models.report_signature import ReportSignature

from app.auth.routes import router as auth_router
from app.routers.works import router as works_router
from app.routers.grievances import router as grievances_router
from app.routers.fund_release import router as fund_release_router
from app.routers.chatbot import router as chatbot_router
from app.routers.reports import router as reports_router
from app.routers.audit import router as audit_router
from app.routers.compliance import router as compliance_router
from app.routers.ai_detection import router as ai_detection_router
from app.routers.ratings import router as ratings_router
from app.routers.photos import router as photos_router
from app.routers.dashboard import router as dashboard_router
from app.routers.work_assignment import router as work_assignment_router
from app.routers.leaderboard import router as leaderboard_router
from app.routers.alerts import router as alerts_router
from app.routers.reference_data import router as reference_router

app = FastAPI(
    title="SIH MPLADS Monitoring & Accountability Platform",
    description="AI-powered MPLADS monitoring and accountability platform",
    version="0.2.0",
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    try:
        db = SessionLocal()
        work_count = db.query(Work).count()
        user_count = db.query(User).count()
        
        if work_count == 0:
            print("No works found in database; importing real MPLADS data first.")
            try:
                from app.seed_real_data import import_data
                import_data(limit=500, create_mp_users=True)
            except Exception as error:
                print(f"Real MPLADS import skipped: {error}")
                seed()
        elif user_count == 0:
            print("No users found; seeding demo users for login access.")
            seed()
        
        # Load reference data
        try:
            from app.seeds.load_reference_data import (
                load_constituencies, load_sector_reference,
                load_state_finance_historical, load_yearly_finance_historical,
                load_state_works_historical
            )
            from app.models.constituency import Constituency
            from app.models.reference_data import (
                SectorReference, StateFinanceHistorical,
                YearlyFinanceHistorical, StateWorksHistorical
            )
            from pathlib import Path
            
            data_dir = Path(__file__).parent.parent.parent
            
            # Load constituencies
            if db.query(Constituency).count() == 0:
                if (data_dir / "constituency_reservation_status.csv").exists():
                    print("Loading constituency data...")
                    result = load_constituencies(db, str(data_dir / "constituency_reservation_status.csv"))
                    print(f"Loaded {result.get('loaded', 0)} constituencies")
            
            # Load sector reference
            if db.query(SectorReference).count() == 0:
                if (data_dir / "historical_mplads_sector_works.csv").exists():
                    print("Loading sector reference data...")
                    result = load_sector_reference(db, str(data_dir / "historical_mplads_sector_works.csv"))
                    print(f"Loaded {result.get('loaded', 0)} sectors")
            
            # Load state finance historical
            if db.query(StateFinanceHistorical).count() == 0:
                if (data_dir / "historical_mplads_state_finance.csv").exists():
                    print("Loading state finance historical data...")
                    result = load_state_finance_historical(db, str(data_dir / "historical_mplads_state_finance.csv"))
                    print(f"Loaded {result.get('loaded', 0)} state finance records")
            
            # Load yearly finance historical
            if db.query(YearlyFinanceHistorical).count() == 0:
                if (data_dir / "historical_mplads_yearly_finance.csv").exists():
                    print("Loading yearly finance historical data...")
                    result = load_yearly_finance_historical(db, str(data_dir / "historical_mplads_yearly_finance.csv"))
                    print(f"Loaded {result.get('loaded', 0)} yearly finance records")
            
            # Load state works historical
            if db.query(StateWorksHistorical).count() == 0:
                if (data_dir / "historical_mplads_state_works.csv").exists():
                    print("Loading state works historical data...")
                    result = load_state_works_historical(db, str(data_dir / "historical_mplads_state_works.csv"))
                    print(f"Loaded {result.get('loaded', 0)} state works records")
        except Exception as error:
            print(f"Reference data loading: {error}")
        finally:
            db.close()
    except Exception as error:
        print(f"Startup seeding skipped: {error}")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analytics.router)
app.include_router(auth_router)
app.include_router(works_router)
app.include_router(grievances_router)
app.include_router(fund_release_router)
app.include_router(chatbot_router)
app.include_router(reports_router)
app.include_router(audit_router)
app.include_router(compliance_router)
app.include_router(ai_detection_router)
app.include_router(ratings_router)
app.include_router(dashboard_router)
app.include_router(photos_router)
app.include_router(work_assignment_router)
app.include_router(leaderboard_router)
app.include_router(alerts_router)
app.include_router(reference_router)


@app.on_event("startup")
def initialize_database():
    try:
        init_db()
    except Exception as error:
        # Keep health/docs available when an external database is temporarily down.
        print(f"Database initialization skipped: {error}")


@app.get("/")
def root():
    return {"message": "SIH MPLADS Monitoring API", "status": "running"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
