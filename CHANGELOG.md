# Changelog

All notable changes to Ring Light Overlay will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-14

### Added - Major Code Quality Improvements
- Comprehensive English documentation for international developers
- Type hints throughout the codebase for better IDE support
- Google-style docstrings for all classes and methods
- Logging system for debugging and monitoring
- Configuration class (`RingLightConfig`) with all constants centralized
- Helper methods for rendering gradients (better code organization)
- Error handling in main function
- README.md with complete usage instructions
- CONTRIBUTING.md with contribution guidelines
- requirements.txt for easy dependency installation
- LICENSE file (MIT License)
- .gitignore for clean repository
- CHANGELOG.md (this file)

### Changed
- Refactored code structure for better maintainability
- Improved variable names (English, descriptive)
- Separated concerns into helper methods
- Enhanced comments and documentation
- UI text translated to English for wider audience
- Better code organization following SOLID principles

### Technical Improvements
- Type safety with full type hints
- Constants extracted from magic numbers
- Logging instead of print statements
- Error handling for robustness
- More descriptive method names
- Better separation of UI creation logic

## [1.0.0] - Initial Version

### Features
- Virtual ring light overlay
- Customizable brightness (0-200%)
- Adjustable thickness (1-900px)
- Color picker
- Multi-layer bloom effect
- Click-through transparent overlay
- Control panel with real-time adjustments
- Panic button for emergency shutdown
- Screen geometry auto-detection
- Always-on-top overlay

---

## Version Numbering

- **Major**: Breaking changes or significant rewrites
- **Minor**: New features, backwards compatible
- **Patch**: Bug fixes, minor improvements
