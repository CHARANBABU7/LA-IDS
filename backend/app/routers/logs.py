from fastapi import APIRouter, UploadFile, File, Depends , Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.linux_auth_parser import parse_log_file
from app.services.log_service import save_parsed_logs
from app.schemas import LogUploadResponse
from app.schemas import LogResponse
from app.services.log_service import get_logs
from fastapi import HTTPException
from app.services.log_service import get_log_by_id
from enum import Enum
from app.services import apache_parser
from app.services.upload_tracking_service import compute_file_hash, is_duplicate_upload, record_upload
from fastapi.responses import StreamingResponse
from app.services.export_service import export_logs_to_csv


router = APIRouter(prefix="/logs", tags=["Logs"])

class LogType(str, Enum):
    """Supported log formats. Add new values here as new parsers are built."""
    LINUX_AUTH = "linux_auth"
    APACHE = "apache"
PARSERS = {
    LogType.LINUX_AUTH: parse_log_file,
    LogType.APACHE: apache_parser.parse_log_file,
}
@router.post("/upload", response_model=LogUploadResponse)
async def upload_log_file(
    file: UploadFile = File(...),
    log_type: LogType = Form(LogType.LINUX_AUTH),
    db: Session = Depends(get_db),
):
    """
    Accept a raw log file, parse it using the parser matching log_type,
    and persist every line. Rejects exact re-uploads of the same file
    content to prevent duplicate log entries and inflated detection counts.
    """
    raw_bytes = await file.read()
    file_hash = compute_file_hash(raw_bytes)

    if is_duplicate_upload(db, file_hash):
        raise HTTPException(
            status_code=409,
            detail=f"This exact file ('{file.filename}') has already been uploaded. "
                   "Duplicate uploads are rejected to prevent inflated log/alert counts.",
        )

    content = raw_bytes.decode("utf-8", errors="replace")
    parser_fn = PARSERS[log_type]
    parsed_lines = parser_fn(content)
    summary = save_parsed_logs(db, parsed_lines)
    record_upload(db, file_hash, file.filename)

    return LogUploadResponse(
        filename=file.filename,
        total_lines=summary["total_lines"],
        parsed_count=summary["parsed_count"],
        unparsed_count=summary["unparsed_count"],
    )
@router.get("/", response_model=list[LogResponse])
def list_logs(
    source_ip: str | None = None,
    parsed_only: bool = False,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """Retrieve stored logs, optionally filtered by IP or parse status."""
    return get_logs(db, source_ip=source_ip, parsed_only=parsed_only, limit=limit, offset=offset)


@router.get("/export/csv")
def export_logs(db: Session = Depends(get_db)):
    """Download all stored logs as a CSV file."""
    csv_content = export_logs_to_csv(db)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=logs_export.csv"},
    )


@router.get("/{log_id}", response_model=LogResponse)
def get_log(log_id: int, db: Session = Depends(get_db)):
    """Retrieve a single log entry by ID."""
    log = get_log_by_id(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail=f"Log {log_id} not found")
    return log

