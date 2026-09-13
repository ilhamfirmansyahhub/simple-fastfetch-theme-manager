# Installation

On CachyOS / Arch Linux:

```bash
sudo pacman -S --needed git fastfetch pyside6
git clone https://github.com/ilhamfirmansyahhub/simple-fastfetch-theme-manager.git
cd simple-fastfetch-theme-manager
bash install-desktop.sh
```

The manager will then appear in the application launcher as **Fastfetch Theme Manager**.

No `sudo` is needed for the launcher installation. The cloned directory must remain in place because the launcher starts `main.py` from that directory.

To update later:

```bash
cd simple-fastfetch-theme-manager
git pull
```
