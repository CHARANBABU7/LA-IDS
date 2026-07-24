from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import AlertResponse
from app.services.alert_query_service import get_alerts
from fastapi import HTTPException
from app.schemas import AlertStatusUpdate
from app.services.alert_query_service import get_alert_by_id, update_alert_status
from app.schemas import AlertWithLogsResponse
from app.services.investigation_service import get_logs_for_alert
from fastapi.responses import StreamingResponse
from app.services.export_service import export_alerts_to_csv


router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/", response_model=list[AlertResponse])
def list_alerts(
    severity: str | None = None,
    status: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """Retrieve stored alerts, optionally filtered by severity or status."""
    return get_alerts(db, severity=severity, status=status, limit=limit, offset=offset)

@router.get("/export/csv")
def export_alerts(db: Session = Depends(get_db)):
    """Download all stored alerts as a CSV file."""
    csv_content = export_alerts_to_csv(db)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=alerts_export.csv"},
    )

@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Retrieve a single alert by ID for detailed investigation."""
    alert = get_alert_by_id(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    return alert

@router.get("/{alert_id}/investigate", response_model=AlertWithLogsResponse)
def investigate_alert(alert_id: int, db: Session = Depends(get_db)):
    """Retrieve an alert along with the raw log evidence that triggered it."""
    alert = get_alert_by_id(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    related_logs = get_logs_for_alert(db, alert)

    return AlertWithLogsResponse(
        id=alert.id, attack_type=alert.attack_type, severity=alert.severity,
        source_ip=alert.source_ip, timestamp=alert.timestamp,
        description=alert.description, recommendation=alert.recommendation,
        status=alert.status, related_logs=related_logs,
    )


@router.patch("/{alert_id}/status", response_model=AlertResponse)
def update_alert(alert_id: int, payload: AlertStatusUpdate, db: Session = Depends(get_db)):
    """
    Update an alert's status — how an analyst actually works a case:
    open -> investigating -> resolved (or false_positive).
    """
    alert = update_alert_status(db, alert_id, payload.status.value)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    return alert


