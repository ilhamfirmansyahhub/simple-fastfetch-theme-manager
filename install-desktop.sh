#!/bin/bash
set -e

REPO_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$HOME/.local/share/applications"
DESKTOP_FILE="$APP_DIR/simple-fastfetch-theme-manager.desktop"

mkdir -p "$APP_DIR"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Fastfetch Theme Manager
Comment=Edit and customize your Fastfetch setup
Exec=python3 "$REPO_DIR/main.py"
Terminal=false
Categories=Utility;System;
StartupNotify=true
EOF

chmod 644 "$DESKTOP_FILE"

update-desktop-database "$APP_DIR" 2>/dev/null || true

echo "Fastfetch Theme Manager is now available in your application launcher."
echo "Launcher entry: $DESKTOP_FILE"
echo "Repository path: $REPO_DIR"
