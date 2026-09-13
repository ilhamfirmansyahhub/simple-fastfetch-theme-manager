#!/usr/bin/env bash
set -euo pipefail

APP_NAME="Simple Fastfetch Theme Manager"
APP_ID="simple-fastfetch-theme-manager"
APP_DIR="$HOME/.local/share/$APP_ID"
DESKTOP_DIR="$HOME/.local/share/applications"
DESKTOP_FILE="$DESKTOP_DIR/$APP_ID.desktop"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is required." >&2
    exit 1
fi

if ! command -v fastfetch >/dev/null 2>&1; then
    echo "Error: fastfetch is required." >&2
    exit 1
fi

if ! python3 -c 'import PySide6' >/dev/null 2>&1; then
    echo "Error: PySide6 is required." >&2
    echo "On Arch Linux/CachyOS: sudo pacman -S pyside6" >&2
    exit 1
fi

mkdir -p "$APP_DIR" "$DESKTOP_DIR"

# Install the app in a stable per-user location so the launcher entry keeps
# working even if the Git repository is moved or deleted later.
cp "$SCRIPT_DIR/main.py" "$SCRIPT_DIR/run.sh" "$APP_DIR/"
chmod +x "$APP_DIR/run.sh"

cat > "$DESKTOP_FILE" <<DESKTOP
[Desktop Entry]
Version=1.0
Type=Application
Name=$APP_NAME
Comment=Visually edit and manage your Fastfetch setup
Exec=$APP_DIR/run.sh
Terminal=false
Categories=Utility;Settings;
Keywords=Fastfetch;Theme;Ricing;Terminal;Linux;
StartupNotify=true
DESKTOP

chmod 644 "$DESKTOP_FILE"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
fi

echo "Installed: $APP_NAME"
echo "Launcher entry: $DESKTOP_FILE"
echo "Open it from your application launcher."
