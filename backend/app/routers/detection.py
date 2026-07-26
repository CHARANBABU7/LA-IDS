from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
# from app.services.detector import run_all_detectors
from app.services.alert_service import save_new_alerts
from app.schemas import DetectionRunResponse
from sqlalchemy import func
from app.models import Log
from app.services.detector_state_service import get_last_scanned_id, update_last_scanned_id
from app.services.detector import (
    detect_ssh_bruteforce, detect_endpoint_scanning,
    detect_sql_injection, detect_xss, detect_directory_traversal,
)
from app.services.detector_state_service import get_last_scanned_id, update_last_scanned_id
from sqlalchemy import func
from app.models import Log
from app.services.detector_state_service import update_last_scanned_id
from app.services.detection_runner import run_detection_cycle


# DETECTOR_REGISTRY = {
#     "ssh_bruteforce": detect_ssh_bruteforce,
#     "endpoint_scanning": detect_endpoint_scanning,
#     "sql_injection": detect_sql_injection,
#     "xss_attempt": detect_xss,
#     "directory_traversal": detect_directory_traversal,
# }

router = APIRouter(prefix="/detect", tags=["Detection"])





@router.post("/run", response_model=DetectionRunResponse)
def run_detection(db: Session = Depends(get_db)):
    """Manually trigger a detection cycle over any logs not yet scanned."""
    result = run_detection_cycle(db)
    return DetectionRunResponse(**result)


# @router.post("/reset-cursor")
# def reset_detection_cursor(db: Session = Depends(get_db)):
#     """TEMPORARY — resets the detection cursor to force a full rescan."""
#     update_last_scanned_id(db, 0)
#     return {"message": "Cursor reset to 0"}