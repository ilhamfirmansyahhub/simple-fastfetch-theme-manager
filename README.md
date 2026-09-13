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

Clone the repository, enter the directory, then run the installer:

```bash
git clone https://github.com/ilhamfirmansyahhub/simple-fastfetch-theme-manager.git
cd simple-fastfetch-theme-manager
chmod +x install.sh
./install.sh
```

The installer checks that Python 3, Fastfetch, and PySide6 are available. It then installs the application to:

```text
~/.local/share/simple-fastfetch-theme-manager/
```

### Application launcher integration

The installer automatically creates a standard `.desktop` entry at:

```text
~/.local/share/applications/simple-fastfetch-theme-manager.desktop
```

This means you do **not** need to open a terminal every time you want to edit Fastfetch.

After installation:

1. Open your desktop application's launcher/menu.
2. Search for **Simple Fastfetch Theme Manager**.
3. Launch it normally like any other application.
4. You can pin it to your favorite applications or taskbar/dock if your desktop environment supports pinning.

The launcher entry points to the installed copy under `~/.local/share/`, so moving or deleting the Git repository after installation does not break the launcher.

If the launcher does not appear immediately, open the application menu again or log out and back in so your desktop environment refreshes its application list.

## Run from source

You can also run the program directly from the repository without installing the launcher entry:

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

The uninstall script removes only the installed application files and launcher entry. Your Fastfetch configuration and assets in `~/.config/fastfetch/` are left untouched.

## Fastfetch files

The application reads the existing Fastfetch configuration from:

```text
~/.config/fastfetch/config.jsonc
```

Uploaded images are copied into:

```text
~/.config/fastfetch/assets/
```
