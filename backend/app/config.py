"""
Central configuration for all tunable detection parameters.
Change sensitivity here — never inside detector.py itself.
"""

# SSH brute-force detection
BRUTE_FORCE_THRESHOLD = 5
BRUTE_FORCE_WINDOW_MINUTES = 10

# Endpoint scanning detection
SCAN_THRESHOLD = 10
SCAN_WINDOW_MINUTES = 5

# Web attack detection (SQLi, XSS, directory traversal)
WEB_ATTACK_THRESHOLD = 3
WEB_ATTACK_WINDOW_MINUTES = 10

# High-severity escalation thresholds
BRUTE_FORCE_HIGH_SEVERITY_COUNT = 10
SCAN_HIGH_SEVERITY_COUNT = 20
WEB_ATTACK_HIGH_SEVERITY_COUNT = 6