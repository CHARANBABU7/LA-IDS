import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Log
from app.services.detector import detect_ssh_bruteforce, detect_endpoint_scanning


@pytest.fixture
def db_session():
    """Fresh in-memory SQLite DB per test — no interference with real data."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


def _make_log(source_ip: str, status_code: int, timestamp: datetime) -> Log:
    return Log(
        timestamp=timestamp, source_ip=source_ip, username="test",
        request_method="SSH", endpoint=None, status_code=status_code,
        message="test", raw_log="test",
    )


def test_bruteforce_triggers_at_threshold(db_session):
    base_time = datetime(2026, 7, 21, 10, 0, 0)
    for i in range(6):  # 6 failures, threshold is 5
        db_session.add(_make_log("203.0.113.9", 401, base_time + timedelta(seconds=i * 3)))
    db_session.commit()

    threats = detect_ssh_bruteforce(db_session)
    assert len(threats) == 1
    assert threats[0]["source_ip"] == "203.0.113.9"
    assert threats[0]["attack_type"] == "ssh_bruteforce"


def test_bruteforce_does_not_trigger_below_threshold(db_session):
    base_time = datetime(2026, 7, 21, 10, 0, 0)
    for i in range(4):  # only 4 failures, below threshold of 5
        db_session.add(_make_log("203.0.113.9", 401, base_time + timedelta(seconds=i * 3)))
    db_session.commit()

    threats = detect_ssh_bruteforce(db_session)
    assert len(threats) == 0


def test_bruteforce_respects_since_log_id_cursor(db_session):
    base_time = datetime(2026, 7, 21, 10, 0, 0)
    logs = [_make_log("203.0.113.9", 401, base_time + timedelta(seconds=i * 3)) for i in range(6)]
    db_session.add_all(logs)
    db_session.commit()

    last_id = logs[-1].id
    # Everything already scanned — should find nothing new
    threats = detect_ssh_bruteforce(db_session, since_log_id=last_id)
    assert len(threats) == 0


def test_endpoint_scanning_triggers_at_threshold(db_session):
    base_time = datetime(2026, 7, 21, 11, 0, 0)
    for i in range(10):  # threshold is 10
        db_session.add(_make_log("203.0.113.50", 404, base_time + timedelta(seconds=i * 2)))
    db_session.commit()

    threats = detect_endpoint_scanning(db_session)
    assert len(threats) == 1
    assert threats[0]["attack_type"] == "endpoint_scanning"