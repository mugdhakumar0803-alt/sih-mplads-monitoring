from fastapi import FastAPI

from app.routers.ai_detection import router as ai_detection_router

app = FastAPI(
    title="SIH MPLADS Monitoring & Accountability Platform",
    description="AI-powered MPLADS monitoring and accountability platform",
    version="0.1.0",
)

app.include_router(ai_detection_router)


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
