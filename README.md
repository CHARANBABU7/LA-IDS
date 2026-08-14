# LA-IDS — Log Analysis & Intrusion Detection System

A full-stack security monitoring platform that ingests server logs, analyzes suspicious activity, detects common attack patterns, and provides a centralized dashboard for security investigation and alert management.

## Overview

**LA-IDS (Log Analysis & Intrusion Detection System)** is designed to turn raw server logs into actionable security information.

The system supports log ingestion and parsing, rule-based threat detection, alert generation, investigation workflows, analytics, and visualization through a web-based security dashboard.

### Key capabilities

* Upload and analyze server log files
* Parse Linux SSH authentication logs
* Parse Apache/Nginx access logs
* Detect multiple common attack patterns
* Use sliding time windows for behavioral detection
* Prevent duplicate log processing
* Generate and manage security alerts
* Investigate suspicious IP addresses and alerts
* Monitor detection statistics through a dashboard
* Explore ingested logs
* Analyze security activity through charts
* Export security data as CSV
* Track alert lifecycle from **Open → Resolved**

---

## Detection Engine

LA-IDS currently detects **7 attack categories**:

| Detection                  | Description                                                       |
| -------------------------- | ----------------------------------------------------------------- |
| SSH Brute Force            | Detects repeated failed SSH authentication attempts               |
| Endpoint Scanning          | Identifies repeated requests to non-existent endpoints            |
| SQL Injection              | Detects suspicious SQL injection patterns in requests             |
| Cross-Site Scripting (XSS) | Identifies common XSS payload patterns                            |
| Directory Traversal        | Detects attempts to access files outside the intended directory   |
| Command Injection          | Identifies suspicious operating-system command injection patterns |
| Sensitive File Exposure    | Detects probing for sensitive files and configuration resources   |

### Behavioral detection

Some detections use time-based thresholds rather than simply matching individual log entries.

For example:

* **SSH brute force:** 5+ failed login attempts within a 10-minute sliding window
* **Endpoint scanning:** 10+ HTTP 404 responses within a 5-minute sliding window

This allows the system to identify patterns of activity rather than treating every suspicious request independently.

---

## Detection Workflow

```text
                    ┌─────────────────┐
                    │   Log Upload    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Log Validation  │
                    │  & Deduplication│
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Log Parser      │
                    │ SSH / Web Logs  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Detection Engine│
                    │   7 Detectors   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Alert Generation│
                    └────────┬────────┘
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
          ┌───────────────┐     ┌───────────────┐
          │ Investigation │     │   Analytics   │
          └───────────────┘     └───────────────┘
                  │                     │
                  └──────────┬──────────┘
                             ▼
                    ┌─────────────────┐
                    │ Security        │
                    │ Dashboard       │
                    └─────────────────┘
```

---

## Features

### Log Ingestion

* File-based log ingestion
* SHA-256 hashing for duplicate upload detection
* Automatic parsing based on supported log formats
* Persistent storage of processed log information

### Security Alerts

* Automatic alert creation when detection rules trigger
* Attack classification
* Severity information
* Source IP information
* Alert investigation
* Alert status management
* Open/resolved lifecycle

### Dashboard

The dashboard provides a centralized view of security activity, including:

* Total logs
* Detected threats
* Alert statistics
* Attack-type distribution
* Severity distribution
* Security activity trends

### Log Explorer

Allows analysts to inspect processed log records and investigate suspicious activity at the individual log-entry level.

### Analytics

Provides visual analysis of detected security events and attack patterns using interactive charts.

### Investigation

LA-IDS provides investigation-oriented views for analyzing:

* Individual alerts
* Suspicious IP addresses
* Related security activity
* Detection history

### Data Export

Security information can be exported in CSV format for further analysis or reporting.

---

## Tech Stack

### Backend

* **Python**
* **FastAPI**
* **SQLAlchemy**
* **SQLite**
* **Pydantic**
* **Uvicorn**
* **Pytest**

### Frontend

* **React**
* **Vite**
* **Tailwind CSS**
* **Axios**
* **Recharts**
* **Lucide React**
* **React Router**

---

## Project Structure

```text
LA-IDS/
│
├── backend/
│   ├── app/
│   │   ├── ...
│   │   └── ...
│   ├── tests/
│   ├── requirements.txt
│   └── pytest.ini
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── .gitignore
├── package.json
└── package-lock.json
```

---

## Getting Started

### Prerequisites

Make sure the following are installed:

* Python 3.10+
* Node.js 18+
* npm

### 1. Clone the repository

```bash
git clone https://github.com/CHARANBABU7/LA-IDS.git
cd LA-IDS
```

### 2. Start the backend

```bash
cd backend

python -m venv venv
```

Activate the virtual environment.

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn app.main:app --reload
```

The backend will be available through the local FastAPI server.

### 3. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL provided by Vite.

---

## Testing

The backend includes automated tests covering the API, log parsing, and detection functionality.

Run:

```bash
cd backend
pytest
```

---

## Security Detection Examples

### SSH Brute Force

```text
Failed password for invalid user admin from 192.168.1.100
Failed password for invalid user admin from 192.168.1.100
...
```

Repeated authentication failures from the same source within the configured time window can trigger a brute-force alert.

### Endpoint Scanning

```text
GET /admin HTTP/1.1
GET /backup HTTP/1.1
GET /phpmyadmin HTTP/1.1
GET /config HTTP/1.1
```

Repeated requests resulting in `404` responses can indicate endpoint reconnaissance.

### Web Attack Detection

Suspicious request patterns are analyzed for indicators associated with:

* SQL injection
* XSS
* Directory traversal
* Command injection
* Sensitive-file probing

---

## API

The backend exposes REST APIs for:

* Log upload
* Log retrieval
* Alert management
* Alert investigation
* IP investigation
* Dashboard statistics
* Analytics
* CSV export
* Health monitoring

FastAPI also provides interactive API documentation when the backend is running.

---

## Design Goals

LA-IDS was built around several core security-monitoring concepts:

* **Detection over raw log collection**
* **Behavioral analysis using time windows**
* **Actionable security alerts**
* **Investigation-oriented workflows**
* **Separation between ingestion, detection, and presentation**
* **A centralized SOC-style monitoring experience**

---

## Current Status

**Project Status: Complete**

The core application is implemented and tested, with the backend detection engine, REST API, frontend dashboard, log exploration, alert management, analytics, investigation workflows, and export functionality operational.

---

## Future Improvements

Potential future enhancements include:

* Real-time log streaming
* SIEM integration
* Threat intelligence enrichment
* Authentication and role-based access control
* Automated alert notifications
* More advanced correlation between events
* Machine-learning-assisted anomaly detection
* Containerized deployment
* Distributed log ingestion

---

## Author

**Charan Babu**

Cybersecurity | Python | Web Security | DSA

GitHub: [@CHARANBABU7](https://github.com/CHARANBABU7)
