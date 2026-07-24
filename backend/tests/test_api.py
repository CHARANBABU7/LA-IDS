import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from sqlalchemy.pool import StaticPool

@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,   # ← add this
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_upload_log_file(client):
    content = "Jul 21 09:12:01 server sshd[1001]: Failed password for admin from 192.168.1.5 port 22 ssh2\n"
    response = client.post(
        "/logs/upload",
        files={"file": ("test.log", content, "text/plain")},
        data={"log_type": "linux_auth"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_lines"] == 1
    assert body["parsed_count"] == 1


def test_duplicate_upload_rejected(client):
    content = "Jul 21 09:12:01 server sshd[1001]: Failed password for admin from 192.168.1.5 port 22 ssh2\n"
    client.post("/logs/upload", files={"file": ("test.log", content, "text/plain")}, data={"log_type": "linux_auth"})
    response = client.post("/logs/upload", files={"file": ("test.log", content, "text/plain")}, data={"log_type": "linux_auth"})

    assert response.status_code == 409


def test_list_logs_returns_uploaded_data(client):
    content = "Jul 21 09:12:01 server sshd[1001]: Failed password for admin from 192.168.1.5 port 22 ssh2\n"
    client.post("/logs/upload", files={"file": ("test.log", content, "text/plain")}, data={"log_type": "linux_auth"})

    response = client.get("/logs/")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_nonexistent_alert_returns_404(client):
    response = client.get("/alerts/9999")
    assert response.status_code == 404


def test_alert_status_update_case_insensitive(client):
    # First, generate a real alert via a brute-force upload + detect
    lines = "\n".join(
        f"Jul 21 10:00:{i:02d} server sshd[{2000+i}]: Failed password for admin from 203.0.113.9 port 22 ssh2"
        for i in range(6)
    )
    client.post("/logs/upload", files={"file": ("bf.log", lines, "text/plain")}, data={"log_type": "linux_auth"})
    client.post("/detect/run")

    alerts = client.get("/alerts/").json()
    assert len(alerts) == 1
    alert_id = alerts[0]["id"]

    response = client.patch(f"/alerts/{alert_id}/status", json={"status": "RESOLVED"})
    assert response.status_code == 200
    assert response.json()["status"] == "resolved"

def test_dashboard_summary_reflects_data(client):
    # Upload a brute-force-triggering file and detect it
    lines = "\n".join(
        f"Jul 21 10:00:{i:02d} server sshd[{2000+i}]: Failed password for admin from 203.0.113.9 port 22 ssh2"
        for i in range(6)
    )
    client.post("/logs/upload", files={"file": ("bf.log", lines, "text/plain")}, data={"log_type": "linux_auth"})
    client.post("/detect/run")

    response = client.get("/dashboard/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["total_alerts"] == 1
    assert body["open_alerts"] == 1
    assert body["severity_breakdown"]["medium"] == 1
    assert body["attack_type_breakdown"][0]["attack_type"] == "ssh_bruteforce"


def test_alert_investigate_returns_related_logs(client):
    lines = "\n".join(
        f"Jul 21 10:00:{i:02d} server sshd[{2000+i}]: Failed password for admin from 203.0.113.9 port 22 ssh2"
        for i in range(6)
    )
    client.post("/logs/upload", files={"file": ("bf.log", lines, "text/plain")}, data={"log_type": "linux_auth"})
    client.post("/detect/run")

    alert_id = client.get("/alerts/").json()[0]["id"]
    response = client.get(f"/alerts/{alert_id}/investigate")

    assert response.status_code == 200
    body = response.json()
    assert len(body["related_logs"]) == 6
    assert all(log["source_ip"] == "203.0.113.9" for log in body["related_logs"])


def test_investigate_ip_aggregates_logs_and_alerts(client):
    lines = "\n".join(
        f"Jul 21 10:00:{i:02d} server sshd[{2000+i}]: Failed password for admin from 203.0.113.9 port 22 ssh2"
        for i in range(6)
    )
    client.post("/logs/upload", files={"file": ("bf.log", lines, "text/plain")}, data={"log_type": "linux_auth"})
    client.post("/detect/run")

    response = client.get("/investigate/ip/203.0.113.9")
    assert response.status_code == 200
    body = response.json()
    assert body["total_log_entries"] == 6
    assert body["total_alerts"] == 1


def test_logs_csv_export_returns_csv(client):
    content = "Jul 21 09:12:01 server sshd[1001]: Failed password for admin from 192.168.1.5 port 22 ssh2\n"
    client.post("/logs/upload", files={"file": ("test.log", content, "text/plain")}, data={"log_type": "linux_auth"})

    response = client.get("/logs/export/csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "192.168.1.5" in response.text


def test_alerts_csv_export_returns_csv(client):
    lines = "\n".join(
        f"Jul 21 10:00:{i:02d} server sshd[{2000+i}]: Failed password for admin from 203.0.113.9 port 22 ssh2"
        for i in range(6)
    )
    client.post("/logs/upload", files={"file": ("bf.log", lines, "text/plain")}, data={"log_type": "linux_auth"})
    client.post("/detect/run")

    response = client.get("/alerts/export/csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "ssh_bruteforce" in response.text


def test_health_endpoint_reports_database_connected(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "connected"