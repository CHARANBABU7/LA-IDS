from datetime import timedelta
from collections import defaultdict
from typing import TypedDict, Optional
from sqlalchemy.orm import Session
from app.models import Log
import re
from app.config import (
    BRUTE_FORCE_THRESHOLD, BRUTE_FORCE_WINDOW_MINUTES,
    SCAN_THRESHOLD, SCAN_WINDOW_MINUTES,
    WEB_ATTACK_THRESHOLD, WEB_ATTACK_WINDOW_MINUTES,
    BRUTE_FORCE_HIGH_SEVERITY_COUNT, SCAN_HIGH_SEVERITY_COUNT, WEB_ATTACK_HIGH_SEVERITY_COUNT,
)


class DetectedThreat(TypedDict):
    """Uniform shape for any rule's output, regardless of attack type."""
    attack_type: str
    severity: str
    source_ip: str
    description: str
    recommendation: str
    occurrence_count: int
    source_log_ids: list[int]


def _severity_for_count(count: int) -> str:
    if count >= BRUTE_FORCE_HIGH_SEVERITY_COUNT:
        return "high"
    if count >= BRUTE_FORCE_THRESHOLD:
        return "medium"
    return "low"


def detect_ssh_bruteforce(db: Session, since_log_id: int = 0) -> list[DetectedThreat]:
    """
    Scans Failed-password SSH logs, groups by source_ip, and flags
    any IP with >= BRUTE_FORCE_THRESHOLD failures within a rolling
    BRUTE_FORCE_WINDOW_MINUTES window.
    """
    failed_logs = (
        db.query(Log)
        .filter(Log.status_code == 401, Log.source_ip.isnot(None), Log.id > since_log_id)
        .order_by(Log.source_ip, Log.timestamp)
        .all()
    )

    grouped: dict[str, list[Log]] = defaultdict(list)
    for log in failed_logs:
        grouped[log.source_ip].append(log)

    threats: list[DetectedThreat] = []
    window = timedelta(minutes=BRUTE_FORCE_WINDOW_MINUTES)

    for source_ip, logs in grouped.items():
        logs_with_ts = [l for l in logs if l.timestamp is not None]
        if len(logs_with_ts) < BRUTE_FORCE_THRESHOLD:
            continue

        for i, start_log in enumerate(logs_with_ts):
            window_end = start_log.timestamp + window
            matching_logs = [l for l in logs_with_ts[i:] if l.timestamp <= window_end]
            count = len(matching_logs)

            if count >= BRUTE_FORCE_THRESHOLD:
                threats.append(DetectedThreat(
                    attack_type="ssh_bruteforce",
                    severity=_severity_for_count(count),
                    source_ip=source_ip,
                    description=(
                        f"{count} failed SSH login attempts from {source_ip} "
                        f"within {BRUTE_FORCE_WINDOW_MINUTES} minutes."
                    ),
                    recommendation=(
                        f"Investigate {source_ip}. Consider temporary IP ban "
                        "and reviewing targeted usernames for credential exposure."
                    ),
                    occurrence_count=count,
                    source_log_ids=[l.id for l in matching_logs],
                ))
                break

    return threats


def detect_endpoint_scanning(db: Session, since_log_id: int = 0) -> list[DetectedThreat]:
    """
    Flags IPs generating many 404s in a short window — a signature
    of automated endpoint/vuln scanning rather than normal traffic.
    """
    not_found_logs = (
        db.query(Log)
        .filter(Log.status_code == 404, Log.source_ip.isnot(None), Log.id > since_log_id)
        .order_by(Log.source_ip, Log.timestamp)
        .all()
    )

    grouped: dict[str, list[Log]] = defaultdict(list)
    for log in not_found_logs:
        grouped[log.source_ip].append(log)

    threats: list[DetectedThreat] = []
    window = timedelta(minutes=SCAN_WINDOW_MINUTES)

    for source_ip, logs in grouped.items():
        logs_with_ts = [l for l in logs if l.timestamp is not None]
        if len(logs_with_ts) < SCAN_THRESHOLD:
            continue

        for i, start_log in enumerate(logs_with_ts):
            window_end = start_log.timestamp + window
            matching_logs = [l for l in logs_with_ts[i:] if l.timestamp <= window_end]
            count = len(matching_logs)

            if count >= SCAN_THRESHOLD:
                threats.append(DetectedThreat(
                    attack_type="endpoint_scanning",
                    severity="medium" if count < SCAN_HIGH_SEVERITY_COUNT else "high",
                    source_ip=source_ip,
                    description=(
                        f"{count} 404 responses from {source_ip} within "
                        f"{SCAN_WINDOW_MINUTES} minutes — likely automated scanning."
                    ),
                    recommendation=(
                        f"Investigate {source_ip} for vulnerability scanning "
                        "activity. Consider rate limiting or blocking."
                    ),
                    occurrence_count=count,
                    source_log_ids=[l.id for l in matching_logs],
                ))
                break

    return threats

