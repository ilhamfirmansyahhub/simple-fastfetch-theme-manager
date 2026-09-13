# Simple Fastfetch Theme Manager

A minimal native Linux GUI for editing a Fastfetch setup visually.

## Features

- Live preview from the installed `fastfetch`
- Displays the configured logo image
- Drag the logo freely in the preview
- Resize the logo with the mouse wheel while preserving its visual aspect ratio
- Edit displayed Fastfetch text directly in the preview
- Edit the real Fastfetch `config.jsonc` when needed
- Save changes to `~/.config/fastfetch/config.jsonc`
- Install as a normal desktop application so it appears in your application launcher
- No Electron or web runtime

## Requirements

- Linux
- Python 3
- PySide6
- Fastfetch

On Arch Linux/CachyOS, install PySide6 with:

```bash
sudo pacman -S pyside6
```

Fastfetch should already be installed.

## Install

Make the installer executable and run it:

```bash
chmod +x install.sh
./install.sh
```

The installer copies the app to:

```text
~/.local/share/simple-fastfetch-theme-manager/
```

and creates a desktop entry at:

```text
~/.local/share/applications/simple-fastfetch-theme-manager.desktop
```

After installation, search for **Simple Fastfetch Theme Manager** in your application launcher. You can pin it like any other application.

## Run from source

```bash
chmod +x run.sh
./run.sh
```

## Uninstall

From the repository directory:

```bash
chmod +x uninstall.sh
./uninstall.sh
```

The uninstall script removes only the application files and launcher entry. Your Fastfetch configuration and assets in `~/.config/fastfetch/` are left untouched.

## Fastfetch files

The application reads the existing Fastfetch configuration from:

```text
~/.config/fastfetch/config.jsonc
```

Uploaded images are copied into:

```text
~/.config/fastfetch/assets/
```
