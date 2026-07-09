# Playbook Guide

Reference for what each playbook does, when it fires, and how to tune it.

## Playbook 1 — Phishing Email Response
**File:** `playbooks/01_phishing_email.json`
**Trigger:** Wazuh rules 31101 / 31103 / 31530 (phishing URL/content signatures) or custom rule 100101
**Enrichment:** VirusTotal URL report + domain report
**Decision threshold:** `positives > 5` out of total AV engines
**Containment on match:** Block domain + block source IP at firewall, sync to Wazuh active-response
**Notification:** Slack `#soc-alerts`, email to SOC distro

### Tuning
- Lower the `positives > 5` threshold if your environment has a low alert volume and you want more aggressive auto-blocking.
- Add a second condition checking `vt_domain_categories` for newly-registered or parked domains for an extra signal beyond raw AV detections.

## Playbook 2 — Malware Hash Detection & Endpoint Isolation
**File:** `playbooks/02_malware_detection.json`
**Trigger:** Wazuh FIM/syscheck rules 87100 / 87105 / 553 or custom rule 100110
**Enrichment:** VirusTotal file report (MD5 + SHA256 cross-check)
**Decision threshold:** `positives > 3`
**Containment on match:** Isolate endpoint (Wazuh agent group change), kill process via active-response
**Below threshold:** Quarantine the file only, leave the host on the network
**Case management:** Auto-creates a TheHive case with the hash as an observable and a standard investigation task list
**Notification:** Slack `#soc-critical`

### Tuning
- The `positives > 3` threshold is intentionally low because file hashes are exact-match - a few detections on a hash is much stronger signal than a few detections on a URL, which can include benign redirectors.
- If you don't run TheHive, remove steps 9-10 (`create_thehive_case`, `add_ioc_to_case`) and keep the isolation + Slack steps.

## Playbook 3 — Brute Force Attack Response
**File:** `playbooks/03_brute_force.json`
**Trigger:** Wazuh frequency rules 5712/5716/5720 or custom rules 100120 (SSH) / 100121 (RDP)
**Enrichment:** VirusTotal IP reputation report
**Decision logic:** `vt_malicious == true OR attempt_count >= 10` (combined signal, not VT alone)
**Containment on match:** Block source IP at firewall (24h duration), sync to Wazuh active-response
**Below threshold:** Log for continued monitoring, no block
**Notification:** Slack `#soc-alerts`

### Tuning
- The combined logic exists because attempt count alone produces false positives (e.g. a misconfigured monitoring tool retrying logins) and VT reputation alone can miss freshly-stood-up attacker infrastructure with no history yet.
- Adjust the 24h block duration in the firewall action body if your environment prefers permanent blocks for any confirmed brute-force source.

## Playbook 4 — Suspicious IP Enrichment
**File:** `playbooks/04_suspicious_ip.json`
**Trigger:** Custom rule 100130 (outbound connection to non-private/non-allow-listed IP)
**Enrichment:** GeoIP lookup + VirusTotal IP scan
**Decision logic:** Composite score = `(is_hosting_provider ? 30 : 0) + (detected_samples_count * 10)`, block only if `> 40`
**Containment on match:** Block outbound to the destination IP
**Below threshold:** No block - full enrichment is still logged and pushed to a dashboard
**Notification:** None by default (this is a triage aid, not a critical-alert playbook) - add a Slack step if you want one

### Tuning
- This playbook is deliberately conservative (`> 40` is a meaningfully high score) because it's designed as an *enrichment* aid first, blocking second. If you want it more aggressive, lower the threshold or add a third signal (e.g. passive DNS history depth).
- The dashboard push step assumes a generic internal API; replace `DASHBOARD_API_URL` with wherever your team actually reviews enrichment data, or remove the step if you don't have one.

## General Notes on All Playbooks

- Every playbook reads credentials from `$ENV.*` variables, never hardcoded - see `configs/shuffle_env.example`.
- Every containment action is mirrored by a notification step - nothing blocks silently.
- Each playbook fails toward "log and alert a human" rather than silently skipping containment if an enrichment call errors out. If you extend these playbooks, preserve that fail-safe behavior rather than wrapping enrichment failures in a try/continue that swallows the error.
- Thresholds in this guide are starting points, not universal constants. Tune them against your own environment's alert volume and false-positive tolerance.
