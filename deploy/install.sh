#!/usr/bin/env bash
# Install Shorts Studio on an Ubuntu/Debian server (run as root from the repo folder).
set -euo pipefail
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
apt-get update -y
apt-get install -y python3-venv python3-pip
python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install -q -r "$APP_DIR/requirements.txt"
if [ ! -f "$APP_DIR/.env" ]; then
  cp "$APP_DIR/.env.example" "$APP_DIR/.env"
  sed -i "s/^PANEL_PASSWORD=.*/PANEL_PASSWORD=$(openssl rand -hex 12)/" "$APP_DIR/.env"
  sed -i "s/^AGENT_TOKEN=.*/AGENT_TOKEN=$(openssl rand -hex 32)/" "$APP_DIR/.env"
  echo "Created .env with a random panel password and agent token."
fi
sed "s#__APP_DIR__#$APP_DIR#g" "$APP_DIR/deploy/shorts-studio.service" > /etc/systemd/system/shorts-studio.service
systemctl daemon-reload
systemctl enable --now shorts-studio
echo
echo "Panel runs on 127.0.0.1:8080.  Put Caddy in front for HTTPS (see deploy/Caddyfile)."
echo "Login: $(grep ^PANEL_USER "$APP_DIR/.env" | cut -d= -f2) / $(grep ^PANEL_PASSWORD "$APP_DIR/.env" | cut -d= -f2)"
