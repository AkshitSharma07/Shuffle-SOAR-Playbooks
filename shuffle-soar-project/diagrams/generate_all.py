from build_flow import build_flow

# ---------------------------------------------------------------
# Playbook 1: Phishing Email Response
# ---------------------------------------------------------------
build_flow(
    title_text="Playbook 1: phishing email response",
    desc_text="Wazuh phishing alert leads to IOC extraction, VirusTotal URL and domain checks, a threat score, then either blocking the domain and source IP or logging for monitoring, followed by Slack and email notification.",
    nodes=[
        {"title": "Wazuh alert: phishing rule fires", "sub": ["Rule IDs 31101 / 31103 / 31530"], "color": "teal"},
        {"title": "Parse Wazuh alert", "sub": ["rule_id, src_ip, url, dst_user, hostname"], "color": "blue"},
        {"title": "Extract IOCs (regex)", "sub": ["url / domain / ip"], "color": "purple"},
        {"title": "VirusTotal URL + domain report", "sub": ["positives / total AV engines"], "color": "rust"},
        {"title": "Calculate threat score", "sub": ["(positives / total) x 100"], "color": "maroon"},
        {
            "branch": True,
            "left_label": "score > 5",
            "right_label": "score <= 5",
            "left": {"title": "Block domain", "sub": ["+ block source IP"], "color": "darkred"},
            "right": {"title": "Log & monitor", "sub": ["no block taken"], "color": "darkgray"},
        },
        {"title": "Notify and sync", "sub": ["Slack #soc-alerts + Email SOC", "Wazuh active-response update"], "color": "green"},
    ],
    out_svg="playbook_phishing.svg",
    out_png="playbook_phishing.png",
)

# ---------------------------------------------------------------
# Playbook 2: Malware Hash Detection
# ---------------------------------------------------------------
build_flow(
    title_text="Playbook 2: malware hash detection and endpoint isolation",
    desc_text="Wazuh file integrity alert leads to hash lookups on VirusTotal, malware family identification, then either isolating the endpoint and killing the process or quarantining the file, followed by case creation and a Slack alert.",
    nodes=[
        {"title": "Wazuh FIM alert: new/modified file", "sub": ["File integrity monitoring"], "color": "teal"},
        {"title": "Parse alert", "sub": ["md5, sha1, sha256, file_path, agent_id"], "color": "blue"},
        {"title": "VirusTotal MD5 + SHA256 lookup", "sub": ["cross-verify with two hash algorithms"], "color": "rust"},
        {"title": "Extract malware family", "sub": ["most common AV engine label"], "color": "purple"},
        {
            "branch": True,
            "left_label": "positives > 3",
            "right_label": "positives <= 3",
            "left": {"title": "Isolate endpoint", "sub": ["+ kill process"], "color": "darkred"},
            "right": {"title": "Quarantine file", "sub": ["host stays online"], "color": "darkgray"},
        },
        {"title": "Create TheHive case", "sub": ["attach SHA256 as observable", "auto-generate task list"], "color": "maroon"},
        {"title": "Slack #soc-critical", "sub": ["host, malware family, VT score, case #"], "color": "green"},
    ],
    out_svg="playbook_malware.svg",
    out_png="playbook_malware.png",
)

# ---------------------------------------------------------------
# Playbook 3: Brute Force Attack Response
# ---------------------------------------------------------------
build_flow(
    title_text="Playbook 3: brute force attack response",
    desc_text="Wazuh frequency alert on repeated failed logins leads to a VirusTotal IP reputation check, then either auto-blocking the source IP or rate-limiting and continued monitoring, followed by a Slack notification.",
    nodes=[
        {"title": "Wazuh alert: 5+ failed logins", "sub": ["same source IP, short time window"], "color": "teal"},
        {"title": "Parse alert", "sub": ["src_ip, dst_user, attempt_count, protocol"], "color": "blue"},
        {"title": "VirusTotal IP reputation report", "sub": ["community detections, passive DNS history"], "color": "rust"},
        {
            "branch": True,
            "left_label": "malicious or high volume",
            "right_label": "clean / low volume",
            "left": {"title": "Auto-block IP", "sub": ["at firewall, 24h"], "color": "darkred"},
            "right": {"title": "Rate-limit", "sub": ["continue monitoring"], "color": "darkgray"},
        },
        {"title": "Sync to Wazuh active-response", "sub": ["host-level firewall stays consistent"], "color": "maroon"},
        {"title": "Slack #soc-alerts", "sub": ["source IP, target user, attempt count, VT reputation"], "color": "green"},
    ],
    out_svg="playbook_bruteforce.svg",
    out_png="playbook_bruteforce.png",
)

# ---------------------------------------------------------------
# Playbook 4: Suspicious IP Enrichment
# ---------------------------------------------------------------
build_flow(
    title_text="Playbook 4: suspicious IP enrichment",
    desc_text="An outbound connection to an unrecognized IP triggers GeoIP and VirusTotal lookups, a composite threat score, then either a conditional block or logging the enrichment to a dashboard for analyst review.",
    nodes=[
        {"title": "Wazuh alert: outbound connection", "sub": ["destination IP not on allow-list"], "color": "teal"},
        {"title": "Parse alert", "sub": ["dest_ip, src_host, dest_port, process_name"], "color": "blue"},
        {"title": "GeoIP lookup", "sub": ["country, ASN, hosting provider"], "color": "purple"},
        {"title": "VirusTotal IP scan", "sub": ["detections, passive DNS, related samples"], "color": "rust"},
        {"title": "Composite threat scoring", "sub": ["GeoIP risk + VT detection count"], "color": "maroon"},
        {
            "branch": True,
            "left_label": "score > 40",
            "right_label": "score <= 40",
            "left": {"title": "Conditional block", "sub": ["outbound traffic"], "color": "darkred"},
            "right": {"title": "Log to dashboard", "sub": ["full enrichment kept"], "color": "darkgray"},
        },
    ],
    out_svg="playbook_suspicious_ip.svg",
    out_png="playbook_suspicious_ip.png",
)
