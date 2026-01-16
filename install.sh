#!/bin/bash
# LumaScreen Installation Script
# Installs the AppImage system-wide and integrates with desktop environment

set -e

APPIMAGE="LumaScreen-1.0.0-x86_64.AppImage"
INSTALL_DIR="/usr/local/bin"
DESKTOP_FILE="lumascreen.desktop"
ICON_FILE="lumascreen.png"

echo "🚀 Installing LumaScreen..."

# Check if AppImage exists
if [ ! -f "$APPIMAGE" ]; then
    echo "❌ Error: $APPIMAGE not found. Please build it first with ./build-appimage.sh"
    exit 1
fi

# Check if running as root for system-wide installation
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  This script requires sudo privileges for system-wide installation."
    echo "Re-running with sudo..."
    sudo "$0" "$@"
    exit $?
fi

# Install AppImage
echo "📦 Installing AppImage to $INSTALL_DIR..."
chmod +x "$APPIMAGE"
cp "$APPIMAGE" "$INSTALL_DIR/lumascreen"
echo "✓ AppImage installed"

# Create desktop file
echo "📝 Creating desktop entry..."
cat > "/usr/share/applications/$DESKTOP_FILE" << 'EOF'
[Desktop Entry]
Type=Application
Name=LumaScreen
GenericName=Virtual Screen Light
Comment=Virtual screen light overlay for video calls and streaming
Exec=/usr/local/bin/lumascreen
Icon=lumascreen
Terminal=false
Categories=Utility;AudioVideo;Video;
Keywords=luma;screen;light;video;call;streaming;webcam;ring;
StartupNotify=true
StartupWMClass=lumascreen
EOF
echo "✓ Desktop entry created"

# Install icon
echo "🎨 Installing icon..."
if [ -f "$ICON_FILE" ]; then
    mkdir -p /usr/share/icons/hicolor/256x256/apps
    cp "$ICON_FILE" /usr/share/icons/hicolor/256x256/apps/
    
    # Update icon cache if possible
    if command -v gtk-update-icon-cache &> /dev/null; then
        gtk-update-icon-cache /usr/share/icons/hicolor/ 2>/dev/null || true
    fi
    echo "✓ Icon installed"
else
    echo "⚠️  Icon file not found, skipping..."
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications/ 2>/dev/null || true
fi

echo ""
echo "✅ LumaScreen installed successfully!"
echo ""
echo "You can now:"
echo "  • Run from terminal: lumascreen"
echo "  • Find it in your application menu"
echo "  • Search for 'LumaScreen' in your launcher"
echo ""
