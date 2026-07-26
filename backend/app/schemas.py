from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import field_validator


class ORMBase(BaseModel):
    class Config:
        from_attributes = True


class DetectionRunResponse(ORMBase):
    """Normalized summary of a detection run — no raw Alert rows dumped."""
    threats_found: int
    alerts_created: int
    duplicates_skipped: int

class LogUploadResponse(ORMBase):
    """
    Normalized response after upload. Now includes the automatic
    detection cycle's results, since upload always triggers detection —
    one call does the whole pipeline: parse, store, detect, alert.
    """
    filename: str
    total_lines: int
    parsed_count: int
    unparsed_count: int
    detection: DetectionRunResponse | None = None



class LogResponse(ORMBase):
    """Normalized log record returned to the frontend."""
    id: int
    timestamp: Optional[datetime]
    source_ip: Optional[str]
    username: Optional[str]
    request_method: Optional[str]
    endpoint: Optional[str]
    status_code: Optional[int]
    message: str
    raw_log: str

class AlertResponse(ORMBase):
    """Normalized alert record returned to the frontend."""
    id: int
    attack_type: str
    severity: str
    source_ip: str
    timestamp: datetime
    description: str
    recommendation: str
    status: str
class AlertStatus(str, Enum):
    """Constrained set of valid alert states — prevents typos like 'resloved'."""
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"



class AlertStatusUpdate(ORMBase):
    """Incoming request body for updating an alert's status."""
    status: AlertStatus

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value: str) -> str:
        """
        Accept any casing (Resolved, RESOLVED, resolved) and normalize
        to lowercase before enum validation — analysts shouldn't get
        a 422 over a capitalization typo.
        """
        if isinstance(value, str):
            return value.lower()
        return value
class AlertWithLogsResponse(ORMBase):
    """Alert detail view including the actual log evidence that triggered it."""
    id: int
    attack_type: str
    severity: str
    source_ip: str
    timestamp: datetime
    description: str
    recommendation: str
    status: str
    related_logs: list[LogResponse]


class IPInvestigationResponse(ORMBase):
    """Full activity summary for a single IP — the core investigation view."""
    source_ip: str
    total_log_entries: int
    total_alerts: int
    logs: list[LogResponse]
    alerts: list[AlertResponse]

class SeverityBreakdown(ORMBase):
    """Count of open alerts per severity level."""
    low: int
    medium: int
    high: int


class AttackTypeBreakdown(ORMBase):
    """Count of alerts per attack type — powers a bar/pie chart."""
    attack_type: str
    count: int


class TopAttackerEntry(ORMBase):
    """A source IP ranked by how many alerts it has triggered."""
    source_ip: str
    alert_count: int


class DashboardSummaryResponse(ORMBase):
    """
    Single normalized response covering everything a SOC dashboard
    needs at a glance — avoids the frontend making several separate
    calls just to render one screen.
    """
    total_logs: int
    total_alerts: int
    open_alerts: int
    resolved_alerts: int
    severity_breakdown: SeverityBreakdown
    attack_type_breakdown: list[AttackTypeBreakdown]
    top_attackers: list[TopAttackerEntry]