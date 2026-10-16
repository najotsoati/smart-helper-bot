#!/usr/bin/env bash
# Pull new code from GitHub and restart the panel when something changed.
# Installed as a systemd timer by install.sh (every 5 minutes), with the owner's consent.
set -euo pipefail
cd "$(dirname "$0")/.."
before=$(git rev-parse HEAD)
git pull -q --ff-only || exit 0
after=$(git rev-parse HEAD)
if [ "$before" != "$after" ]; then
  if ! git diff --quiet "$before" "$after" -- requirements.txt; then
    .venv/bin/pip install -q -r requirements.txt
  fi
  systemctl restart shorts-studio
  echo "updated $before -> $after"
fi
