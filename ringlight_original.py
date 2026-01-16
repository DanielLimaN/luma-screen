#!/usr/bin/env python3
"""
Ring Light Overlay - A virtual ring light for video calls and streaming.

This application creates a customizable ring light effect on your screen
to improve lighting during video calls, streaming, or content creation.

Author: Free contribution to the community
License: MIT
"""

import sys
import logging
from typing import Optional

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
)
from PySide6.QtCore import Qt, QRect, QTimer
from PySide6.QtGui import QPainter, QColor, QLinearGradient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Constants
class RingLightConfig:
    """Configuration constants for the ring light application."""
    
    # Default values
    DEFAULT_THICKNESS: int = 220
    DEFAULT_BRIGHTNESS: float = 0.80  # 80% brightness
    DEFAULT_COLOR: tuple[int, int, int] = (255, 255, 255)  # White
    
    # Limits
    MIN_THICKNESS: int = 1
    MAX_THICKNESS: int = 900
    MIN_BRIGHTNESS_PERCENT: int = 0
    MAX_BRIGHTNESS_PERCENT: int = 200
    MIN_BRIGHTNESS: float = 0.0
    MAX_BRIGHTNESS: float = 2.0
    MAX_ALPHA: int = 220  # Safety cap for alpha channel
    
    # UI Update intervals
    GEOMETRY_POLL_INTERVAL_MS: int = 1000
    
    # Window dimensions
    MIN_CONTROL_PANEL_WIDTH: int = 520
    COLOR_PREVIEW_WIDTH: int = 70
    COLOR_PREVIEW_HEIGHT: int = 22
    
    # Layout spacing
    LAYOUT_SPACING: int = 12
    
    # Bloom effect layers (intensity, size_multiplier)
    BLOOM_LAYERS: list[tuple[float, float]] = [
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
        """
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
        """
        self.thickness = max(RingLightConfig.MIN_THICKNESS, int(pixels))
        self.update()
        logger.debug(f"Thickness set to {self.thickness}px")
    
    def set_color(self, new_color: Optional[QColor]) -> None:
        """
        Set the base color of the ring light.
        
        Args:
            new_color: The new color to use. Must be a valid QColor instance.
        """
        if new_color and new_color.isValid():
            self.color = new_color
            self.update()
            logger.debug(
                f"Color set to RGB({new_color.red()}, {new_color.green()}, "
                f"{new_color.blue()})"
            )

    def paintEvent(self, event):
        p = QPainter(self)

        # Modo "luz", mas controlado (não aditivo bruto)
        p.setCompositionMode(QPainter.CompositionMode_Screen)

        w, h = self.width(), self.height()
        t = min(self.thickness, max(1, min(w, h)))

        base = QColor(self.color)

        # Bloom forte, mas sem “invadir” a tela inteira
        layers = [
            (1.00, 1.00),
            (0.70, 0.75),
            (0.45, 0.55),
            (0.25, 0.40),
        ]

        for intensity, mul in layers:
            size = max(1, int(t * mul))

            alpha = int(255 * self.brightness * intensity)
            # cap extra de segurança
            alpha = max(0, min(220, alpha))

            c = QColor(base)
            c.setAlpha(alpha)

            transparent = QColor(base)
            transparent.setAlpha(0)

            # TOP
            grad = QLinearGradient(0, 0, 0, size)
            grad.setColorAt(0, c)
            grad.setColorAt(1, transparent)
            p.fillRect(QRect(0, 0, w, size), grad)

            # BOTTOM
            grad = QLinearGradient(0, h, 0, h - size)
            grad.setColorAt(0, c)
            grad.setColorAt(1, transparent)
            p.fillRect(QRect(0, h - size, w, size), grad)

            # LEFT
            grad = QLinearGradient(0, 0, size, 0)
            grad.setColorAt(0, c)
            grad.setColorAt(1, transparent)
            p.fillRect(QRect(0, 0, size, h), grad)

            # RIGHT
            grad = QLinearGradient(w, 0, w - size, 0)
            grad.setColorAt(0, c)
            grad.setColorAt(1, transparent)
            p.fillRect(QRect(w - size, 0, size, h), grad)

        p.end()


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
        """
        super().__init__()
        self.overlay: RingLightOverlay = overlay
        
        self.setWindowTitle("Ring Light — Control Panel")
        self.setMinimumWidth(RingLightConfig.MIN_CONTROL_PANEL_WIDTH)
        
        # Create main layout
        root_widget = QWidget()
        layout = QVBoxLayout(root_widget)
        layout.setSpacing(RingLightConfig.LAYOUT_SPACING)
        
        # Brightness control (0-200%)
        brightness_row = self._create_brightness_control()
        layout.addLayout(brightness_row)
        
        # Thickness control
        thickness_row = self._create_thickness_control()
        layout.addLayout(thickness_row)
        
        # Color control
        color_row = self._create_color_control()
        layout.addLayout(color_row)
        
        # Action buttons
        actions_row = self._create_action_buttons()
        layout.addLayout(actions_row)
        
        # Helpful hint
        hint_label = QLabel(
            "Tip: Brightness 80-140% and thickness 200-350px usually works best."
        )
        hint_label.setStyleSheet("color: #666;")
        layout.addWidget(hint_label)
        
        self.setCentralWidget(root_widget)
        logger.info("Control panel initialized")
    
    def _create_brightness_control(self) -> QHBoxLayout:
        """Create and return the brightness control layout."""
        row = QHBoxLayout()
        row.addWidget(QLabel("Brightness:"))
        
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(
            RingLightConfig.MIN_BRIGHTNESS_PERCENT,
            RingLightConfig.MAX_BRIGHTNESS_PERCENT
        )
        self.brightness_slider.setValue(int(self.overlay.brightness * 100))
        self.brightness_value = QLabel(f"{self.brightness_slider.value()}%")
        
        row.addWidget(self.brightness_slider, 1)
        row.addWidget(self.brightness_value)
        
        self.brightness_slider.valueChanged.connect(self._on_brightness_changed)
        return row
    
    def _create_thickness_control(self) -> QHBoxLayout:
        """Create and return the thickness control layout."""
        row = QHBoxLayout()
        row.addWidget(QLabel("Thickness (px):"))
        
        self.thickness_spin = QSpinBox()
        self.thickness_spin.setRange(
            RingLightConfig.MIN_THICKNESS,
            RingLightConfig.MAX_THICKNESS
        )
        self.thickness_spin.setValue(self.overlay.thickness)
        
        row.addWidget(self.thickness_spin)
        row.addStretch(1)
        
        self.thickness_spin.valueChanged.connect(self.overlay.set_thickness)
        return row
    
    def _create_color_control(self) -> QHBoxLayout:
        """Create and return the color control layout."""
        row = QHBoxLayout()
        row.addWidget(QLabel("Color:"))
        
        self.color_btn = QPushButton("Choose Color…")
        self.color_preview = QLabel("   ")
        self.color_preview.setFixedWidth(RingLightConfig.COLOR_PREVIEW_WIDTH)
        self.color_preview.setFixedHeight(RingLightConfig.COLOR_PREVIEW_HEIGHT)
        self._update_color_preview()
        
        row.addWidget(_changed(self, value: int) -> None:
        """
        Handle brightness slider value changes.
        
        Args:
            value: New brightness percentage value (0-200).
        """
        self.brightness_value.setText(f"{value}%")
        self.overlay.set_brightness_percent(value)
    
    def _pick_color(self) -> None:
        """Open a color picker dialog and update the ring light color."""
        chosen_color = QColorDialog.getColor(
            self.overlay.color,
            self,
            "Select Ring Light Color"
        ) -> None:
        """Toggle the overlay visibility on/off."""
        if self.overlay.isVisible():
            self.overlay.hide()
            self.toggle_btn.setText("Turn On Overlay")
            logger.info("Overlay turned off")
        else:
            self.overlay.show()
            self.toggle_btn.setText("Turn Off Overlay")
            logger.info("Overlay turned on")
    
    def _panic_off(self) -> None:
        """
        Emergency overlay shutdown.
        
        Immediately hides the overlay. Useful if the overlay is interfering
        with other applications or causing issues.
        """
        self.overlay.hide()
        self.toggle_btn.setText("Turn On Overlay")
        logger.warning("Panic button pressed - overlay disabled")
    
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


def main() -> None:
    """
    Main application entry point.
    
    Initializes the Qt application, creates the overlay and control panel,
    and starts the event loop.
    """
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Ring Light")
        app.setOrganizationName("Open Source Community")
        
        logger.info("Starting Ring Light application")
        
        overlay = RingLightOverlay()
        panel = ControlPanel(overlay)
        panel.show()
        
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1Widget(self.panic_btn)
        row_actions.addWidget(self.close_btn)
        layout.addLayout(row_actions)

        self.toggle_btn.clicked.connect(self._toggle_overlay)
        self.panic_btn.clicked.connect(self._panic_off)
        self.close_btn.clicked.connect(self._close_all)

        hint = QLabel("Sugestão: Brilho 80–140% e espessura 200–350 costuma ficar ótimo.")
        hint.setStyleSheet("color: #666;")
        layout.addWidget(hint)

        self.setCentralWidget(root)

    def _on_brightness(self, v: int):
        self.brightness_value.setText(f"{v}%")
        self.overlay.set_brightness_percent(v)

    def _pick_color(self):
        chosen = QColorDialog.getColor(self.overlay.color, self, "Selecione a cor do ring light")
        if chosen.isValid():
            self.overlay.set_color(chosen)
            self._update_color_preview()

    def _update_color_preview(self):
        c = self.overlay.color
        self.color_preview.setStyleSheet(
            f"background-color: rgb({c.red()},{c.green()},{c.blue()}); border: 1px solid #444;"
        )

    def _toggle_overlay(self):
        if self.overlay.isVisible():
            self.overlay.hide()
            self.toggle_btn.setText("Ligar overlay")
        else:
            self.overlay.show()
            self.toggle_btn.setText("Desligar overlay")

    def _panic_off(self):
        self.overlay.hide()
        self.toggle_btn.setText("Ligar overlay")

    def _close_all(self):
        self.overlay.close()
        QApplication.instance().quit()

    def closeEvent(self, event):
        # se fechar o painel, encerra tudo (segurança)
        self._close_all()


def main():
    app = QApplication(sys.argv)
    overlay = RingLightOverlay()
    panel = ControlPanel(overlay)
    panel.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
