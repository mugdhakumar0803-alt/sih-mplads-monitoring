from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.database import init_db

from app.auth.routes import router as auth_router
from app.routers.works import router as works_router
from app.routers.grievances import router as grievances_router
from app.routers.fund_release import router as fund_release_router
from app.routers.chatbot import router as chatbot_router
from app.routers.ai_detection import router as ai_detection_router
from app.routers.compliance import router as compliance_router
from app.routers.photos import router as photos_router

app = FastAPI(
    title="SIH MPLADS Monitoring & Accountability Platform",
    description="AI-powered MPLADS monitoring and accountability platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(works_router)
app.include_router(grievances_router)
app.include_router(fund_release_router)
app.include_router(chatbot_router)
app.include_router(ai_detection_router)
app.include_router(compliance_router)
app.include_router(photos_router)


@app.on_event("startup")
def initialize_database():
    try:
        init_db()
    except Exception as error:
        # Keep health/docs available when an external database is temporarily down.
        print(f"Database initialization skipped: {error}")


@app.get("/")
def root():
    return {
        "message": "SIH MPLADS Monitoring API",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
from app.routers.dashboard import router as dashboard_router
...
app.include_router(dashboard_router)