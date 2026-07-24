import hashlib
from sqlalchemy.orm import Session
from app.models import UploadedFile


def compute_file_hash(content: bytes) -> str:
    """SHA-256 hash of raw file bytes — content-based, not filename-based,
    so renaming a file doesn't bypass the duplicate check."""
    return hashlib.sha256(content).hexdigest()


def is_duplicate_upload(db: Session, file_hash: str) -> bool:
    """Check if this exact file content has already been uploaded."""
    return db.query(UploadedFile).filter(UploadedFile.file_hash == file_hash).first() is not None


def record_upload(db: Session, file_hash: str, filename: str) -> None:
    """Record this file's hash so future identical uploads are caught."""
    record = UploadedFile(file_hash=file_hash, filename=filename)
    db.add(record)
    db.commit()