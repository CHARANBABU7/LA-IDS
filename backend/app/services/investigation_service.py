from sqlalchemy.orm import Session
from app.models import Log, Alert


def get_logs_for_alert(db: Session, alert: Alert) -> list[Log]:
    """Fetch the actual Log rows that triggered a given alert."""
    if not alert.source_log_ids:
        return []
    log_ids = [int(i) for i in alert.source_log_ids.split(",")]
    return db.query(Log).filter(Log.id.in_(log_ids)).order_by(Log.timestamp).all()


def investigate_ip(db: Session, source_ip: str) -> dict:
    """
    Pulls every log and alert associated with a given IP — the single
    view an analyst needs to answer 'what has this IP actually done?'
    """
    logs = db.query(Log).filter(Log.source_ip == source_ip).order_by(Log.timestamp).all()
    alerts = db.query(Alert).filter(Alert.source_ip == source_ip).order_by(Alert.timestamp).all()

    return {
        "source_ip": source_ip,
        "total_log_entries": len(logs),
        "total_alerts": len(alerts),
        "logs": logs,
        "alerts": alerts,
    }