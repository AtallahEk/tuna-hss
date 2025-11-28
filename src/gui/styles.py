# GUI renk ve stil tanımları

COLOR_PRIMARY = "#0a0a0a"      # Ana arka plan
COLOR_SECONDARY = "#1a1a1a"    # İkincil arka plan
COLOR_ACCENT = "#00ff88"       # Vurgu (yeşil)
COLOR_DANGER = "#ff3366"       # Tehlike (kırmızı)
COLOR_WARNING = "#ffaa00"      # Uyarı (turuncu)
COLOR_SUCCESS = "#00cc66"      # Başarı
COLOR_INFO = "#0099ff"         # Bilgi (mavi)
COLOR_TEXT = "#e0e0e0"         # Metin
COLOR_BORDER = "#333333"       # Kenarlık

MAIN_WINDOW_STYLE = f"""
QMainWindow {{
    background-color: {COLOR_PRIMARY};
}}
"""

TOP_BAR_STYLE = f"""
QWidget {{
    background-color: {COLOR_SECONDARY};
    border-bottom: 2px solid {COLOR_ACCENT};
}}
QLabel {{
    color: {COLOR_TEXT};
    font-size: 14px;
    font-weight: bold;
    padding: 5px;
}}
"""

CAMERA_PANEL_STYLE = f"""
QLabel {{
    background-color: {COLOR_SECONDARY};
    border: 2px solid {COLOR_BORDER};
    border-radius: 5px;
}}
"""

INFO_BAR_STYLE = f"""
QWidget {{
    background-color: {COLOR_SECONDARY};
    border: 2px solid {COLOR_BORDER};
    border-radius: 5px;
    padding: 10px;
}}
QLabel {{
    color: {COLOR_TEXT};
    font-size: 13px;
    padding: 5px;
}}
"""

CONTROL_BAR_STYLE = f"""
QWidget {{
    background-color: {COLOR_SECONDARY};
    border: 2px solid {COLOR_BORDER};
    border-radius: 5px;
    padding: 10px;
}}
"""

BUTTON_STYLE = f"""
QPushButton {{
    background-color: {COLOR_SECONDARY};
    color: {COLOR_TEXT};
    border: 2px solid {COLOR_BORDER};
    border-radius: 5px;
    padding: 8px 15px;
    font-size: 12px;
    font-weight: bold;
    min-width: 100px;
}}
QPushButton:hover {{
    background-color: {COLOR_ACCENT};
    color: {COLOR_PRIMARY};
    border-color: {COLOR_ACCENT};
}}
QPushButton:pressed {{
    background-color: {COLOR_SUCCESS};
}}
QPushButton:disabled {{
    background-color: #0f0f0f;
    color: #555555;
    border-color: #222222;
}}
"""

BUTTON_DANGER_STYLE = f"""
QPushButton {{
    background-color: {COLOR_DANGER};
    color: white;
    border: 2px solid {COLOR_DANGER};
    border-radius: 5px;
    padding: 8px 15px;
    font-size: 12px;
    font-weight: bold;
    min-width: 100px;
}}
QPushButton:hover {{
    background-color: #ff5588;
    border-color: #ff5588;
}}
QPushButton:pressed {{
    background-color: #cc1144;
}}
"""

BUTTON_SUCCESS_STYLE = f"""
QPushButton {{
    background-color: {COLOR_SUCCESS};
    color: white;
    border: 2px solid {COLOR_SUCCESS};
    border-radius: 5px;
    padding: 8px 15px;
    font-size: 12px;
    font-weight: bold;
    min-width: 100px;
}}
QPushButton:hover {{
    background-color: #00ff88;
    border-color: #00ff88;
}}
QPushButton:pressed {{
    background-color: #009955;
}}
"""

TOGGLE_BUTTON_ACTIVE_STYLE = f"""
QPushButton {{
    background-color: {COLOR_ACCENT};
    color: {COLOR_PRIMARY};
    border: 2px solid {COLOR_ACCENT};
    border-radius: 5px;
    padding: 8px 15px;
    font-size: 12px;
    font-weight: bold;
    min-width: 100px;
}}
"""

SLIDER_STYLE = f"""
QSlider::groove:horizontal {{
    border: 1px solid {COLOR_BORDER};
    height: 8px;
    background: {COLOR_SECONDARY};
    margin: 2px 0;
    border-radius: 4px;
}}
QSlider::handle:horizontal {{
    background: {COLOR_ACCENT};
    border: 2px solid {COLOR_ACCENT};
    width: 18px;
    margin: -5px 0;
    border-radius: 9px;
}}
QSlider::handle:horizontal:hover {{
    background: {COLOR_SUCCESS};
    border-color: {COLOR_SUCCESS};
}}
QSlider::sub-page:horizontal {{
    background: {COLOR_ACCENT};
    border-radius: 4px;
}}
"""

LOG_PANEL_STYLE = f"""
QTextEdit {{
    background-color: {COLOR_SECONDARY};
    color: {COLOR_TEXT};
    border: 2px solid {COLOR_BORDER};
    border-radius: 5px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11px;
    padding: 5px;
}}
"""

SPINBOX_STYLE = f"""
QSpinBox {{
    background-color: {COLOR_SECONDARY};
    color: {COLOR_TEXT};
    border: 2px solid {COLOR_BORDER};
    border-radius: 5px;
    padding: 5px;
    font-size: 12px;
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {COLOR_ACCENT};
    border-radius: 3px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {COLOR_SUCCESS};
}}
"""

DIALOG_STYLE = f"""
QDialog {{
    background-color: {COLOR_PRIMARY};
}}
QLabel {{
    color: {COLOR_TEXT};
    font-size: 12px;
}}
"""