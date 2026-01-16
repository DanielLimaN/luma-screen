# Contributing to Ring Light Overlay

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. Create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, desktop environment)
   - Screenshots if applicable

### Suggesting Enhancements

1. Check existing issues and discussions
2. Create an issue describing:
   - The problem you're trying to solve
   - Your proposed solution
   - Alternative approaches considered
   - Why this benefits users

### Pull Requests

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/ringlight.git
   cd ringlight
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Follow the code style guidelines (below)
   - Add/update docstrings
   - Add type hints
   - Update tests if applicable
   - Update documentation

4. **Test Your Changes**
   ```bash
   python ringlight_improved.py
   ```
   - Test on your platform
   - Verify all features work
   - Check for performance issues

5. **Commit**
   ```bash
   git add .
   git commit -m "Add: descriptive commit message"
   ```
   
   Commit message prefixes:
   - `Add:` new features
   - `Fix:` bug fixes
   - `Update:` changes to existing features
   - `Refactor:` code restructuring
   - `Docs:` documentation only
   - `Style:` formatting, no code change

6. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a pull request on GitHub

## Code Style Guidelines

### Python Style

Follow **PEP 8** with these specifics:

- **Line length**: Maximum 100 characters (88 for Black formatter)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings
- **Imports**: Grouped and sorted
  ```python
  # Standard library
  import sys
  import logging
  
  # Third-party
  from PySide6.QtWidgets import QWidget
  
  # Local
  from .config import Settings
  ```

### Type Hints

Always include type hints:

```python
def set_brightness(self, value: int) -> None:
    """Set brightness level."""
    self.brightness = value
```

### Docstrings

Use **Google-style** docstrings:

```python
def calculate_gradient(
    self,
    start: int,
    end: int,
    color: QColor
) -> QLinearGradient:
    """
    Calculate a linear gradient between two points.
    
    Args:
        start: Starting position in pixels.
        end: Ending position in pixels.
        color: The gradient color.
        
    Returns:
        A configured QLinearGradient object.
        
    Raises:
        ValueError: If start >= end.
    """
    if start >= end:
        raise ValueError("Start must be less than end")
    # ...
```

### Naming Conventions

- **Classes**: `PascalCase` - `RingLightOverlay`
- **Functions/Methods**: `snake_case` - `set_brightness`
- **Constants**: `UPPER_SNAKE_CASE` - `MAX_BRIGHTNESS`
- **Private methods**: `_snake_case` - `_apply_geometry`
- **Variables**: `snake_case` - `current_value`

### Comments

- Use comments sparingly - code should be self-explanatory
- Explain *why*, not *what*
- Keep comments up-to-date

```python
# Good
# Limit alpha to prevent oversaturation on OLED displays
alpha = min(alpha, 220)

# Not so good
# Set alpha to min of alpha and 220
alpha = min(alpha, 220)
```

## Testing

Currently, testing is manual. Future contributions for automated testing are welcome!

### Manual Testing Checklist

- [ ] Application starts without errors
- [ ] Overlay displays correctly
- [ ] All controls respond properly
- [ ] Settings are applied in real-time
- [ ] Color picker works
- [ ] Toggle on/off works
- [ ] Panic button works
- [ ] Close button exits cleanly
- [ ] No errors in console
- [ ] Performs well (no lag)

## Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development tools (optional)
pip install mypy pylint black

# Run the application
python ringlight_improved.py
```

## Project Structure

```
ringlight/
├── ringlight_improved.py  # Main application
├── requirements.txt       # Dependencies
├── README.md             # User documentation
├── CONTRIBUTING.md       # This file
├── LICENSE               # MIT License
└── .gitignore           # Git ignore rules
```

## Areas for Contribution

We welcome contributions in these areas:

### High Priority
- [ ] Windows compatibility testing and fixes
- [ ] macOS compatibility testing and fixes
- [ ] Wayland support improvements
- [ ] Multi-monitor support
- [ ] Configuration file for persistent settings

### Medium Priority
- [ ] Preset lighting configurations
- [ ] Keyboard shortcuts
- [ ] System tray integration
- [ ] Animation effects
- [ ] More gradient patterns

### Nice to Have
- [ ] Automated tests
- [ ] CI/CD pipeline
- [ ] Installer scripts
- [ ] Video tutorials
- [ ] Translation/i18n support

## Questions?

- Open an issue for questions
- Tag with `question` label
- We're here to help!

## Recognition

Contributors will be acknowledged in:
- README.md Contributors section
- Release notes
- Project documentation

Thank you for contributing! 🎉
