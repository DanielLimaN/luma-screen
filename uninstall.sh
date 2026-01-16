#!/bin/bash
# LumaScreen Uninstallation Script
# Removes LumaScreen from the system

set -e

echo "🗑️  Uninstalling LumaScreen..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  This script requires sudo privileges."
    echo "Re-running with sudo..."
    sudo "$0" "$@"
    exit $?
fi

# Remove AppImage
if [ -f "/usr/local/bin/lumascreen" ]; then
    rm /usr/local/bin/lumascreen
    echo "✓ Removed executable"
else
    echo "⚠️  Executable not found"
fi

# Remove desktop file
if [ -f "/usr/share/applications/lumascreen.desktop" ]; then
    rm /usr/share/applications/lumascreen.desktop
    echo "✓ Removed desktop entry"
else
    echo "⚠️  Desktop entry not found"
fi

# Remove icon
if [ -f "/usr/share/icons/hicolor/256x256/apps/lumascreen.png" ]; then
    rm /usr/share/icons/hicolor/256x256/apps/lumascreen.png
    echo "✓ Removed icon"
    
    # Update icon cache
    if command -v gtk-update-icon-cache &> /dev/null; then
        gtk-update-icon-cache /usr/share/icons/hicolor/ 2>/dev/null || true
    fi
else
    echo "⚠️  Icon not found"
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications/ 2>/dev/null || true
fi

echo ""
echo "✅ LumaScreen uninstalled successfully!"
echo ""
