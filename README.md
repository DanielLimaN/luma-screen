# LumaScreen

A virtual ring light application for Linux distributions, designed for video calls, streaming, and content creation. This lightweight desktop application creates a customizable, translucent light effect around your screen edges to improve lighting quality during video recording or calls.

**Platform:** Linux (X11/Wayland) | **Distribution:** AppImage for universal compatibility

## Features

- **Customizable Brightness**: Adjust from 0% to 200% for perfect lighting
- **Adjustable Thickness**: Control the ring light size (1-900 pixels)
- **Color Selection**: Choose any color for your ring light effect
- **Multi-layer Bloom**: Realistic light diffusion with multiple gradient layers
- **Click-through Overlay**: The overlay doesn't interfere with your applications
- **Always on Top**: Stays visible across all applications
- **Screen-aware**: Automatically adapts to screen resolution changes

## Requirements

**Platform Requirements:**
- **Operating System:** Linux distributions (Ubuntu, Fedora, Debian, Arch, etc.)
- **Display Server:** X11 (fully tested) or Wayland (experimental support)
- **Architecture:** x86_64

**Runtime Requirements** (when running from source):
- Python 3.10 or higher
- PySide6 (Qt for Python) >= 6.6.0

**Note:** Windows and macOS are not currently supported. The AppImage is self-contained and works on most Linux distributions without additional dependencies.

## Installation

### Option 1: System-Wide Installation (Recommended)

Build and install the AppImage for easy system-wide access:

```bash
# 1. Clone the repository
git clone <repository-url>
cd ringlight

# 2. Build the AppImage
./build-appimage.sh

# 3. Install system-wide (requires sudo)
./install.sh
```

After installation, you can:
- Run from terminal: `lumascreen`
- Launch from your application menu
- Search for "LumaScreen" in your launcher

**To uninstall:**
```bash
./uninstall.sh
```

### Option 2: Portable AppImage

Run directly without system installation:

```bash
# Build the AppImage
./build-appimage.sh

# Make it executable and run
chmod +x LumaScreen-1.0.0-x86_64.AppImage
./LumaScreen-1.0.0-x86_64.AppImage
```

### Option 3: Run from Source

For development or testing:

```bash
# 1. Clone the repository
git clone <repository-url>
cd ringlight

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python ringlight.py
```

## Usage

After installation, launch LumaScreen:

**If installed system-wide:**
```bash
lumascreen
```
Or find it in your application menu.

**If running from source:**
```bash
python ringlight.py
```

### Controls

- **Brightness Slider**: Adjust light intensity (0-200%)
- **Thickness Spinner**: Change ring light width in pixels
- **Choose Color Button**: Pick any color for your ring light
- **Turn Off/On Overlay**: Temporarily disable the overlay
- **PANIC Button**: Emergency shutdown of the overlay
- **Close All**: Exit the application

### Recommended Settings

For best results:
- **Brightness**: 80-140%
- **Thickness**: 200-350 pixels
- **Color**: White (255, 255, 255) or warm white (255, 240, 220)

## How It Works

The application creates two windows:

1. **Overlay Window**: A transparent, frameless, always-on-top window that covers your entire screen. It uses Qt's screen composition mode to render gradient-based light effects around the edges.

2. **Control Panel**: A standard window for adjusting settings in real-time.

The overlay uses multiple gradient layers with varying intensities to create a realistic bloom effect, similar to professional ring lights.

## Technical Details

### Architecture

- **RingLightConfig**: Configuration class containing all constants and default values
- **RingLightOverlay**: The transparent overlay widget that renders the light effect
- **ControlPanel**: The UI window for user controls
- **main()**: Application entry point with error handling

### Key Technologies

- **PySide6/Qt6**: Cross-platform UI framework
- **QPainter**: For custom rendering
- **QLinearGradient**: For smooth light diffusion
- **Composition Modes**: Screen blend mode for natural light effect

### Code Quality

This codebase follows industry best practices:
- ✅ Type hints throughout
- ✅ Comprehensive docstrings (Google style)
- ✅ Logging for debugging
- ✅ Constants in configuration class
- ✅ Separation of concerns
- ✅ Error handling
- ✅ Clean, readable code

## Customization

You can modify the default settings in the `RingLightConfig` class:

```python
class RingLightConfig:
    DEFAULT_THICKNESS: int = 220
    DEFAULT_BRIGHTNESS: float = 0.80  # 80%
    DEFAULT_COLOR: tuple[int, int, int] = (255, 255, 255)
    # ... more configuration options
```

You can also adjust the bloom effect by modifying the `BLOOM_LAYERS` constant:

```python
BLOOM_LAYERS: list[tuple[float, float]] = [
    (1.00, 1.00),  # (intensity, size_multiplier)
    (0.70, 0.75),
    (0.45, 0.55),
    (0.25, 0.40),
]
```

## Troubleshooting

### The overlay doesn't appear
- Check if the overlay is turned on (button should say "Turn Off Overlay")
- Increase the brightness setting
- Check application logs in the terminal

### The overlay interferes with my applications
- This shouldn't happen as the overlay is click-through
- If it does, use the PANIC button to disable it
- Report the issue with your OS and desktop environment details

### Performance issues
- Reduce the thickness setting
- Reduce the number of bloom layers in the code
- Check system resources

## Contributing

This is a free contribution to the community. Contributions are welcome!

### How to Contribute

1. Fork the repository
2. Create a feature branch
3. Make your changes following the existing code style
4. Test thoroughly
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Add type hints to all functions
- Write docstrings for all public methods
- Use descriptive variable names
- Keep functions focused and single-purpose

## License

MIT License - feel free to use, modify, and distribute as needed.

## Acknowledgments

Created as a free contribution to the open-source community to help content creators, streamers, and remote workers improve their video lighting.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Contribute improvements via pull requests

---

**Made with ❤️ for the developer community**
