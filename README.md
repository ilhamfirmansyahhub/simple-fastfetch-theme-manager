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

## Run

```bash
chmod +x run.sh
./run.sh
```

The application reads the existing Fastfetch configuration from:

```text
~/.config/fastfetch/config.jsonc
```

Uploaded images are copied into:

```text
~/.config/fastfetch/assets/
```
