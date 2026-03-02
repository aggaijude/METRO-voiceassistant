import sys
import os
import threading
import subprocess
import numpy as np
import sounddevice as sd
from dotenv import load_dotenv, set_key

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QDialog, QLineEdit, QComboBox, 
                               QListWidget, QTabWidget, QFormLayout, QGroupBox, QStackedLayout, QFrame)
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QAction, QIcon, QRadialGradient, QPixmap, QPainterPath, QImage
from PySide6.QtCore import Qt, QTimer, Signal, QSize, QSettings, QPropertyAnimation, QEasingCurve, QRect, QRectF

import database

# Load environment variables
load_dotenv(".env")

# ---------------- THEMES ----------------
THEMES = {
    "Stock (Blue)": {
        "bg": "#06121f",
        "primary": "#00dcff",
        "secondary": "#78a0b4",
        "ring_outer": "#00d2ff",
        "ring_inner": "#ff9628",
        "core": "#00283c",
        "btn_bg": "rgba(0, 220, 255, 30)",
        "btn_border": "#00dcff",
        "btn_text": "#00dcff",
        "btn_hover": "rgba(0, 220, 255, 80)"
    },
    "Obsidian (Black)": {
        "bg": "#000000",
        "primary": "#ffffff",
        "secondary": "#aaaaaa",
        "ring_outer": "#ffffff",
        "ring_inner": "#cccccc",
        "core": "#222222",
        "btn_bg": "rgba(255, 255, 255, 30)",
        "btn_border": "#ffffff",
        "btn_text": "#ffffff",
        "btn_hover": "rgba(255, 255, 255, 80)"
    },
    "Ivory (White)": {
        "bg": "#ffffff",
        "primary": "#000000",
        "secondary": "#555555",
        "ring_outer": "#000000",
        "ring_inner": "#444444",
        "core": "#eeeeee",
        "btn_bg": "rgba(0, 0, 0, 10)",
        "btn_border": "#000000",
        "btn_text": "#000000",
        "btn_hover": "rgba(0, 0, 0, 30)"
    }
}

class HistoryPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("border: none; font-size: 14px; background-color: transparent;")
        layout.addWidget(self.list_widget)
        
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_history)
        
    def showEvent(self, event):
        self.refresh_history()
        self.refresh_timer.start(2000)
        super().showEvent(event)
        
    def hideEvent(self, event):
        self.refresh_timer.stop()
        super().hideEvent(event)

    def refresh_history(self):
        rows = database.get_history(50)
        self.list_widget.clear()
        for ts, source, cmd in rows:
            self.list_widget.addItem(f"[{ts}] {source}: {cmd}")

