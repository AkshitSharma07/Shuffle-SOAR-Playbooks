# API Reference

Quick reference for every external API surface this project touches.

## VirusTotal Public API v2

**Base URL:** `https://www.virustotal.com/vtapi/v2`
**Auth:** API key as a query parameter (`apikey=...`)
**Free tier limits:** 4 requests/minute, 500 requests/day

| Endpoint | Method | Used For | Key Response Fields |
|---|---|---|---|
| `/file/report` | GET | Hash lookup (malware ID) | `positives`, `total`, `scans`, `permalink`, `suggested_threat_label` |
| `/url/report` | GET | URL reputation | `positives`, `total`, `scan_date`, `permalink` |
| `/domain/report` | GET | Domain reputation | `categories`, `detected_urls`, `whois`, `resolutions` |
| `/ip-address/report` | GET | IP reputation | `detected_urls`, `detected_communicating_samples`, `country`, `as_owner` |

Get a free key at https://www.virustotal.com/gui/sign-in under your profile's API Key section.

## Wazuh API

**Base URL:** `https://<wazuh-manager>:55000`
**Auth:** JWT bearer token (obtained via `/security/user/authenticate`)

| Endpoint | Method | Used For |
|---|---|---|
| `/agents/{agent_id}/group/{group_id}` | PUT | Move an agent into an isolation group (Playbook 2) |
| `/active-response` | POST | Trigger active-response commands: block-ip, kill-process, quarantine-file |

Full API documentation: https://documentation.wazuh.com/current/user-manual/api/reference.html

## Shuffle SOAR Concepts (not a traditional REST API)

Shuffle workflows are configured through its UI/JSON, not called directly as an API by this project's playbooks. Key concepts referenced throughout the playbook JSON files:

| Concept | Meaning |
|---|---|
| `$trigger.body` | Raw payload received by the webhook trigger |
| `$steps.<step_id>.<field>` | References output from an earlier step in the same workflow |
| `$ENV.<VAR_NAME>` | Pulls a value from Shuffle's environment variable store (configured per-workflow or globally) |

Shuffle's own API documentation (for programmatic workflow management, if you go beyond the UI): https://shuffler.io/docs

## Firewall API (Generic)

This project treats the firewall integration generically since the actual product varies by environment (pfSense, FortiGate, Palo Alto, etc.). The playbooks call:

```
POST {FIREWALL_API_URL}/block
Authorization: Bearer {FIREWALL_API_KEY}
Body: { "action": "block", "type": "ip"|"domain", "value": "...", "reason": "...", "created_by": "Shuffle-SOAR-Auto" }
```

Replace this with your actual vendor's documented block/rule-creation endpoint. Most NGFWs expose a REST API for dynamic address objects or block lists that this maps onto directly.

## Slack API

**Used action:** `chat.postMessage`
**Required OAuth scope:** `chat:write`
**Auth:** Bot token (`xoxb-...`) from a Slack App under **OAuth & Permissions**

Setup: https://api.slack.com/apps -> Create New App -> OAuth & Permissions -> add `chat:write` scope -> Install to Workspace -> copy Bot User OAuth Token.

## TheHive API (optional)

**Base URL:** `https://<thehive-instance>:9000`
**Auth:** API key, bearer token

| Endpoint | Method | Used For |
|---|---|---|
| `/api/case` | POST | Create a new investigation case |
| `/api/case/{case_id}/artifact` | POST | Attach an IOC as a tracked observable |

Full documentation: https://docs.thehive-project.org/thehive/

## GeoIP (Playbook 4)

This project's example config uses ipinfo.io as a placeholder. Any GeoIP provider with a simple REST lookup works — ip-api.com and MaxMind GeoLite2 (self-hosted) are free alternatives if you'd rather not depend on an external paid quota.
