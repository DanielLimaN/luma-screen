#!/usr/bin/env python3
"""
LumaScreen - A virtual ring light overlay for video calls and streaming.

This application creates a customizable luminous border effect around your screen
to improve lighting during video calls, streaming, or content creation.

Features:
    - Customizable brightness (0-200%)
    - Adjustable thickness (1-900px)
    - Color selection with live preview
    - Click-through transparent overlay
    - Preset configurations for quick setup
    - Auto-adapts to screen resolution changes

Author: Free contribution to the community
License: MIT
Version: 1.0.0
Python: >=3.10
"""

import sys
import logging
import os
from typing import Optional, Final

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QColorDialog,
    QSpinBox,
    QGroupBox,
    QFrame,
)
from PySide6.QtCore import Qt, QRect, QRectF, QTimer
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QPainterPath, QCloseEvent

# Application metadata
__version__: Final[str] = "1.0.0"
__author__: Final[str] = "Open Source Community"
__license__: Final[str] = "MIT"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
class RingLightConfig:
    """
    Configuration constants for the ring light application.
    
    This class centralizes all configuration values, limits, and defaults
    to maintain consistency across the application and facilitate customization.
    """
    
    # Default values
    DEFAULT_THICKNESS: Final[int] = 220
    DEFAULT_BRIGHTNESS: Final[float] = 1.0  # 100% brightness
    DEFAULT_COLOR: Final[tuple[int, int, int]] = (255, 255, 255)  # White
    
    # Limits
    MIN_THICKNESS: Final[int] = 1
    MAX_THICKNESS: Final[int] = 900
    MIN_BRIGHTNESS_PERCENT: Final[int] = 0
    MAX_BRIGHTNESS_PERCENT: Final[int] = 200
    MIN_BRIGHTNESS: Final[float] = 0.0
    MAX_BRIGHTNESS: Final[float] = 2.0
    MAX_ALPHA: Final[int] = 220  # Safety cap for alpha channel
    
    # UI Update intervals (milliseconds)
    GEOMETRY_POLL_INTERVAL_MS: Final[int] = 1000
    
    # Window dimensions
    MIN_CONTROL_PANEL_WIDTH: Final[int] = 520
    COLOR_PREVIEW_WIDTH: Final[int] = 70
    COLOR_PREVIEW_HEIGHT: Final[int] = 22
    
    # Layout spacing
    LAYOUT_SPACING: Final[int] = 12
    
    # Border margin from screen edges
    SCREEN_MARGIN: Final[int] = 10
    
    # Outer corner radius for rounded corners
    OUTER_CORNER_RADIUS: Final[int] = 20
    
    # Bloom effect layers (intensity, size_multiplier) - for future use
    BLOOM_LAYERS: Final[list[tuple[float, float]]] = [
        (1.00, 1.00),
        (0.70, 0.75),
        (0.45, 0.55),
        (0.25, 0.40),
    ]


