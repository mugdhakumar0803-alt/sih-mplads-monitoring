from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from app.database import Base, engine
from app.models.user import User
from app.models.work import Work
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

app = FastAPI(
    title="SIH MPLADS Monitoring & Accountability Platform",
    description="AI-powered MPLADS monitoring and accountability platform",
    version="0.2.0",
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(works_router)
app.include_router(grievances_router)
app.include_router(fund_release_router)
app.include_router(chatbot_router)
app.include_router(reports_router)
app.include_router(audit_router)
app.include_router(compliance_router)
app.include_router(ai_detection_router)


@app.get("/")
def root():
    return {"message": "SIH MPLADS Monitoring API", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
