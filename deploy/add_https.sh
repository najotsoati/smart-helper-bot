#!/usr/bin/env bash
# Give the panel its own HTTPS address: studio.<ip-with-dashes>.sslip.io
# Adds a block to Caddy; existing sites in the Caddyfile stay as they are.
set -euo pipefail
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PORT=$(grep '^STUDIO_PORT=' "$APP_DIR/.env" | cut -d= -f2)
IP=$(curl -4 -s ifconfig.me)
HOST="studio.$(echo "$IP" | tr . -).sslip.io"
CF=/etc/caddy/Caddyfile

if ! command -v caddy >/dev/null; then
  if ss -ltnp | grep -qE ':(80|443)\s'; then
    echo "Ports 80/443 are used by another web server (not Caddy):"
    ss -ltnp | grep -E ':(80|443)\s'
    echo "Send this output to Claude; nothing was changed."; exit 1
  fi
  apt-get install -y caddy
  : > "$CF"
fi

if grep -q "^$HOST" "$CF" 2>/dev/null; then
  echo "Already configured."
else
  cp "$CF" "$CF.bak.$(date +%s)" 2>/dev/null || true
  printf '\n%s {\n\treverse_proxy 127.0.0.1:%s\n\trequest_body {\n\t\tmax_size 200MB\n\t}\n}\n' "$HOST" "$PORT" >> "$CF"
  if ! caddy validate --config "$CF" --adapter caddyfile >/dev/null 2>&1; then
    echo "Caddy config is invalid, restoring the backup."; cp "$(ls -t $CF.bak.* | head -1)" "$CF"; exit 1
  fi
  systemctl reload caddy
fi
sed -i "s#^PUBLIC_URL=.*#PUBLIC_URL=https://$HOST#" "$APP_DIR/.env"
systemctl restart shorts-studio
echo "Panel: https://$HOST"