class RingLightOverlay(QWidget):
    """
    Transparent overlay widget that renders a customizable ring light effect.
    
    This widget creates a frameless, always-on-top window that covers the entire
    screen and renders a gradient-based ring light effect around the edges.
    The overlay is click-through, allowing interaction with underlying windows.
    
    Attributes:
        thickness (int): Thickness of the ring light in pixels.
        brightness (float): Brightness multiplier (0.0 to 2.0).
        color (QColor): Base color of the ring light.
    """
    
    def __init__(self) -> None:
        """Initialize the ring light overlay with default settings."""
        super().__init__()
        
        # Initialize properties with default values
        self.thickness: int = RingLightConfig.DEFAULT_THICKNESS
        self.brightness: float = RingLightConfig.DEFAULT_BRIGHTNESS
        self.color: QColor = QColor(*RingLightConfig.DEFAULT_COLOR)
        
        # Configure window to be frameless, always on top, and click-through
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        # Apply initial screen geometry
        self._apply_screen_geometry()
        self.show()
        
        # Set up timer to monitor screen geometry changes
        self._poll_timer: QTimer = QTimer(self)
        self._poll_timer.timeout.connect(self._apply_screen_geometry)
        self._poll_timer.start(RingLightConfig.GEOMETRY_POLL_INTERVAL_MS)
        
        logger.info("Ring light overlay initialized")

    def _apply_screen_geometry(self) -> None:
        """
        Apply the primary screen's geometry to this overlay window.
        
        This method ensures the overlay always covers the entire primary screen,
        even if the screen resolution or configuration changes.
        """
        screen = QApplication.primaryScreen()
        if not screen:
            logger.warning("No primary screen found")
            return
            
        geom = screen.geometry()
        if self.geometry() != geom:
            self.setGeometry(geom)
            self.update()
            logger.debug(f"Screen geometry updated: {geom.width()}x{geom.height()}")
    
    def set_brightness_percent(self, value_0_200: int) -> None:
        """
        Set the brightness level as a percentage.
        
        Args:
            value_0_200: Brightness percentage (0-200, where 100 is normal).
        
        Raises:
            ValueError: If value is not within valid range.
        """
        if not isinstance(value_0_200, (int, float)):
            raise ValueError(f"Brightness must be numeric, got {type(value_0_200)}")
        
        if not (RingLightConfig.MIN_BRIGHTNESS_PERCENT <= value_0_200 <= RingLightConfig.MAX_BRIGHTNESS_PERCENT):
            logger.warning(
                f"Brightness {value_0_200}% out of range "
                f"({RingLightConfig.MIN_BRIGHTNESS_PERCENT}-{RingLightConfig.MAX_BRIGHTNESS_PERCENT}%), clamping"
            )
        
        self.brightness = max(
            RingLightConfig.MIN_BRIGHTNESS,
            min(RingLightConfig.MAX_BRIGHTNESS, value_0_200 / 100.0)
        )
        self.update()
        logger.debug(f"Brightness set to {value_0_200}% ({self.brightness:.2f})")
    
    def set_thickness(self, pixels: int) -> None:
        """
        Set the thickness of the ring light effect.
        
        Args:
            pixels: Thickness in pixels (minimum 1).
        
        Raises:
            ValueError: If pixels is not a valid integer.
        """
        if not isinstance(pixels, (int, float)):
            raise ValueError(f"Thickness must be numeric, got {type(pixels)}")
        
        if pixels < RingLightConfig.MIN_THICKNESS:
            logger.warning(f"Thickness {pixels}px below minimum, clamping to {RingLightConfig.MIN_THICKNESS}px")
        
        self.thickness = max(RingLightConfig.MIN_THICKNESS, int(pixels))
        self.update()
        logger.debug(f"Thickness set to {self.thickness}px")
    
    def set_color(self, new_color: Optional[QColor]) -> None:
        """
        Set the base color of the ring light.
        
        Args:
            new_color: The new color to use. Must be a valid QColor instance.
        
        Raises:
            ValueError: If color is not a valid QColor.
        """
        if new_color is None:
            logger.warning("Attempted to set None color, ignoring")
            return
        
        if not isinstance(new_color, QColor):
            raise ValueError(f"Color must be QColor instance, got {type(new_color)}")
        
        if not new_color.isValid():
            logger.warning("Attempted to set invalid color, ignoring")
            return
        
        self.color = new_color
        self.update()
        logger.debug(
            f"Color set to RGB({new_color.red()}, {new_color.green()}, "
            f"{new_color.blue()})"
        )

    def paintEvent(self, event) -> None:
        """
        Render the ring light effect as a continuous frame with rounded corners.
        
        Adapts to screen size and configured thickness.
        
        Args:
            event: Qt paint event (unused but required by Qt).
        """
        painter = QPainter(self)
        try:
            painter.setCompositionMode(QPainter.CompositionMode_Screen)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            width = self.width()
            height = self.height()
            
            # Validate dimensions
            if width <= 0 or height <= 0:
                logger.warning(f"Invalid dimensions: {width}x{height}")
                return
            
            margin = RingLightConfig.SCREEN_MARGIN
            radius = RingLightConfig.OUTER_CORNER_RADIUS
            
            # Calculate maximum safe thickness
            min_dimension = min(width, height)
            max_thickness = max(
                RingLightConfig.MIN_THICKNESS, 
                min_dimension // 2 - margin
            )
            effective_thickness = min(self.thickness, max_thickness)

            # Prepare color with brightness-adjusted alpha
            solid_color = QColor(self.color)
            alpha = int(255 * self.brightness)
            alpha = max(0, min(255, alpha))
            solid_color.setAlpha(alpha)

            # Define outer border rectangle
            outer_rect = QRectF(
                margin,
                margin,
                width - 2 * margin,
                height - 2 * margin
            )
            
            # Define inner border rectangle
            inner_rect = QRectF(
                margin + effective_thickness,
                margin + effective_thickness,
                width - 2 * (margin + effective_thickness),
                height - 2 * (margin + effective_thickness)
            )

            # Create outer path with rounded corners
            outer_path = QPainterPath()
            outer_path.addRoundedRect(outer_rect, radius, radius)
            
            # Create inner path with scaled radius
            inner_path = QPainterPath()
            inner_radius = max(0, radius - effective_thickness)
            inner_path.addRoundedRect(inner_rect, inner_radius, inner_radius)
            
            # Subtract inner from outer to create border frame
            border_path = outer_path.subtracted(inner_path)

            painter.fillPath(border_path, solid_color)
        
        except Exception as e:
            logger.error(f"Error in paintEvent: {e}", exc_info=True)
        
        finally:
            painter.end()


