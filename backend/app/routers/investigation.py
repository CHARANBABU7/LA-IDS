from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import IPInvestigationResponse
from app.services.investigation_service import investigate_ip

router = APIRouter(prefix="/investigate", tags=["Investigation"])


@router.get("/ip/{source_ip}", response_model=IPInvestigationResponse)
def get_ip_activity(source_ip: str, db: Session = Depends(get_db)):
    """Full activity report for a given IP: every log and alert tied to it."""
    return investigate_ip(db, source_ip)