SQLI_PATTERNS = re.compile(
    r"(\bUNION\b.*\bSELECT\b|\bOR\b\s+['\"]?1['\"]?\s*=\s*['\"]?1|--\s|;\s*DROP\b|'\s*OR\s*')",
    re.IGNORECASE,
)
XSS_PATTERNS = re.compile(
    r"(<script|javascript:|onerror\s*=|onload\s*=|<img[^>]+onerror)",
    re.IGNORECASE,
)
TRAVERSAL_PATTERNS = re.compile(
    r"(\.\./|\.\.\\|%2e%2e%2f|%2e%2e/|\.\.%2f|/etc/passwd|/etc/shadow|windows/system32)",
    re.IGNORECASE,
)

def _detect_web_attack_pattern(
    db: Session,
    pattern: re.Pattern,
    attack_type: str,
    since_log_id: int = 0,
) -> list[DetectedThreat]:
    """
    Shared logic for any regex-based web attack detection (SQLi, XSS,
    traversal). Groups matching logs by source_ip, flags IPs with
    enough hits within the window.
    """
    logs = (
        db.query(Log)
        .filter(Log.endpoint.isnot(None), Log.source_ip.isnot(None), Log.id > since_log_id)
        .order_by(Log.source_ip, Log.timestamp)
        .all()
    )

    matching_logs_all = [l for l in logs if pattern.search(l.endpoint)]

    grouped: dict[str, list[Log]] = defaultdict(list)
    for log in matching_logs_all:
        grouped[log.source_ip].append(log)

    threats: list[DetectedThreat] = []
    window = timedelta(minutes=WEB_ATTACK_WINDOW_MINUTES)

    for source_ip, ip_logs in grouped.items():
        logs_with_ts = [l for l in ip_logs if l.timestamp is not None]
        if len(logs_with_ts) < WEB_ATTACK_THRESHOLD:
            continue

        for i, start_log in enumerate(logs_with_ts):
            window_end = start_log.timestamp + window
            matching_logs = [l for l in logs_with_ts[i:] if l.timestamp <= window_end]
            count = len(matching_logs)

            if count >= WEB_ATTACK_THRESHOLD:
                threats.append(DetectedThreat(
                    attack_type=attack_type,
                    severity="high" if count >= WEB_ATTACK_HIGH_SEVERITY_COUNT else "medium",
                    source_ip =source_ip,
                    description=(
                        f"{count} {attack_type.replace('_', ' ')} attempts detected "
                        f"from {source_ip} within {WEB_ATTACK_WINDOW_MINUTES} minutes."
                    ),
                    recommendation=(
                        f"Investigate {source_ip} immediately. Review application input "
                        "validation and consider blocking this IP."
                    ),
                    occurrence_count=count,
                    source_log_ids=[l.id for l in matching_logs],
                ))
                break

    return threats


def detect_sql_injection(db: Session, since_log_id: int = 0) -> list[DetectedThreat]:
    return _detect_web_attack_pattern(db, SQLI_PATTERNS, "sql_injection", since_log_id)


def detect_xss(db: Session, since_log_id: int = 0) -> list[DetectedThreat]:
    return _detect_web_attack_pattern(db, XSS_PATTERNS, "xss_attempt", since_log_id)


def detect_directory_traversal(db: Session, since_log_id: int = 0) -> list[DetectedThreat]:
    return _detect_web_attack_pattern(db, TRAVERSAL_PATTERNS, "directory_traversal", since_log_id)


# def run_all_detectors(db: Session, since_log_id: int = 0) -> list[DetectedThreat]:
#     """
#     Entry point for detection. Add new rule functions here as they're
#     built (e.g. detect_sql_injection, detect_path_traversal) — this
#     is the ONLY place that needs to change when a new rule is added.
#     """
#     threats: list[DetectedThreat] = []
#     threats.extend(detect_ssh_bruteforce(db, since_log_id))
#     threats.extend(detect_endpoint_scanning(db, since_log_id))
#     threats.extend(detect_sql_injection(db, since_log_id))
#     threats.extend(detect_xss(db, since_log_id))
#     threats.extend(detect_directory_traversal(db, since_log_id))
#     return threats

