from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QBrush
from gui import styles


class StatusIndicator(QWidget):
    """Durum gösterge lambası"""
    
    def __init__(self, label_text):
        super().__init__()
        self.status = False  # False = kırmızı, True = yeşil
        self.label_text = label_text
        self.setFixedSize(150, 30)
    
    def set_status(self, status):
        """Durumu güncelle"""
        self.status = status
        self.update()
    
    def paintEvent(self, event):
        """Göstergeyi çiz"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # LED ışık
        color = QColor(styles.COLOR_SUCCESS) if self.status else QColor(styles.COLOR_DANGER)
        painter.setBrush(QBrush(color))
        painter.setPen(color)
        painter.drawEllipse(5, 7, 16, 16)
        
        # İç parlaklık efekti
        inner_color = QColor(255, 255, 255, 100)
        painter.setBrush(QBrush(inner_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(8, 10, 6, 6)
        
        # Metin
        painter.setPen(QColor(styles.COLOR_TEXT))
        painter.drawText(30, 20, self.label_text)


class SystemStatusWidget(QWidget):
    """Sistem durum widget'i"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """UI oluştur"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Başlık
        title = QLabel("🔌 SİSTEM DURUMU")
        title.setStyleSheet(f"""
            color: {styles.COLOR_ACCENT};
            font-size: 14px;
            font-weight: bold;
        """)
        layout.addWidget(title)
        
        # Durum göstergeleri
        self.camera_indicator = StatusIndicator("Kamera")
        layout.addWidget(self.camera_indicator)
        
        self.esp32_indicator = StatusIndicator("ESP32")
        layout.addWidget(self.esp32_indicator)
        
        self.ai_indicator = StatusIndicator("AI Model")
        layout.addWidget(self.ai_indicator)
        
        self.gps_indicator = StatusIndicator("GPS")
        layout.addWidget(self.gps_indicator)
        
        # Sistem bilgileri
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        self.uptime_label = QLabel("Uptime: 00:00:00")
        self.uptime_label.setStyleSheet(f"color: {styles.COLOR_TEXT}; font-size: 10px;")
        info_layout.addWidget(self.uptime_label)
        
        self.temp_label = QLabel("Sıcaklık: -- °C")
        self.temp_label.setStyleSheet(f"color: {styles.COLOR_TEXT}; font-size: 10px;")
        info_layout.addWidget(self.temp_label)
        
        self.battery_label = QLabel("Batarya: --%")
        self.battery_label.setStyleSheet(f"color: {styles.COLOR_TEXT}; font-size: 10px;")
        info_layout.addWidget(self.battery_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def update_camera_status(self, connected):
        """Kamera durumunu güncelle"""
        self.camera_indicator.set_status(connected)
    
    def update_esp32_status(self, connected):
        """ESP32 durumunu güncelle"""
        self.esp32_indicator.set_status(connected)
    
    def update_ai_status(self, loaded):
        """AI model durumunu güncelle"""
        self.ai_indicator.set_status(loaded)
    
    def update_gps_status(self, connected):
        """GPS durumunu güncelle"""
        self.gps_indicator.set_status(connected)
    
    def update_system_info(self, uptime, temp, battery):
        """Sistem bilgilerini güncelle"""
        self.uptime_label.setText(f"Uptime: {uptime}")
        self.temp_label.setText(f"Sıcaklık: {temp} °C")
        self.battery_label.setText(f"Batarya: {battery}%")