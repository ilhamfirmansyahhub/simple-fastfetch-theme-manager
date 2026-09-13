# Simple Fastfetch Theme Manager

A minimal native GUI manager for Fastfetch on Linux.

## Install on CachyOS / Arch Linux

```bash
sudo pacman -S --needed git fastfetch pyside6
git clone https://github.com/ilhamfirmansyahhub/simple-fastfetch-theme-manager.git
cd simple-fastfetch-theme-manager
bash install-desktop.sh
```

After that, open your application launcher and search for **Fastfetch Theme Manager**.

No system-wide installation is required. Keep the cloned repository folder in place because the launcher runs the manager from that folder.

You can also run it directly with:

```bash
./run.sh
```

## Update

```bash
cd simple-fastfetch-theme-manager
git pull
```

## Features

- Upload and preview your Fastfetch logo.
- Move the logo freely around the preview.
- Resize the logo while keeping its visual aspect ratio.
- Edit displayed Fastfetch text directly in the GUI.
- Edit the Fastfetch config when needed.
- Save changes to `~/.config/fastfetch/config.jsonc`.
