import re
from datetime import datetime
from typing import Optional, TypedDict


class ParsedLogLine(TypedDict):
    """
    Uniform shape returned for EVERY line, parsed or not.
    parsed=False rows still carry raw_log so nothing is ever lost.
    """
    parsed: bool
    timestamp: Optional[datetime]
    source_ip: Optional[str]
    username: Optional[str]
    request_method: Optional[str]
    endpoint: Optional[str]
    status_code: Optional[int]
    message: str
    raw_log: str


# Matches common Linux auth.log SSH failure/success lines, e.g.:
# "Jul 21 10:15:32 server sshd[1234]: Failed password for admin from 192.168.1.5 port 22 ssh2"
AUTH_LOG_PATTERN = re.compile(
    r"^(?P<month>\w{3})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+"
    r"\S+\s+sshd\[\d+\]:\s+"
    r"(?P<result>Failed|Accepted)\s+password\s+for\s+"
    r"(?:invalid user\s+)?(?P<username>\S+)\s+from\s+"
    r"(?P<source_ip>[\d.]+)\s+port\s+\d+"
)


def _build_timestamp(month: str, day: str, time_str: str) -> Optional[datetime]:
    """
    Linux auth logs omit the year, so we assume the current year.
    Good enough for a portfolio project; flagged here so it's easy
    to find if real multi-year log ingestion is ever needed.
    """
    try:
        current_year = datetime.now().year
        return datetime.strptime(
            f"{current_year} {month} {day} {time_str}", "%Y %b %d %H:%M:%S"
        )
    except ValueError:
        return None


def parse_line(raw_line: str) -> ParsedLogLine:
    """
    Parse a single Linux auth log line.
    Never raises — unparseable lines return parsed=False with
    raw_log preserved so analysts can review them later.
    """
    raw_line = raw_line.strip()

    if not raw_line:
        return ParsedLogLine(
            parsed=False, timestamp=None, source_ip=None, username=None,
            request_method=None, endpoint=None, status_code=None,
            message="empty line", raw_log=raw_line,
        )

    match = AUTH_LOG_PATTERN.match(raw_line)

    if not match:
        return ParsedLogLine(
            parsed=False, timestamp=None, source_ip=None, username=None,
            request_method=None, endpoint=None, status_code=None,
            message="unparsed", raw_log=raw_line,
        )

    groups = match.groupdict()
    timestamp = _build_timestamp(groups["month"], groups["day"], groups["time"])
    result = groups["result"]  # "Failed" or "Accepted"

    return ParsedLogLine(
        parsed=True,
        timestamp=timestamp,
        source_ip=groups["source_ip"],
        username=groups["username"],
        request_method="SSH",
        endpoint=None,
        status_code=200 if result == "Accepted" else 401,
        message=f"{result} password for {groups['username']}",
        raw_log=raw_line,
    )


def parse_log_file(content: str) -> list[ParsedLogLine]:
    """Parse every line in an uploaded log file's content."""
    lines = content.splitlines()
    return [parse_line(line) for line in lines]