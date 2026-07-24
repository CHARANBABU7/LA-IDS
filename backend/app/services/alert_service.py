from sqlalchemy.orm import Session
from app.models import Alert
from app.services.detector import DetectedThreat
from datetime import datetime


def save_new_alerts(db: Session, threats: list[DetectedThreat]) -> dict:
    """
    Persists detected threats as Alert rows, skipping ones that already
    have an open alert for the same (source_ip, attack_type) pair —
    prevents duplicate alerts every time detection re-runs.
    """
    created = 0
    skipped = 0

    for threat in threats:
        existing = (
            db.query(Alert)
            .filter(
                Alert.source_ip == threat["source_ip"],
                Alert.attack_type == threat["attack_type"],
                Alert.status == "open",
            )
            .first()
        )

        if existing:
            skipped += 1
            continue

        alert = Alert(
            attack_type=threat["attack_type"],
            severity=threat["severity"],
            source_ip=threat["source_ip"],
            timestamp=datetime.utcnow(),
            description=threat["description"],
            recommendation=threat["recommendation"],
            status="open",
            source_log_ids=",".join(str(i) for i in threat["source_log_ids"]),
        )
        db.add(alert)
        created += 1

    db.commit()
    return {"created": created, "skipped_duplicates": skipped}