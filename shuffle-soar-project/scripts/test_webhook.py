#!/usr/bin/env python3
"""
test_webhook.py
===============
Quick connectivity check for a Shuffle webhook - sends a minimal ping
payload and reports whether Shuffle received it. Use this before running
simulate_alert.py to confirm the URL and network path are correct.

Usage:
    python3 scripts/test_webhook.py http://localhost:3001/api/v1/hooks/abc123
"""

import sys
import json
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print("The 'requests' library is not installed. Run: pip install requests --break-system-packages")
    sys.exit(1)


def test_webhook(url: str) -> None:
    ping_payload = {
        "test": True,
        "source": "test_webhook.py",
        "message": "Connectivity check from Shuffle SOAR project scripts",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    print(f"Sending test ping to: {url}")
    try:
        resp = requests.post(url, json=ping_payload, timeout=10)
    except requests.exceptions.ConnectionError:
        print("FAILED - could not connect. Is Shuffle running? (docker-compose up -d in the Shuffle/ folder)")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("FAILED - request timed out after 10 seconds.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"FAILED - {e}")
        sys.exit(1)

    if resp.status_code in (200, 201, 202):
        print(f"SUCCESS - Shuffle responded with status {resp.status_code}")
        print(f"Response body: {resp.text[:300]}")
    else:
        print(f"UNEXPECTED RESPONSE - status {resp.status_code}")
        print(f"Response body: {resp.text[:300]}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/test_webhook.py <webhook_url>")
        sys.exit(1)
    test_webhook(sys.argv[1])
