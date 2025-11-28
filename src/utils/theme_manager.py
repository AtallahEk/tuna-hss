class ThemeManager:
    """Tema yöneticisi"""
    
    # Karanlık Tema (Varsayılan)
    DARK_THEME = {
        "primary": "#0a0a0a",
        "secondary": "#1a1a1a",
        "accent": "#00ff88",
        "danger": "#ff3366",
        "warning": "#ffaa00",
        "success": "#00cc66",
        "info": "#0099ff",
        "text": "#e0e0e0",
        "border": "#333333"
    }
    
    # Aydınlık Tema
    LIGHT_THEME = {
        "primary": "#f5f5f5",
        "secondary": "#ffffff",
        "accent": "#00cc66",
        "danger": "#ff3366",
        "warning": "#ffaa00",
        "success": "#00cc66",
        "info": "#0099ff",
        "text": "#1a1a1a",
        "border": "#cccccc"
    }
    
    # Gece Görüşü Tema (Yeşil tonlar)
    NIGHT_VISION_THEME = {
        "primary": "#001100",
        "secondary": "#002200",
        "accent": "#00ff00",
        "danger": "#ff3366",
        "warning": "#ffaa00",
        "success": "#00cc00",
        "info": "#00ff00",
        "text": "#00ff00",
        "border": "#004400"
    }
    
    # Mavi Tema
    BLUE_THEME = {
        "primary": "#0a0a1a",
        "secondary": "#1a1a2a",
        "accent": "#00aaff",
        "danger": "#ff3366",
        "warning": "#ffaa00",
        "success": "#00cc66",
        "info": "#0099ff",
        "text": "#e0e0ff",
        "border": "#333355"
    }
    
    def __init__(self):
        self.current_theme = "dark"
        self.themes = {
            "dark": self.DARK_THEME,
            "light": self.LIGHT_THEME,
            "night": self.NIGHT_VISION_THEME,
            "blue": self.BLUE_THEME
        }
    
    def get_theme(self, name=None):
        """Tema renklerini al"""
        if name is None:
            name = self.current_theme
        return self.themes.get(name, self.DARK_THEME)
    
    def set_theme(self, name):
        """Temayı değiştir"""
        if name in self.themes:
            self.current_theme = name
            return True
        return False
    
    def get_stylesheet(self, widget_type, theme_name=None):
        """Widget için stylesheet üret"""
        colors = self.get_theme(theme_name)
        
        if widget_type == "main_window":
            return f"""
            QMainWindow {{
                background-color: {colors['primary']};
            }}
            """
        
        elif widget_type == "button":
            return f"""
            QPushButton {{
                background-color: {colors['secondary']};
                color: {colors['text']};
                border: 2px solid {colors['border']};
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 12px;
                font-weight: bold;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {colors['accent']};
                color: {colors['primary']};
                border-color: {colors['accent']};
            }}
            QPushButton:pressed {{
                background-color: {colors['success']};
            }}
            """
        
        elif widget_type == "panel":
            return f"""
            QWidget {{
                background-color: {colors['secondary']};
                border: 2px solid {colors['border']};
                border-radius: 5px;
            }}
            QLabel {{
                color: {colors['text']};
            }}
            """
        
        return ""