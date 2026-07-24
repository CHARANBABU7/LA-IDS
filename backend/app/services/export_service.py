import csv
import io
from sqlalchemy.orm import Session
from app.models import Log, Alert


def export_logs_to_csv(db: Session) -> str:
    """Generates CSV content for all stored logs."""
    logs = db.query(Log).order_by(Log.timestamp).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "timestamp", "source_ip", "username", "request_method",
        "endpoint", "status_code", "message", "raw_log",
    ])

    for log in logs:
        writer.writerow([
            log.id, log.timestamp, log.source_ip, log.username,
            log.request_method, log.endpoint, log.status_code,
            log.message, log.raw_log,
        ])

    return output.getvalue()


def export_alerts_to_csv(db: Session) -> str:
    """Generates CSV content for all stored alerts."""
    alerts = db.query(Alert).order_by(Alert.timestamp).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "attack_type", "severity", "source_ip", "timestamp",
        "description", "recommendation", "status",
    ])

    for alert in alerts:
        writer.writerow([
            alert.id, alert.attack_type, alert.severity, alert.source_ip,
            alert.timestamp, alert.description, alert.recommendation, alert.status,
        ])

    return output.getvalue()