class ControlPanel(QMainWindow):
    """
    Control panel window for managing ring light settings.
    
    This window provides user interface controls for adjusting the ring light's
    brightness, thickness, and color. It also includes toggle and shutdown controls.
    
    Attributes:
        overlay (RingLightOverlay): The overlay widget being controlled.
    """
    
    def __init__(self, overlay: RingLightOverlay) -> None:
        """
        Initialize the control panel.
        
        Args:
            overlay: The RingLightOverlay instance to control.
        
        Raises:
            ValueError: If overlay is None or not a RingLightOverlay instance.
        """
        if overlay is None:
            raise ValueError("Overlay cannot be None")
        
        if not isinstance(overlay, RingLightOverlay):
            raise ValueError(f"Overlay must be RingLightOverlay instance, got {type(overlay)}")
        
        super().__init__()
        self.overlay: RingLightOverlay = overlay
        
        self._setup_ui()
        self._set_window_icon()
        logger.info("Control panel initialized")
    
    def _set_window_icon(self) -> None:
        """Set application window icon using embedded SVG."""
        from PySide6.QtGui import QIcon, QPixmap
        from PySide6.QtSvg import QSvgRenderer
        from PySide6.QtCore import QByteArray
        
        # Embedded SVG icon
        svg_data = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">
  <circle cx="128" cy="128" r="110" fill="#4CAF50" stroke="#45a049" stroke-width="2"/>
  <circle cx="128" cy="128" r="80" fill="none" stroke="white" stroke-width="0"/>
  <circle cx="128" cy="128" r="80" fill="rgba(0,0,0,0)"/>
  <path d="M 28 128 A 100 100 0 0 1 228 128" fill="none" stroke="#81C784" stroke-width="8" stroke-linecap="round"/>
