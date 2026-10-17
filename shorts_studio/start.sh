#!/usr/bin/env bash
# Shorts Studio: macOS / Linux launcher. First run installs everything (~2 min), later runs start instantly.
set -e
cd "$(dirname "$0")"

PY=""
for cand in python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "$cand" >/dev/null 2>&1 && "$cand" -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then
    PY="$cand"; break
  fi
done
if [ -z "$PY" ]; then
  echo "Python 3.10+ topilmadi. https://www.python.org/downloads/ dan o'rnating (macOS: brew install python)."
  exit 1
fi

if [ ! -x .venv/bin/python ]; then
  echo "Birinchi ishga tushirish: virtual muhit yaratilmoqda..."
  "$PY" -m venv .venv
fi

# reinstall dependencies only when requirements.txt changed
STAMP=.venv/.requirements.stamp
if [ ! -f "$STAMP" ] || ! cmp -s requirements.txt "$STAMP"; then
  echo "Kutubxonalar o'rnatilmoqda (bir necha daqiqa)..."
  .venv/bin/python -m pip install --upgrade pip -q
  .venv/bin/python -m pip install -r requirements.txt -q
  cp requirements.txt "$STAMP"
fi

exec .venv/bin/python run.py
