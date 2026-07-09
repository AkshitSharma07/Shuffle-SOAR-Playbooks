# Setup Guide

Complete installation walkthrough for the Shuffle SOAR Playbook Automation project. This guide covers both a quick demo path (no live SIEM needed) and a full live deployment with Wazuh.

## 1. Prerequisites

| Requirement | Notes |
|---|---|
| Docker & Docker Compose | Used to run Shuffle (and optionally Wazuh) |
| Python 3.8+ | For the helper scripts in `scripts/` |
| Git | To clone this repo and Shuffle itself |
| VirusTotal account (free) | https://www.virustotal.com/gui/sign-in |
| 4GB+ RAM available | Shuffle alone is light; Wazuh's full stack (manager + indexer + dashboard) is heavier |

## 2. Quick Demo Path (Shuffle only, no live SIEM)

This path lets you import and run every playbook and see the orchestration logic work, without standing up Wazuh.

```bash
git clone https://github.com/<your-username>/shuffle-soar-playbooks.git
cd shuffle-soar-playbooks
chmod +x scripts/setup.sh
./scripts/setup.sh
```

The setup script will:
1. Check for Docker, Docker Compose, Python, and Git
2. Create `.env` from `configs/shuffle_env.example` (you still need to fill in your real API keys)
3. Clone the Shuffle repository
4. Start Shuffle with `docker-compose up -d`

Once running, open `http://localhost:3001`, create an admin account, and import each JSON file from `playbooks/` via **Workflows -> Import**.

Test the pipeline without a real alert:

```bash
python3 scripts/simulate_alert.py --type malware
```

## 3. Full Live Deployment (with Wazuh)

### 3.1 Install Wazuh

Wazuh's own quick-start Docker Compose is the easiest path and is documented at the official Wazuh installation guide. At a high level:

```bash
git clone https://github.com/wazuh/wazuh-docker.git -b v4.x
cd wazuh-docker/single-node
docker-compose up -d
```

This starts the Wazuh Manager, Wazuh Indexer, and Wazuh Dashboard. The dashboard is reachable at `https://localhost:443` by default.

### 3.2 Install at least one Wazuh Agent

Install the Wazuh agent on any endpoint you want monitored (Linux, Windows, or macOS). Registration and the agent installer are generated from the Wazuh Dashboard under **Agents -> Deploy new agent**.

### 3.3 Add the custom detection rules

Copy `configs/wazuh_rules.xml` into the manager's custom rules file:

```bash
# On the Wazuh Manager host (or inside the manager container)
cat configs/wazuh_rules.xml >> /var/ossec/etc/rules/local_rules.xml
systemctl restart wazuh-manager
```

### 3.4 Configure the Wazuh -> Shuffle integration

Wazuh supports custom integrations that POST matching alerts to an external URL. Add an integration block to `/var/ossec/etc/ossec.conf` on the manager, pointing at each playbook's Shuffle webhook URL (you'll get these after importing the playbooks - see step 4 below):

```xml
<integration>
  <name>custom-shuffle</name>
  <hook_url>http://your-shuffle-host:3001/api/v1/hooks/your_webhook_id</hook_url>
  <rule_id>100101,100110,100120,100121,100130</rule_id>
  <alert_format>json</alert_format>
</integration>
```

Restart the manager after editing:

```bash
systemctl restart wazuh-manager
```

## 4. Import and Configure Playbooks in Shuffle

1. Open the Shuffle UI (`http://localhost:3001`)
2. Go to **Workflows -> Import** and upload each file from `playbooks/` one at a time
3. For each imported workflow, open the app nodes (VirusTotal, Slack, HTTP, SMTP) and authenticate them with the credentials from your `.env`
4. Copy the workflow's webhook URL (shown on the Webhook trigger node) into your `.env` under the matching `SHUFFLE_WEBHOOK_*` key, and into the Wazuh integration block from step 3.4
5. Activate each workflow (toggle from Draft to Active)

## 5. Verify End to End

```bash
# Test basic webhook connectivity
python3 scripts/test_webhook.py http://localhost:3001/api/v1/hooks/your_webhook_id

# Send a full simulated alert through a specific playbook
python3 scripts/simulate_alert.py --type bruteforce
```

Check the Shuffle UI's workflow execution log to see each step run, and confirm the Slack/email notification arrives.

## 6. Common Issues

| Symptom | Likely Cause | Fix |
|---|---|---|
| Shuffle webhook never fires | Wazuh integration not pointing at the right URL, or manager not restarted | Re-check `ossec.conf` integration block and restart `wazuh-manager` |
| VirusTotal steps return 204/empty | Rate limit hit (4 req/min on free tier) | Add delay between steps or reduce test frequency |
| Firewall block step fails | `FIREWALL_API_URL`/`FIREWALL_API_KEY` are placeholders | Replace with your actual firewall vendor's REST API details, or stub the step out for demo purposes |
| Docker Compose fails to start Shuffle | Port 3001 already in use | Stop the conflicting process or change the port mapping in Shuffle's `docker-compose.yml` |