</svg>"""
        
        try:
            # Create QPixmap from SVG
            renderer = QSvgRenderer(QByteArray(svg_data.encode()))
            pixmap = QPixmap(64, 64)
            pixmap.fill(0x00000000)  # Transparent
            
            from PySide6.QtGui import QPainter
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            
            icon = QIcon(pixmap)
            self.setWindowIcon(icon)
            logger.debug("Window icon set from embedded SVG")
        except Exception as e:
            logger.warning(f"Could not set window icon: {e}")
    
    def _setup_ui(self) -> None:
        """Configure the user interface layout and widgets."""
        self.setWindowTitle("💡 LumaScreen — Control Panel")
        self.setMinimumWidth(RingLightConfig.MIN_CONTROL_PANEL_WIDTH)
        
        # Widget e layout principal
        root_widget = QWidget()
        layout = QVBoxLayout(root_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Grupo de ajustes do efeito
        effect_group = QGroupBox("⚙️ Settings")
        effect_layout = QVBoxLayout()
        effect_layout.setSpacing(12)
        
        effect_layout.addLayout(self._create_brightness_control())
        effect_layout.addLayout(self._create_thickness_control())
        effect_layout.addLayout(self._create_color_control())
        effect_group.setLayout(effect_layout)
        layout.addWidget(effect_group)
        
        # Presets rápidos
        presets_group = QGroupBox("⭐ Presets")
        presets_layout = QHBoxLayout()
        presets_layout.addLayout(self._create_presets())
        presets_group.setLayout(presets_layout)
        layout.addWidget(presets_group)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Controles de ação
        layout.addLayout(self._create_action_buttons())
        
        # Dica
        hint_label = QLabel(
            "💡 <i>Tip: Use presets to get started quickly!</i>"
        )
        hint_label.setStyleSheet("color: #666; padding: 5px;")
        hint_label.setWordWrap(True)
        layout.addWidget(hint_label)
        
        layout.addStretch()
        self.setCentralWidget(root_widget)
    
    def _create_brightness_control(self) -> QVBoxLayout:
        """Cria e retorna o controle de brilho."""
        container = QVBoxLayout()
        
        # Label e valor
        header = QHBoxLayout()
        label = QLabel("☀️ Brightness")
        label.setStyleSheet("font-weight: bold;")
        header.addWidget(label)
        header.addStretch()
        self.brightness_value = QLabel("100%")
        self.brightness_value.setStyleSheet("color: #0066cc; font-weight: bold;")
        header.addWidget(self.brightness_value)
        container.addLayout(header)
        
        # Slider
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(
            RingLightConfig.MIN_BRIGHTNESS_PERCENT,
            RingLightConfig.MAX_BRIGHTNESS_PERCENT
        )
        self.brightness_slider.setValue(int(self.overlay.brightness * 100))
        self.brightness_slider.setToolTip(
            "Adjust brightness from 0% to 200%\n"
            "Recommended: 80-140% for general use"
        )
        container.addWidget(self.brightness_slider)
        
        self.brightness_slider.valueChanged.connect(self._on_brightness_changed)
        return container
    
    def _create_thickness_control(self) -> QVBoxLayout:
        """Cria e retorna o controle de espessura."""
        container = QVBoxLayout()
        
        # Label e valor
        header = QHBoxLayout()
        label = QLabel("📏 Thickness")
        label.setStyleSheet("font-weight: bold;")
        header.addWidget(label)
        header.addStretch()
        self.thickness_value = QLabel("220px")
        self.thickness_value.setStyleSheet("color: #0066cc; font-weight: bold;")
        header.addWidget(self.thickness_value)
        container.addLayout(header)
        
        # Slider
        self.thickness_slider = QSlider(Qt.Horizontal)
        self.thickness_slider.setRange(
            RingLightConfig.MIN_THICKNESS,
            RingLightConfig.MAX_THICKNESS
        )
        self.thickness_slider.setValue(self.overlay.thickness)
        self.thickness_slider.setToolTip(
            "Adjust ring light border thickness\n"
            "Recommended: 200-350px for general use"
        )
        container.addWidget(self.thickness_slider)
        
        self.thickness_slider.valueChanged.connect(self._on_thickness_changed)
        return container
    
    def _create_color_control(self) -> QVBoxLayout:
        """Cria e retorna o controle de cor."""
        container = QVBoxLayout()
        
        # Label
        label = QLabel("🎨 Color")
        label.setStyleSheet("font-weight: bold;")
        container.addWidget(label)
        
        # Botão e preview
        row = QHBoxLayout()
        self.color_btn = QPushButton("Choose Color")
        self.color_btn.setToolTip("Click to select a custom color")
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(100, 30)
        self._update_color_preview()
        
        row.addWidget(self.color_btn)
        row.addWidget(self.color_preview)
        row.addStretch()
        container.addLayout(row)
        
        self.color_btn.clicked.connect(self._pick_color)
        return container
    
    def _create_presets(self) -> QHBoxLayout:
        """Cria botões de presets rápidos."""
        row = QHBoxLayout()
        
        warm_btn = QPushButton("🌅 Warm")
        warm_btn.setToolTip("Warm light (100%, 250px, yellowish)")
        warm_btn.clicked.connect(lambda: self._apply_preset(100, 250, QColor(255, 240, 220)))
        
        cool_btn = QPushButton("❄️ Cool")
        cool_btn.setToolTip("Cool light (120%, 280px, white)")
        cool_btn.clicked.connect(lambda: self._apply_preset(120, 280, QColor(255, 255, 255)))
        
        soft_btn = QPushButton("🌙 Soft")
        soft_btn.setToolTip("Soft light (80%, 300px, slightly yellow)")
        soft_btn.clicked.connect(lambda: self._apply_preset(80, 300, QColor(255, 250, 240)))
        
        intense_btn = QPushButton("⚡ Intense")
        intense_btn.setToolTip("Intense light (150%, 200px, pure white)")
        intense_btn.clicked.connect(lambda: self._apply_preset(150, 200, QColor(255, 255, 255)))
        
        row.addWidget(warm_btn)
        row.addWidget(cool_btn)
        row.addWidget(soft_btn)
        row.addWidget(intense_btn)
        
        return row
    
    def _create_action_buttons(self) -> QVBoxLayout:
        """Cria e retorna os botões de ação."""
        container = QVBoxLayout()
        container.setSpacing(8)
        
        # Toggle button (principal)
        self.toggle_btn = QPushButton("⏸️ Turn Off Screen Light")
        self.toggle_btn.setStyleSheet(
            "QPushButton { padding: 10px; font-weight: bold; background-color: #4CAF50; color: white; }"
            "QPushButton:hover { background-color: #45a049; }"
        )
        self.toggle_btn.setToolTip("Turn the screen light effect on or off")
        
        # Linha com panic e fechar
        bottom_row = QHBoxLayout()
        self.panic_btn = QPushButton("🚨 PANIC")
        self.panic_btn.setStyleSheet(
            "QPushButton { padding: 8px; background-color: #f44336; color: white; }"
            "QPushButton:hover { background-color: #da190b; }"
        )
        self.panic_btn.setToolTip("Immediately turn off in case of problems")
        
        self.close_btn = QPushButton("❌ Close All")
        self.close_btn.setStyleSheet("QPushButton { padding: 8px; }")
        self.close_btn.setToolTip("Close the application completely")
        
        bottom_row.addWidget(self.panic_btn)
        bottom_row.addWidget(self.close_btn)
        
        container.addWidget(self.toggle_btn)
        container.addLayout(bottom_row)
        
        self.toggle_btn.clicked.connect(self._toggle_overlay)
        self.panic_btn.clicked.connect(self._panic_off)
        self.close_btn.clicked.connect(self._close_all)
        
        return container

    def _on_brightness_changed(self, value: int) -> None:
        """
        Atualiza o brilho quando o slider muda.
        
        Args:
            value: Novo valor de brilho em porcentagem (0-200).
        """
        self.brightness_value.setText(f"{value}%")
        self.overlay.set_brightness_percent(value)
    
    def _on_thickness_changed(self, value: int) -> None:
        """
        Atualiza a espessura quando o slider muda.
        
        Args:
            value: Novo valor de espessura em pixels.
        """
        self.thickness_value.setText(f"{value}px")
        self.overlay.set_thickness(value)
    
    def _apply_preset(self, brightness: int, thickness: int, color: QColor) -> None:
        """
        Aplica um preset de configurações.
        
        Args:
            brightness: Brilho em porcentagem.
            thickness: Espessura em pixels.
            color: Cor da luz.
        """
        self.brightness_slider.setValue(brightness)
        self.thickness_slider.setValue(thickness)
        self.overlay.set_color(color)
        self._update_color_preview()
        logger.info(f"Preset aplicado: {brightness}%, {thickness}px")
    
    def _pick_color(self) -> None:
        """Abre o seletor de cores e atualiza a cor da luz."""
        chosen_color = QColorDialog.getColor(
            self.overlay.color,
            self,
            "Choose Screen Light Color"
        )
        if chosen_color.isValid():
            self.overlay.set_color(chosen_color)
            self._update_color_preview()
    
    def _update_color_preview(self) -> None:
        """Atualiza o preview da cor atual."""
        current_color = self.overlay.color
        self.color_preview.setStyleSheet(
            f"background-color: rgb({current_color.red()}, "
            f"{current_color.green()}, {current_color.blue()}); "
            f"border: 2px solid #333; border-radius: 4px;"
        )
        self.color_preview.setToolTip(
            f"RGB({current_color.red()}, {current_color.green()}, {current_color.blue()})"
        )

    def _toggle_overlay(self) -> None:
        """Alterna a visibilidade do overlay."""
        if self.overlay.isVisible():
            self.overlay.hide()
            self.toggle_btn.setText("▶️ Turn On Screen Light")
            self.toggle_btn.setStyleSheet(
                "QPushButton { padding: 10px; font-weight: bold; background-color: #2196F3; color: white; }"
                "QPushButton:hover { background-color: #0b7dda; }"
            )
            logger.info("Screen light turned off")
        else:
            self.overlay.show()
            self.toggle_btn.setText("⏸️ Turn Off Screen Light")
            self.toggle_btn.setStyleSheet(
                "QPushButton { padding: 10px; font-weight: bold; background-color: #4CAF50; color: white; }"
                "QPushButton:hover { background-color: #45a049; }"
            )
            logger.info("Screen light turned on")
    
    def _panic_off(self) -> None:
        """
        Desligamento emergencial do overlay.
        
        Esconde imediatamente o overlay em caso de problemas.
        """
        self.overlay.hide()
        self.toggle_btn.setText("▶️ Turn On Screen Light")
        self.toggle_btn.setStyleSheet(
            "QPushButton { padding: 10px; font-weight: bold; background-color: #2196F3; color: white; }"
            "QPushButton:hover { background-color: #0b7dda; }"
        )
        logger.warning("Panic button pressed - screen light disabled")
    
    def _close_all(self) -> None:
        """Close the overlay and quit the application."""
        logger.info("Closing application")
        self.overlay.close()
        app = QApplication.instance()
        if app:
            app.quit()
    
    def closeEvent(self, event) -> None:
        """
        Handle control panel close event.
        
        When the control panel is closed, the entire application is terminated
        for safety and to prevent orphaned overlay windows.
        
        Args:
            event: The close event (provided by Qt).
        """
        self._close_all()


def main() -> int:
    """
    Main application entry point.
    
    Initializes the Qt application, creates the overlay and control panel,
    and starts the event loop.
    
    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    try:
        # Validate Python version
        if sys.version_info < (3, 10):
            logger.error("Python 3.10 or higher required")
            return 1
        
        app = QApplication(sys.argv)
        app.setApplicationName("LumaScreen")
        app.setOrganizationName("Open Source Community")
        
        logger.info("Starting LumaScreen application")
        
        # Create overlay and control panel
        overlay = RingLightOverlay()
        panel = ControlPanel(overlay)
        panel.show()
        
        exit_code = app.exec()
        logger.info(f"Application exiting with code {exit_code}")
        return exit_code
        
    except Exception as e:
        logger.error(f"Fatal application error: {e}", exc_info=True)
        return 1
    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0


if __name__ == "__main__":
    sys.exit(main())
