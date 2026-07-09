#!/usr/bin/env python3
"""
simulate_alert.py
==================
Sends a sample Wazuh-formatted alert to a Shuffle webhook so you can test
and demo each playbook without needing a live SIEM event.

Usage:
    python3 scripts/simulate_alert.py --type phishing
    python3 scripts/simulate_alert.py --type malware
    python3 scripts/simulate_alert.py --type bruteforce
    python3 scripts/simulate_alert.py --type suspicious_ip
    python3 scripts/simulate_alert.py --type malware --webhook-url http://localhost:3001/api/v1/hooks/abc123

Requires the corresponding SHUFFLE_WEBHOOK_* value to be set in your .env
(or pass --webhook-url directly). Falls back to printing the payload only
if no URL is available, so you can inspect what would be sent.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    requests = None


def load_dotenv(path=".env"):
    """Minimal .env loader - avoids requiring python-dotenv as a dependency."""
    env = {}
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip()
    return env


SAMPLE_ALERTS = {
    "phishing": {
        "rule": {"id": "31103", "level": 10, "description": "Phishing URL detected in mail content"},
        "data": {
            "srcip": "185.220.101.45",
            "url": "http://secure-verify-account-update.tk/login.php",
            "dstuser": "j.doe",
        },
        "agent": {"name": "MAIL-GW-01", "id": "002", "ip": "10.0.0.12"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    },
    "malware": {
        "rule": {"id": "87105", "level": 12, "description": "File integrity monitoring: new executable detected"},
        "syscheck": {
            "path": "/home/user/Downloads/invoice_2024.exe",
            "file": "invoice_2024.exe",
            "event": "added",
            "md5_after": "44d88612fea8a8f36de82e1278abb02f",
            "sha1_after": "3395856ce81f2b7382dee72602f798b642f14140",
            "sha256_after": "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0",
        },
        "agent": {"name": "WKS-FIN-07", "id": "014", "ip": "10.0.5.22"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    },
    "bruteforce": {
        "rule": {"id": "100120", "level": 10, "description": "SSH brute force: 5+ failed logins from same source"},
        "data": {
            "srcip": "103.45.22.180",
            "dstuser": "root",
            "protocol": "ssh",
            "win": {"eventdata": {"failureCount": "12"}},
        },
        "agent": {"name": "PROD-WEB-03", "id": "021", "ip": "10.0.2.8"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    },
    "suspicious_ip": {
        "rule": {"id": "100130", "level": 7, "description": "Outbound connection to non-allow-listed IP"},
        "data": {
            "dest_ip": "91.215.85.142",
            "src_host": "WKS-DEV-11",
            "dest_port": "443",
            "process_name": "powershell.exe",
        },
        "agent": {"id": "030"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    },
}

WEBHOOK_ENV_KEYS = {
    "phishing": "SHUFFLE_WEBHOOK_PHISHING",
    "malware": "SHUFFLE_WEBHOOK_MALWARE",
    "bruteforce": "SHUFFLE_WEBHOOK_BRUTEFORCE",
    "suspicious_ip": "SHUFFLE_WEBHOOK_SUSPICIOUS_IP",
}


def main():
    parser = argparse.ArgumentParser(description="Simulate a Wazuh alert for Shuffle playbook testing")
    parser.add_argument("--type", required=True, choices=list(SAMPLE_ALERTS.keys()), help="Which sample alert to send")
    parser.add_argument("--webhook-url", help="Override the webhook URL instead of reading it from .env")
    args = parser.parse_args()

    payload = SAMPLE_ALERTS[args.type]
    env = load_dotenv()
    webhook_url = args.webhook_url or env.get(WEBHOOK_ENV_KEYS[args.type])

    print(f"--- Simulated '{args.type}' alert payload ---")
    print(json.dumps(payload, indent=2))
    print("--------------------------------------------")

    if not webhook_url:
        print("\nNo webhook URL provided and none found in .env. Payload printed above only.")
        print(f"Set {WEBHOOK_ENV_KEYS[args.type]} in your .env or pass --webhook-url to actually send it.")
        sys.exit(0)

    if requests is None:
        print("\nThe 'requests' library is not installed. Run: pip install requests --break-system-packages")
        sys.exit(1)

    print(f"\nSending to: {webhook_url}")
    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        print(f"Response status: {resp.status_code}")
        print(f"Response body: {resp.text[:500]}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
