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


DETECTOR_REGISTRY = {
    "ssh_bruteforce": detect_ssh_bruteforce,
    "endpoint_scanning": detect_endpoint_scanning,
    "sql_injection": detect_sql_injection,
    "xss_attempt": detect_xss,
    "directory_traversal": detect_directory_traversal,
}

router = APIRouter(prefix="/detect", tags=["Detection"])




@router.post("/run", response_model=DetectionRunResponse)
def run_detection(db: Session = Depends(get_db)):
    """
    Runs every registered detector against logs it individually hasn't
    seen yet. Each detector tracks its own progress, so adding a new
    rule later never causes it to miss log ranges other detectors
    already scanned.
    """
    all_threats = []
    latest_log_id = db.query(func.max(Log.id)).scalar() or 0

    for detector_name, detector_fn in DETECTOR_REGISTRY.items():
        since_id = get_last_scanned_id(db, detector_name)
        threats = detector_fn(db, since_log_id=since_id)
        all_threats.extend(threats)
        update_last_scanned_id(db, detector_name, latest_log_id)

    result = save_new_alerts(db, all_threats)

    return DetectionRunResponse(
        threats_found=len(all_threats),
        alerts_created=result["created"],
        duplicates_skipped=result["skipped_duplicates"],
    )


# @router.post("/reset-cursor")
# def reset_detection_cursor(db: Session = Depends(get_db)):
#     """TEMPORARY — resets the detection cursor to force a full rescan."""
#     update_last_scanned_id(db, 0)
#     return {"message": "Cursor reset to 0"}