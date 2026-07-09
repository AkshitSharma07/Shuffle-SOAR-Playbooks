# Contributing

This started as a personal portfolio project, but improvements are welcome.

## Ways to contribute

- **New playbooks** — additional alert types (e.g. ransomware behavior, data exfiltration, insider threat) following the same pattern: trigger, parse, enrich, score, branch, contain/log, notify.
- **Additional enrichment sources** — AbuseIPDB, Shodan, MISP, or AlienVault OTX alongside or instead of VirusTotal.
- **Threshold tuning guidance** — if you've run these playbooks against real alert volume and have data on false-positive rates at different thresholds, that's extremely useful to document.
- **Bug fixes** — typos in the JSON, broken references, outdated Wazuh rule IDs (Wazuh's stock ruleset does change between versions).

## How to submit a change

1. Fork the repository
2. Create a branch for your change (`git checkout -b add-ransomware-playbook`)
3. Make your changes — if adding a playbook, please also add: the workflow JSON in `playbooks/`, a diagram in `diagrams/` (the `diagrams/build_flow.py` helper can generate consistent-looking flowcharts), and a section in `docs/PLAYBOOK_GUIDE.md`
4. Open a pull request describing what the change does and why

## Code style

- Playbook JSON files should stay consistent with the existing structure (`id`, `name`, `description`, `triggers`, `workflow.steps`, `metadata`).
- Shell scripts should be POSIX-compatible where reasonable and use `set -euo pipefail`.
- Python scripts should run on 3.8+ with no dependencies beyond `requests` (kept intentionally minimal so the project stays easy to clone and run).

## Reporting issues

Open a GitHub issue with the playbook name, what you expected, and what actually happened. If it's related to a specific Wazuh rule ID, please note your Wazuh version, since rule IDs have shifted between major versions.