class SettingsPanel(QWidget):
    saved = Signal() # Signal to notify main window to reload settings

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("MetroAI", "VoiceAssistant")
        
        # Styles specific to this panel
        self.setStyleSheet("""
            QWidget { background-color: #0d1b2a; color: white; border-radius: 12px; }
            QLabel { color: #e0e1dd; font-size: 14px; background: transparent; }
            QLineEdit, QComboBox { 
                background-color: #1b263b; 
                color: white; 
                border: 1px solid #415a77; 
                padding: 5px; 
                border-radius: 4px;
            }
            QPushButton {
                background-color: #415a77;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #778da9; }
            QTabWidget::pane { border: 1px solid #415a77; }
            QTabBar::tab {
                background: #1b263b;
                color: #e0e1dd;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected { background: #415a77; }
        """)

        # Main Layout is a StackedLayout to switch between Settings and History
        self.stacked_layout = QStackedLayout(self)
        
        # --- Page 1: Settings ---
        self.settings_page = QWidget()
        self.init_settings_page()
        self.stacked_layout.addWidget(self.settings_page)
        
        # --- Page 2: History ---
        self.history_page = QWidget()
        self.init_history_page()
        self.stacked_layout.addWidget(self.history_page)

    def init_settings_page(self):
        layout = QVBoxLayout(self.settings_page)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Settings")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        close_btn = QPushButton("X")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("background-color: transparent; color: #888; font-size: 16px;")
        close_btn.clicked.connect(self.hide)
        header_layout.addWidget(close_btn)
        layout.addLayout(header_layout)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # API Tab
        self.api_tab = QWidget()
        self.init_api_tab()
        self.tabs.addTab(self.api_tab, "API Keys")

        # Theme Tab
        self.theme_tab = QWidget()
        self.init_theme_tab()
        self.tabs.addTab(self.theme_tab, "Appearance")

        # Action Buttons
        button_layout = QHBoxLayout()
        
        history_btn = QPushButton("View History")
        history_btn.clicked.connect(lambda: self.stacked_layout.setCurrentIndex(1))
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        
        button_layout.addWidget(history_btn)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

    def init_history_page(self):
        layout = QVBoxLayout(self.history_page)
        
        # Header
        header_layout = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.setFixedSize(80, 30)
        back_btn.clicked.connect(lambda: self.stacked_layout.setCurrentIndex(0))
        
        title = QLabel("Command History")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        
        header_layout.addWidget(back_btn)
        header_layout.addSpacing(10)
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # History Content
        self.history_panel_widget = HistoryPanel()
        layout.addWidget(self.history_panel_widget)

    def init_api_tab(self):
        layout = QFormLayout()
        self.api_tab.setLayout(layout)

        self.livekit_url = QLineEdit(os.getenv("LIVEKIT_URL", ""))
        self.livekit_api_key = QLineEdit(os.getenv("LIVEKIT_API_KEY", ""))
        self.livekit_api_secret = QLineEdit(os.getenv("LIVEKIT_API_SECRET", ""))
        self.gemini_api_key = QLineEdit(os.getenv("GEMINI_API_KEY", ""))
        
        self.livekit_api_secret.setEchoMode(QLineEdit.Password)
        self.gemini_api_key.setEchoMode(QLineEdit.Password)

        layout.addRow("LiveKit URL:", self.livekit_url)
        layout.addRow("LiveKit API Key:", self.livekit_api_key)
        layout.addRow("LiveKit API Secret:", self.livekit_api_secret)
        layout.addRow("Gemini API Key:", self.gemini_api_key)

    def init_theme_tab(self):
        layout = QVBoxLayout()
        self.theme_tab.setLayout(layout)
        
        group = QGroupBox("Theme Selection")
        form = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(THEMES.keys()))
        
        current_theme = self.settings.value("theme", "Stock (Blue)")
        index = self.theme_combo.findText(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        form.addRow("Color Theme:", self.theme_combo)
        group.setLayout(form)
        layout.addWidget(group)
        layout.addStretch()

    def save_settings(self):
        # Save to .env
        env_file = ".env"
        if not os.path.exists(env_file):
            with open(env_file, 'w') as f: f.write("")

        set_key(env_file, "LIVEKIT_URL", self.livekit_url.text())
        set_key(env_file, "LIVEKIT_API_KEY", self.livekit_api_key.text())
        set_key(env_file, "LIVEKIT_API_SECRET", self.livekit_api_secret.text())
        set_key(env_file, "GEMINI_API_KEY", self.gemini_api_key.text())
        
        # Save Theme
        selected_theme = self.theme_combo.currentText()
        self.settings.setValue("theme", selected_theme)
        
        self.saved.emit() # Notify parent
        self.hide()

class MetroUI(QWidget):
    def __init__(self):
        super().__init__()
        
        self.settings = QSettings("MetroAI", "VoiceAssistant")
        self.current_theme_name = self.settings.value("theme", "Stock (Blue)")
        self.colors = THEMES.get(self.current_theme_name, THEMES["Stock (Blue)"])

        self.setWindowTitle("METRO Voice Assistant")
        self.resize(900, 600)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.apply_theme()

        self.rotation = 0.0
        self.audio_level = 0.0
        
        # Audio visualization setup
        self.stream = sd.InputStream(
            channels=1,
            samplerate=16000,
            callback=self.audio_callback,
        )
        self.stream.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)
        
        # UI Elements
        self.init_ui_controls()

        # Settings Panel (Overlay)
        self.settings_panel = SettingsPanel(self)
        self.settings_panel.hide()
        self.settings_panel.saved.connect(self.reload_settings)

        # Database
        database.init_db()

        # Load Logo, remove background, crop to center square, and mask to circle
        original_pixmap = QPixmap("metro_logo.png")
        if not original_pixmap.isNull():
            # Convert to image for processing
            image = original_pixmap.toImage().convertToFormat(QImage.Format_ARGB32)
            
            # 1. Auto-detect and remove background (Black or White)
            # Check top-left pixel to guess background color
            bg_color = image.pixelColor(0, 0)
            is_black_bg = bg_color.red() < 30 and bg_color.green() < 30 and bg_color.blue() < 30
            is_white_bg = bg_color.red() > 225 and bg_color.green() > 225 and bg_color.blue() > 225
            
            if is_black_bg or is_white_bg:
                # Create a mask for the background
                for y in range(image.height()):
                    for x in range(image.width()):
                        pixel = image.pixelColor(x, y)
                        if is_black_bg:
                            if pixel.red() < 40 and pixel.green() < 40 and pixel.blue() < 40:
                                pixel.setAlpha(0)
                                image.setPixelColor(x, y, pixel)
                        elif is_white_bg:
                            if pixel.red() > 215 and pixel.green() > 215 and pixel.blue() > 215:
                                pixel.setAlpha(0)
                                image.setPixelColor(x, y, pixel)

            # 2. Crop to Center Square
            size = min(image.width(), image.height())
            x = (image.width() - size) // 2
            y = (image.height() - size) // 2
            
            # 3. Create Circular Mask
            target = QImage(size, size, QImage.Format_ARGB32)
            target.fill(Qt.transparent)
            
            painter = QPainter(target)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            
            path = QPainterPath()
            path.addEllipse(0, 0, size, size)
            painter.setClipPath(path)
            
            painter.drawImage(0, 0, image, sx=x, sy=y, sw=size, sh=size)
            painter.end()
            
            self.logo = QPixmap.fromImage(target)
        else:
            self.logo = original_pixmap
            print("Warning: Logo not found or invalid.")

    def reload_settings(self):
        # Reload env if changed
        load_dotenv(".env", override=True)
        
        # Reload theme
        new_theme = self.settings.value("theme", "Stock (Blue)")
        if new_theme != self.current_theme_name:
            self.current_theme_name = new_theme
            self.colors = THEMES.get(self.current_theme_name, THEMES["Stock (Blue)"])
            self.apply_theme()
            self.update() # Trigger repaint
        
        print("Settings updated and reloaded.")

    def resizeEvent(self, event):
        # Resize settings panel to cover most of the screen, centered
        if hasattr(self, 'settings_panel'):
            margin = 50
            w = self.width() - (margin * 2)
            h = self.height() - (margin * 2)
            self.settings_panel.setGeometry(margin, margin, w, h)
        super().resizeEvent(event)

    def apply_theme(self):
        self.setStyleSheet(f"background-color: {self.colors['bg']};")
        if hasattr(self, 'settings_btn'):
            self.apply_settings_btn_style()

    def apply_settings_btn_style(self):
        # Circular Icon Style
        btn_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {self.colors['primary']};
                border: none;
                font-weight: bold;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['btn_hover']};
                border-color: {self.colors['ring_outer']};
                color: {self.colors['ring_outer']};
            }}
            QPushButton:pressed {{
                background-color: {self.colors['btn_border']};
                color: {self.colors['bg']};
            }}
        """
        self.settings_btn.setStyleSheet(btn_style)

    def init_ui_controls(self):
        # Settings Icon (Top-Right)
        self.settings_btn = QPushButton("⚙", self)
        self.settings_btn.setFixedSize(40, 40)
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.clicked.connect(self.toggle_settings)
        self.apply_settings_btn_style()
        
        # Position manually in resizeEvent or use layout. 
        # Using absolute positioning relative to window corner for "Floating" feel
        self.settings_btn.move(self.width() - 60, 20)

    def resizeEvent(self, event):
        # Update settings button position
        if hasattr(self, 'settings_btn'):
            self.settings_btn.move(self.width() - 60, 20)
            
        # Update Settings Panel position
        if hasattr(self, 'settings_panel'):
            # Side panel style or centered overlay
            # Let's do a large centered overlay
            m_w = int(self.width() * 0.85)
            m_h = int(self.height() * 0.85)
            x = (self.width() - m_w) // 2
            y = (self.height() - m_h) // 2
            self.settings_panel.setGeometry(x, y, m_w, m_h)
            
        super().resizeEvent(event)

    def toggle_settings(self):
        if self.settings_panel.isVisible():
            self.settings_panel.hide()
        else:
            self.settings_panel.raise_()
            self.settings_panel.show()
            # Reset to settings page when opening
            self.settings_panel.stacked_layout.setCurrentIndex(0)



    def audio_callback(self, indata, frames, time, status):
        level = np.linalg.norm(indata) * 5
        self.audio_level = min(level, 1.0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()

        painter.setPen(QColor(self.colors['primary']))
        painter.setFont(QFont("Segoe UI", 18, QFont.Bold))
        painter.drawText(0, 45, width, 40, Qt.AlignCenter, "METRO – Voice Assistant")

        painter.setPen(QColor(self.colors['secondary']))
        painter.setFont(QFont("Segoe UI", 10))
        painter.drawText(0, 80, width, 30, Qt.AlignCenter, "Listening • Processing • Responding")

        cx = width // 2
        cy = height // 2 + 30

        painter.translate(cx, cy)
        
        # Save state to isolate rotation to rings only
        painter.save()
        painter.rotate(self.rotation)

        c_outer = QColor(self.colors['ring_outer'])
        c_inner = QColor(self.colors['ring_inner'])

        # Outer Ring
        pen = QPen(c_outer, 3)
        painter.setPen(pen)
        for i in range(0, 360, 12):
            painter.drawArc(-220, -220, 440, 440, i * 16, 6 * 16)

        # Inner Arcs
        pen = QPen(c_inner, 4)
        painter.setPen(pen)
        painter.drawArc(-200, -200, 400, 400, 40 * 16, 50 * 16)
        painter.drawArc(-200, -200, 400, 400, 220 * 16, 40 * 16)
        
        # Restore state to draw static core
        painter.restore()

        # Core (Static Logo)
        target_size = 180 # Matches the logo's inner ring geometry better
        offset = target_size // 2
        rect = QRectF(-offset, -offset, target_size, target_size)
        
        if hasattr(self, 'logo') and not self.logo.isNull():
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            
            # Draw the logo perfectly upright (0 degrees already due to restore())
            # Background removal is handled at the Pixmap level in __init__
            painter.drawPixmap(rect, self.logo, QRectF(self.logo.rect()))
        else:
            # Fallback if logo missing
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(self.colors['core']))
            painter.drawEllipse(-45, -45, 90, 90)

        self.rotation += 0.12 + self.audio_level * 0.3

# ==============================
# START UI HELPER
# ==============================
def start_ui():
    app = QApplication(sys.argv)
    ui = MetroUI()
    ui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    start_ui()
