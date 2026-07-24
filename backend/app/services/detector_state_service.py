from sqlalchemy.orm import Session
from app.models import DetectorState


def get_last_scanned_id(db: Session, detector_name: str) -> int:
    """Returns the highest Log.id this specific detector has evaluated. 0 if never run."""
    state = db.query(DetectorState).filter(DetectorState.detector_name == detector_name).first()
    return state.last_scanned_log_id if state else 0


def update_last_scanned_id(db: Session, detector_name: str, new_last_id: int) -> None:
    """Advance this detector's cursor independently of every other detector's progress."""
    state = db.query(DetectorState).filter(DetectorState.detector_name == detector_name).first()
    if state:
        state.last_scanned_log_id = new_last_id
    else:
        state = DetectorState(detector_name=detector_name, last_scanned_log_id=new_last_id)
        db.add(state)
    db.commit()