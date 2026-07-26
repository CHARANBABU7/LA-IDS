from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Log
from app.services.detector import (
    detect_ssh_bruteforce, detect_endpoint_scanning,
    detect_sql_injection, detect_xss, detect_directory_traversal,
    detect_command_injection, detect_sensitive_file_access,
)
from app.services.detector_state_service import get_last_scanned_id, update_last_scanned_id
from app.services.alert_service import save_new_alerts

# Single source of truth for every registered rule. Adding a new attack
# type = one new entry here. Nothing else needs to change.
DETECTOR_REGISTRY = {
    "ssh_bruteforce": detect_ssh_bruteforce,
    "endpoint_scanning": detect_endpoint_scanning,
    "sql_injection": detect_sql_injection,
    "xss_attempt": detect_xss,
    "directory_traversal": detect_directory_traversal,
    "command_injection": detect_command_injection,
    "sensitive_file_access": detect_sensitive_file_access,
}


def run_detection_cycle(db: Session) -> dict:
    """
    Runs every registered detector against logs it hasn't seen yet.
    Shared by both the manual /detect/run endpoint and the automatic
    post-upload trigger, so behavior is identical either way.
    """
    all_threats = []
    latest_log_id = db.query(func.max(Log.id)).scalar() or 0

    for name, detector_fn in DETECTOR_REGISTRY.items():
        since_id = get_last_scanned_id(db, name)
        threats = detector_fn(db, since_log_id=since_id)
        all_threats.extend(threats)
        update_last_scanned_id(db, name, latest_log_id)

    result = save_new_alerts(db, all_threats)

    return {
        "threats_found": len(all_threats),
        "alerts_created": result["created"],
        "duplicates_skipped": result["skipped_duplicates"],
    }