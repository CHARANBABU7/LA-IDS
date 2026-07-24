from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Log, Alert


def get_dashboard_summary(db: Session) -> dict:
    """
    Aggregates counts across logs and alerts into one summary view.
    Kept as simple grouped COUNT queries — no need for anything fancier
    at this data scale, and it stays readable per the project's own
    'prefer readable over clever' rule.
    """
    total_logs = db.query(func.count(Log.id)).scalar() or 0
    total_alerts = db.query(func.count(Alert.id)).scalar() or 0
    open_alerts = db.query(func.count(Alert.id)).filter(Alert.status == "open").scalar() or 0
    resolved_alerts = db.query(func.count(Alert.id)).filter(Alert.status == "resolved").scalar() or 0

    severity_counts = (
        db.query(Alert.severity, func.count(Alert.id))
        .filter(Alert.status == "open")
        .group_by(Alert.severity)
        .all()
    )
    severity_map = {severity: count for severity, count in severity_counts}
    severity_breakdown = {
        "low": severity_map.get("low", 0),
        "medium": severity_map.get("medium", 0),
        "high": severity_map.get("high", 0),
    }

    attack_type_counts = (
        db.query(Alert.attack_type, func.count(Alert.id))
        .group_by(Alert.attack_type)
        .all()
    )
    attack_type_breakdown = [
        {"attack_type": attack_type, "count": count}
        for attack_type, count in attack_type_counts
    ]

    top_attackers_raw = (
        db.query(Alert.source_ip, func.count(Alert.id).label("alert_count"))
        .group_by(Alert.source_ip)
        .order_by(func.count(Alert.id).desc())
        .limit(5)
        .all()
    )
    top_attackers = [
        {"source_ip": ip, "alert_count": count}
        for ip, count in top_attackers_raw
    ]

    return {
        "total_logs": total_logs,
        "total_alerts": total_alerts,
        "open_alerts": open_alerts,
        "resolved_alerts": resolved_alerts,
        "severity_breakdown": severity_breakdown,
        "attack_type_breakdown": attack_type_breakdown,
        "top_attackers": top_attackers,
    }