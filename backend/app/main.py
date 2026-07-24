from fastapi import FastAPI
from app.database import Base, engine
from app.models import Alert
from app.routers import logs
from app.routers import detection
from app.routers import alerts   
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from app.error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)
from app.routers import investigation
from app.routers import dashboard
from sqlalchemy import text
from app.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware




Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Log Analysis & Intrusion Detection System",
    description="A lightweight SIEM-style platform for log analysis and intrusion detection.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(logs.router)
app.include_router(detection.router)
app.include_router(alerts.router) 
app.include_router(investigation.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to LA-IDS 🚀",
        "status": "Backend is running"
    }
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Verifies the API is running AND the database is reachable —
    a real health check, not just a ping. Useful for deployment
    platforms (Render/Vercel) to detect a broken DB connection
    even if the web process itself is technically alive.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "unreachable"

    return {
        "status": "ok" if db_status == "connected" else "degraded",
        "database": db_status,
    }
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

