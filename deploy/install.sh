#!/usr/bin/env bash
# Install Shorts Studio on an Ubuntu/Debian server (run as root from the repo folder).
# Safe next to other apps: picks a free port and never touches other services.
set -euo pipefail
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
apt-get update -y
apt-get install -y python3-venv python3-pip openssl
python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install -q -r "$APP_DIR/requirements.txt"
if [ ! -f "$APP_DIR/.env" ]; then
  cp "$APP_DIR/.env.example" "$APP_DIR/.env"
  sed -i "s/^PANEL_PASSWORD=.*/PANEL_PASSWORD=$(openssl rand -hex 12)/" "$APP_DIR/.env"
  sed -i "s/^AGENT_TOKEN=.*/AGENT_TOKEN=$(openssl rand -hex 32)/" "$APP_DIR/.env"
  echo "Created .env with a random panel password and agent token."
fi

# Port: keep the one chosen earlier, otherwise the first free one from 8090.
PORT=$(grep -s '^STUDIO_PORT=' "$APP_DIR/.env" | cut -d= -f2 || true)
if [ -z "$PORT" ]; then
  PORT=8090
  while ss -ltn | awk '{print $4}' | grep -qE "[:.]$PORT\$"; do PORT=$((PORT + 1)); done
  echo "STUDIO_PORT=$PORT" >> "$APP_DIR/.env"
fi

sed -e "s#__APP_DIR__#$APP_DIR#g" -e "s#__PORT__#$PORT#g" "$APP_DIR/deploy/shorts-studio.service" \
  > /etc/systemd/system/shorts-studio.service
sed "s#__APP_DIR__#$APP_DIR#g" "$APP_DIR/deploy/shorts-studio-update.service" > /etc/systemd/system/shorts-studio-update.service
cp "$APP_DIR/deploy/shorts-studio-update.timer" /etc/systemd/system/
systemctl daemon-reload
systemctl enable shorts-studio >/dev/null
systemctl enable --now shorts-studio-update.timer >/dev/null
systemctl restart shorts-studio
sleep 2
if systemctl is-active --quiet shorts-studio; then
  echo "OK: Shorts Studio runs on 127.0.0.1:$PORT"
else
  echo "ERROR: service did not start:"; journalctl -u shorts-studio -n 20 --no-pager; exit 1
fi
echo "Login: $(grep ^PANEL_USER "$APP_DIR/.env" | cut -d= -f2) / $(grep ^PANEL_PASSWORD "$APP_DIR/.env" | cut -d= -f2)"
echo "Next: bash deploy/add_https.sh   (adds an HTTPS address without touching other sites)"
