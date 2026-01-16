# Building Ring Light AppImage

This guide explains how to create a distributable AppImage for Ring Light that works on any Linux distribution.

## Prerequisites

```bash
# Install required tools
sudo apt-get install python3 python3-pip python3-venv wget

# Optional: for icon creation
pip install Pillow
```

## Quick Build

### 1. Create Icon (if you don't have one)

```bash
python3 create-icon.py
```

Or provide your own `ringlight.png` (256x256 recommended).

### 2. Build AppImage

```bash
chmod +x build-appimage.sh
./build-appimage.sh
```

This will:
- Create an AppDir structure
- Install Python dependencies in isolated environment
- Package everything into a single AppImage file
- Output: `Ring_Light-1.0.0-x86_64.AppImage`

## Manual Build (Advanced)

If the automated script doesn't work, you can build manually:

### Step 1: Install python-appimage

```bash
pip install python-appimage
```

### Step 2: Create AppImage

```bash
python-appimage build app \
    -l manylinux2014_x86_64 \
    ringlight.py
```

## Using the AppImage

### Run directly:
```bash
chmod +x Ring_Light-1.0.0-x86_64.AppImage
./Ring_Light-1.0.0-x86_64.AppImage
```

### Install system-wide:
```bash
sudo mv Ring_Light-1.0.0-x86_64.AppImage /usr/local/bin/ringlight
sudo chmod +x /usr/local/bin/ringlight
```

### Integrate with desktop environment:
```bash
# The AppImage should auto-integrate when first run
# Or manually:
./Ring_Light-1.0.0-x86_64.AppImage --appimage-extract
sudo cp squashfs-root/ringlight.desktop /usr/share/applications/
sudo cp squashfs-root/ringlight.png /usr/share/icons/hicolor/256x256/apps/
```

## Troubleshooting

### Qt platform plugin error

If you see "could not find the Qt platform plugin":

```bash
export QT_QPA_PLATFORM_PLUGIN_PATH=/path/to/PySide6/plugins/platforms
```

The AppRun script should handle this automatically.

### Missing dependencies

The AppImage bundles Python and all dependencies. If issues occur:

1. Check Python version: `python3 --version` (should be 3.10+)
2. Verify PySide6 installation in AppDir
3. Check AppRun script paths

### Permission errors

```bash
chmod +x Ring_Light-1.0.0-x86_64.AppImage
```

## Distribution

Upload the `.AppImage` file to:
- GitHub Releases
- Your website
- Package managers (via AppImageHub)

Users can download and run directly without installation!

## Notes

- AppImage size: ~150-200MB (includes Python + Qt)
- Works on: Ubuntu, Fedora, Arch, Debian, openSUSE, etc.
- No root required to run
- Self-contained and portable
