from sqlalchemy.orm import Session
from typing import Optional
from app.models import Alert


def get_alerts(
    db: Session,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Alert]:
    """Retrieve alerts with optional filtering by severity or status."""
    query = db.query(Alert)

    if severity:
        query = query.filter(Alert.severity == severity)

    if status:
        query = query.filter(Alert.status == status)

    return (
        query.order_by(Alert.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
def get_alert_by_id(db: Session, alert_id: int) -> Alert | None:
    """Fetch a single alert by ID, or None if it doesn't exist."""
    return db.query(Alert).filter(Alert.id == alert_id).first()


def update_alert_status(db: Session, alert_id: int, new_status: str) -> Alert | None:
    """
    Update an alert's status (e.g. open -> investigating -> resolved).
    Returns None if the alert doesn't exist so the router can 404 cleanly.
    """
    alert = get_alert_by_id(db, alert_id)
    if not alert:
        return None

    alert.status = new_status
    db.commit()
    db.refresh(alert)
    return alert