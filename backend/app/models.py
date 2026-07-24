from sqlalchemy import Column, Integer, String, DateTime, Text

from app.database import Base

from datetime import datetime

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    source_ip = Column(String)
    username = Column(String)
    request_method = Column(String)
    endpoint = Column(String)
    status_code = Column(Integer)
    message = Column(Text)
    raw_log = Column(Text)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    attack_type = Column(String)
    severity = Column(String)
    source_ip = Column(String)
    timestamp = Column(DateTime)
    description = Column(Text)
    recommendation = Column(Text)
    status = Column(String)
    source_log_ids = Column(String, nullable=True)  
class DetectorState(Base):
    """
    Tracks scan progress PER detector type — not globally. This is
    critical: if one shared cursor advanced past a log range, a brand
    new detector added later would never see that range again, even
    though it had never scanned it. Each rule gets its own row.
    """
    __tablename__ = "detector_state"

    id = Column(Integer, primary_key=True)
    detector_name = Column(String, unique=True, nullable=False, index=True)
    last_scanned_log_id = Column(Integer, default=0, nullable=False)

class UploadedFile(Base):
    """
    Tracks a hash of every uploaded file's content, so re-uploading
    the identical file is rejected instead of silently duplicating logs.
    """
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True)
    file_hash = Column(String, unique=True, nullable=False, index=True)
    filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)