import re
from datetime import datetime
from typing import Optional
 
from app.services.linux_auth_parser import ParsedLogLine
 
 
# Matches Apache/Nginx "combined" log format, e.g.:
# 203.0.113.9 - - [21/Jul/2026:10:12:04 +0000] "GET /admin/config.php HTTP/1.1" 404 512
#
# NOTE: the request line is captured as one whole quoted string rather
# than assuming the endpoint has no whitespace. Some payloads (SQLi,
# XSS) can legitimately contain literal, unencoded spaces depending on
# how the upstream server logged them, so splitting on \S+ alone would
# silently fail to parse those lines. See _split_request() below.
ACCESS_LOG_PATTERN = re.compile(
    r'^(?P<source_ip>[\d.]+)\s+\S+\s+\S+\s+'
    r'\[(?P<timestamp>[^\]]+)\]\s+'
    r'"(?P<request>[^"]*)"\s+'
    r'(?P<status>\d{3})\s+\S+'
)
 
 
def _split_request(request: str) -> tuple[Optional[str], Optional[str]]:
    """
    Splits a raw request line into (method, endpoint), tolerating
    spaces inside the endpoint/query string itself. Assumes the method
    is the first token and, if present, a trailing HTTP/x.x protocol
    token is stripped from the end — everything remaining in between
    (spaces included) is treated as the endpoint.
    """
    parts = request.split(" ")
    if len(parts) < 2:
        return None, None
 
    method = parts[0]
    remainder = parts[1:]
 
    # Strip a trailing protocol token like "HTTP/1.1" if present.
    if remainder and remainder[-1].upper().startswith("HTTP/"):
        remainder = remainder[:-1]
 
    endpoint = " ".join(remainder) if remainder else None
    return method, endpoint
 
 
def _build_timestamp(raw_ts: str) -> Optional[datetime]:
    """
    Apache/Nginx timestamps include the full date, unlike auth.log —
    so no "assume current year" workaround needed here.
    Format: 21/Jul/2026:10:12:04 +0000
    """
    try:
        # Strip timezone offset for simplicity; keep parsing lenient.
        date_part = raw_ts.split(" ")[0]
        return datetime.strptime(date_part, "%d/%b/%Y:%H:%M:%S")
    except ValueError:
        return None
 
 
def parse_line(raw_line: str) -> ParsedLogLine:
    """
    Parse a single Apache/Nginx combined-format access log line.
    Same contract as linux_auth_parser.parse_line: never raises,
    always returns a full ParsedLogLine, unparsed lines keep raw_log.
    """
    raw_line = raw_line.strip()
 
    if not raw_line:
        return ParsedLogLine(
            parsed=False, timestamp=None, source_ip=None, username=None,
            request_method=None, endpoint=None, status_code=None,
            message="empty line", raw_log=raw_line,
        )
 
    match = ACCESS_LOG_PATTERN.match(raw_line)
 
    if not match:
        return ParsedLogLine(
            parsed=False, timestamp=None, source_ip=None, username=None,
            request_method=None, endpoint=None, status_code=None,
            message="unparsed", raw_log=raw_line,
        )
 
    groups = match.groupdict()
    timestamp = _build_timestamp(groups["timestamp"])
    method, endpoint = _split_request(groups["request"])
 
    if method is None:
        return ParsedLogLine(
            parsed=False, timestamp=timestamp, source_ip=groups["source_ip"],
            username=None, request_method=None, endpoint=None, status_code=None,
            message="unparsed request line", raw_log=raw_line,
        )
 
    return ParsedLogLine(
        parsed=True,
        timestamp=timestamp,
        source_ip=groups["source_ip"],
        username=None,  # access logs don't carry auth identity
        request_method=method,
        endpoint=endpoint,
        status_code=int(groups["status"]),
        message=f"{method} {endpoint} -> {groups['status']}",
        raw_log=raw_line,
    )
 
 
def parse_log_file(content: str) -> list[ParsedLogLine]:
    """Parse every line in an uploaded Apache/Nginx access log."""
    lines = content.splitlines()
    return [parse_line(line) for line in lines]
 