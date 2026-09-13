#!/usr/bin/env bash
set -euo pipefail

APP_ID="simple-fastfetch-theme-manager"
APP_DIR="$HOME/.local/share/$APP_ID"
DESKTOP_FILE="$HOME/.local/share/applications/$APP_ID.desktop"

rm -rf "$APP_DIR"
rm -f "$DESKTOP_FILE"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true
fi

echo "Uninstalled Simple Fastfetch Theme Manager."
