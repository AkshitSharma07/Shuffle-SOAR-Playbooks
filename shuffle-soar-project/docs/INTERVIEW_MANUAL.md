# Interview Manual (Quick Reference)

This is the condensed, in-repo version of the full project manual. The complete formatted manual with workflow diagrams is `SOAR_Playbook_Project_Manual.docx` (kept outside this repo / shared separately, since it's a personal interview-prep document rather than project documentation).

## 30-Second Summary

I designed and built four SOAR playbooks in Shuffle, an open-source orchestration platform, automating incident response for phishing, malware, brute-force, and suspicious-IP alerts from a Wazuh SIEM. Each playbook receives an alert via webhook, extracts the IOC, enriches it with the VirusTotal API, scores the threat, and — above a confidence threshold — automatically contains it (block, isolate, or kill-process) while notifying the SOC team. Below threshold, it logs for monitoring instead of acting. I documented each playbook as a structured workflow diagram and published the project to GitHub with a blog post walkthrough.

## Per-Playbook One-Liners

- **Phishing:** Wazuh phishing rule -> extract URL/domain -> VirusTotal -> block domain + source IP if score > threshold -> notify
- **Malware:** Wazuh FIM alert -> hash lookup (MD5+SHA256) -> identify malware family -> isolate endpoint + kill process if confirmed -> open TheHive case
- **Brute Force:** 5+ failed logins -> VT IP reputation -> block if malicious OR high attempt count -> sync to Wazuh active-response
- **Suspicious IP:** Outbound connection -> GeoIP + VT -> composite score -> block only if high-confidence, otherwise log enrichment for analyst triage

## Why These Design Choices

| Choice | Reasoning |
|---|---|
| Threshold-based scoring, not binary | A single AV hit is noise. Forces a confidence floor before acting. |
| Combined signals (e.g. VT + attempt count) | Any single signal alone produces false positives. |
| Fail toward "log and alert," never silent skip | If VT is down/rate-limited, a human still gets visibility instead of nothing happening. |
| Every auto-action also notifies | No silent containment - SOC always has an audit trail. |
| Used Shuffle (free/OSS) over paid SOAR | Reproducible - anyone can clone and run it; same orchestration concepts transfer to Splunk SOAR/XSOAR. |

## Numbers to Use (Framed as Modeled, Not Measured)

- MTTD: ~45 min manual -> ~2 min automated
- MTTR: ~4 hours manual -> ~8 min automated
- IOC enrichment time: ~30 min manual -> ~45 sec automated

State these as "modeled improvement based on typical Tier-1 triage time" unless you've run this against real alert volume.

## MITRE ATT&CK Coverage

- Phishing: T1566, T1566.001, T1566.002
- Malware: T1204, T1059, T1055
- Brute Force: T1110
- Suspicious IP: T1071, T1102

## Likely Follow-Ups

**"What if VirusTotal is down?"** -> Fail-safe design: defaults to logging and alerting a human, never silently skips containment or blocks on no data.

**"How do you avoid false-positive containment?"** -> Threshold-based scoring + combining two independent signals before auto-blocking (e.g. hash + domain, or VT + GeoIP).

**"How would this scale to a real enterprise SOC?"** -> Add IOC caching to respect API rate limits, route ambiguous scores to human-in-the-loop approval, feed outcomes into a metrics dashboard.

**"Why not Splunk SOAR or XSOAR?"** -> Cost and reproducibility. Shuffle is free/self-hostable so anyone can clone and run it; the orchestration concepts (trigger, enrich, decide, contain, notify) transfer directly.

**"Walk me through one playbook end to end."** -> Use the malware playbook — clearest narrative: FIM alert -> hash lookup -> family ID -> isolate -> case creation -> notify.

For the full version with workflow diagrams, step tables, and the complete interview-answer scripts per playbook, see the companion Word document.
