#!/usr/bin/env bash
# =============================================================
# Shuffle SOAR Project - Environment Setup Script
# =============================================================
# Bootstraps a local Shuffle instance via Docker Compose.
# Wazuh is NOT started by this script - it's a heavier multi-
# container stack (manager + indexer + dashboard) and is best
# run from Wazuh's own official docker-compose project. See
# docs/SETUP_GUIDE.md for the Wazuh quick-start link.
#
# Usage:
#   chmod +x scripts/setup.sh
#   ./scripts/setup.sh
# =============================================================

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}== Shuffle SOAR Project Setup ==${NC}"

# ---- 1. Check prerequisites ----------------------------------
command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker is required but not installed. Install Docker first: https://docs.docker.com/get-docker/${NC}"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || command -v docker compose >/dev/null 2>&1 || { echo -e "${RED}Docker Compose is required but not installed.${NC}"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo -e "${YELLOW}Warning: python3 not found - scripts/simulate_alert.py and scripts/test_webhook.py will not run.${NC}"; }
command -v git >/dev/null 2>&1 || { echo -e "${RED}Git is required but not installed.${NC}"; exit 1; }

echo -e "${GREEN}[OK]${NC} Prerequisites found."

# ---- 2. Set up .env from template -----------------------------
if [ ! -f ".env" ]; then
  cp configs/shuffle_env.example .env
  echo -e "${YELLOW}[ACTION REQUIRED]${NC} Created .env from template. Edit it now and add your VirusTotal API key and other credentials before continuing."
else
  echo -e "${GREEN}[OK]${NC} .env already exists - leaving it untouched."
fi

# ---- 3. Clone Shuffle if not already present -------------------
if [ ! -d "Shuffle" ]; then
  echo -e "${GREEN}==>${NC} Cloning Shuffle SOAR..."
  git clone https://github.com/Shuffle/Shuffle.git
else
  echo -e "${GREEN}[OK]${NC} Shuffle/ directory already exists - skipping clone."
fi

# ---- 4. Start Shuffle via Docker Compose -----------------------
echo -e "${GREEN}==>${NC} Starting Shuffle (this can take a minute on first run)..."
cd Shuffle
docker-compose up -d
cd ..

echo ""
echo -e "${GREEN}== Setup complete ==${NC}"
echo "Shuffle UI:        http://localhost:3001"
echo "Next steps:"
echo "  1. Open http://localhost:3001 and create your admin account"
echo "  2. Go to Workflows -> Import and upload each file in playbooks/"
echo "  3. Configure the VirusTotal, Slack, and HTTP app credentials inside each imported workflow"
echo "  4. Test with: python3 scripts/simulate_alert.py --type malware"
echo ""
echo "For Wazuh installation, see docs/SETUP_GUIDE.md"
