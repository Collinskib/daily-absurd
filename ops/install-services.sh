#!/usr/bin/env bash
# Install and enable the Daily Absurd systemd --user units.
set -euo pipefail
UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
mkdir -p "$UNIT_DIR"
cp "$(dirname "$0")"/systemd/absurd-*.service "$(dirname "$0")"/systemd/absurd-*.timer "$UNIT_DIR"/
systemctl --user daemon-reload
systemctl --user enable --now absurd-pipeline.timer absurd-dashboard.service
systemctl --user list-timers absurd-pipeline.timer --no-pager
echo "Dashboard: http://127.0.0.1:8899"
