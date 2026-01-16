#!/bin/bash
# Build script for LumaScreen AppImage
# Requires: python-appimage or appimagetool

set -e

APP_NAME="LumaScreen"
APP_VERSION="1.0.0"
PYTHON_VERSION="3.10"

echo "🔨 Building LumaScreen AppImage..."

# Create AppDir structure
APPDIR="AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$APPDIR/usr/lib"

echo "📦 Installing dependencies..."

# Create virtual environment
python3 -m venv "$APPDIR/venv"
source "$APPDIR/venv/bin/activate"

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Copy application files
echo "📋 Copying application files..."
cp ringlight.py "$APPDIR/usr/bin/lumascreen"
chmod +x "$APPDIR/usr/bin/lumascreen"

# Create icon if it doesn't exist
if [ ! -f "lumascreen.png" ]; then
    echo "📸 Creating icon..."
    python3 create-icon.py
fi

# Copy icon to multiple locations for better compatibility
if [ -f "lumascreen.png" ]; then
    cp lumascreen.png "$APPDIR/usr/share/icons/hicolor/256x256/apps/lumascreen.png"
    cp lumascreen.png "$APPDIR/usr/bin/lumascreen.png"  # Same directory as executable
    cp lumascreen.png "$APPDIR/lumascreen.png"
    cp lumascreen.png "$APPDIR/.DirIcon"
    echo "✓ Icon copied to multiple locations"
else
    echo "❌ Could not create icon"
    exit 1
fi

# Copy desktop file
sed 's/ringlight/lumascreen/g' ringlight.desktop > "$APPDIR/lumascreen.desktop"
cp "$APPDIR/lumascreen.desktop" "$APPDIR/usr/share/applications/"

# Create AppRun script
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
APPDIR="$(dirname "$(readlink -f "$0")")"

# Set library paths
export LD_LIBRARY_PATH="${APPDIR}/usr/lib:${LD_LIBRARY_PATH}"

# Ensure Qt platform plugin is found
export QT_PLUGIN_PATH="${APPDIR}/venv/lib/python3.10/site-packages/PySide6/Qt/plugins"
export QT_QPA_PLATFORM_PLUGIN_PATH="${QT_PLUGIN_PATH}/platforms"

# Use the venv Python directly without setting PYTHONHOME
exec "${APPDIR}/venv/bin/python3" "${APPDIR}/usr/bin/lumascreen" "$@"
EOF

chmod +x "$APPDIR/AppRun"

echo "🔧 Building AppImage..."

# Download appimagetool if not present
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo "📥 Downloading appimagetool..."
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x appimagetool-x86_64.AppImage
fi

# Try to run appimagetool, extract if FUSE not available
if ! ./appimagetool-x86_64.AppImage --version &> /dev/null; then
    echo "⚠️  FUSE not available, extracting appimagetool..."
    ./appimagetool-x86_64.AppImage --appimage-extract &> /dev/null
    APPIMAGETOOL="./squashfs-root/AppRun"
else
    APPIMAGETOOL="./appimagetool-x86_64.AppImage"
fi

# Build the AppImage
ARCH=x86_64 "$APPIMAGETOOL" "$APPDIR" "${APP_NAME}-${APP_VERSION}-x86_64.AppImage"

# Clean up extracted appimagetool
if [ -d "squashfs-root" ]; then
    rm -rf squashfs-root
fi

echo "✅ AppImage built successfully: ${APP_NAME}-${APP_VERSION}-x86_64.AppImage"
echo ""
echo "To run: ./${APP_NAME}-${APP_VERSION}-x86_64.AppImage"
echo "To install: chmod +x ${APP_NAME}-${APP_VERSION}-x86_64.AppImage && sudo mv ${APP_NAME}-${APP_VERSION}-x86_64.AppImage /usr/local/bin/lumascreen"
