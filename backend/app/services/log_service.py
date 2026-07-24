from sqlalchemy.orm import Session
from app.models import Log
from app.services.linux_auth_parser import ParsedLogLine
from typing import Optional

def save_parsed_logs(db: Session, parsed_lines: list[ParsedLogLine]) -> dict:
    """
    Bulk-insert parsed log lines and return summary counts.
    No branching on parsed/unparsed here — that logic already
    lives entirely in the parser, so this stays a dumb persistence step.
    """
    log_objects = [
        Log(
            timestamp=line["timestamp"],
            source_ip=line["source_ip"],
            username=line["username"],
            request_method=line["request_method"],
            endpoint=line["endpoint"],
            status_code=line["status_code"],
            message=line["message"],
            raw_log=line["raw_log"],
        )
        for line in parsed_lines
    ]

    db.bulk_save_objects(log_objects)
    db.commit()

    parsed_count = sum(1 for line in parsed_lines if line["parsed"])
    unparsed_count = len(parsed_lines) - parsed_count

    return {
        "total_lines": len(parsed_lines),
        "parsed_count": parsed_count,
        "unparsed_count": unparsed_count,
    }
def get_logs(
    db: Session,
    source_ip: Optional[str] = None,
    parsed_only: bool = False,
    limit: int = 100,
    offset: int = 0,
) -> list[Log]:
    """
    Retrieve logs with optional filtering.
    parsed_only=True excludes rows where every structured field is NULL
    (i.e. the unparsed/raw rows) — useful for an analyst who only wants
    actionable data, while raw rows remain queryable for audits.
    """
    query = db.query(Log)

    if source_ip:
        query = query.filter(Log.source_ip == source_ip)

    if parsed_only:
        query = query.filter(Log.source_ip.isnot(None))

    return (
        query.order_by(Log.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

def get_log_by_id(db: Session, log_id: int) -> Log | None:
    """Fetch a single log entry by ID, or None if it doesn't exist."""
    return db.query(Log).filter(Log.id == log_id).first()