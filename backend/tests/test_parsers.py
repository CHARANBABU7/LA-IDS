from app.services.linux_auth_parser import parse_line as parse_auth_line
from app.services.apache_parser import parse_line as parse_apache_line


def test_auth_parser_parses_failed_login():
    line = "Jul 21 09:12:01 server sshd[1001]: Failed password for admin from 192.168.1.5 port 22 ssh2"
    result = parse_auth_line(line)

    assert result["parsed"] is True
    assert result["source_ip"] == "192.168.1.5"
    assert result["username"] == "admin"
    assert result["status_code"] == 401


def test_auth_parser_parses_accepted_login():
    line = "Jul 21 09:13:45 server sshd[1005]: Accepted password for deploy from 10.0.0.8 port 22 ssh2"
    result = parse_auth_line(line)

    assert result["parsed"] is True
    assert result["status_code"] == 200


def test_auth_parser_handles_garbage_line():
    line = "this is not a real log line at all"
    result = parse_auth_line(line)

    assert result["parsed"] is False
    assert result["raw_log"] == line
    assert result["source_ip"] is None


def test_auth_parser_handles_empty_line():
    result = parse_auth_line("")
    assert result["parsed"] is False
    assert result["message"] == "empty line"


def test_apache_parser_parses_404():
    line = '203.0.113.9 - - [21/Jul/2026:10:12:04 +0000] "GET /admin HTTP/1.1" 404 210'
    result = parse_apache_line(line)

    assert result["parsed"] is True
    assert result["source_ip"] == "203.0.113.9"
    assert result["status_code"] == 404
    assert result["endpoint"] == "/admin"
    assert result["request_method"] == "GET"


def test_apache_parser_handles_garbage_line():
    result = parse_apache_line("not a real access log line")
    assert result["parsed"] is False