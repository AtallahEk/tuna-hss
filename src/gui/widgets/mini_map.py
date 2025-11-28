from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont
from gui import styles
import math


class MiniMapWidget(QWidget):
    """Mini harita widget'i - Taktik görünüm"""
    
    def __init__(self, width=250, height=250):
        super().__init__()
        self.setFixedSize(width, height)
        
        # Sistem konumu (merkez)
        self.system_x = width // 2
        self.system_y = height // 2
        
        # Hedefler
        self.targets = []  # [(x, y, type, distance), ...]
        
        # Grid boyutu (metre)
        self.grid_size = 50  # 50 metre
        self.scale = 2  # 1 piksel = 2 metre
        
    def add_target(self, angle, distance, target_type="enemy"):
        """Hedef ekle"""
        # Açıyı radyana çevir (0° = yukarı)
        angle_rad = math.radians(angle - 90)
        
        # Konum hesapla
        scaled_distance = distance / self.scale
        x = self.system_x + scaled_distance * math.cos(angle_rad)
        y = self.system_y + scaled_distance * math.sin(angle_rad)
        
        self.targets.append((int(x), int(y), target_type, distance))
        self.update()
    
    def clear_targets(self):
        """Hedefleri temizle"""
        self.targets = []
        self.update()
    
    def paintEvent(self, event):
        """Haritayı çiz"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Arka plan
        painter.fillRect(self.rect(), QColor(styles.COLOR_SECONDARY))
        
        # Grid çizgileri
        painter.setPen(QPen(QColor(styles.COLOR_BORDER), 1))
        grid_spacing = self.grid_size // self.scale
        
        # Dikey çizgiler
        for x in range(0, self.width(), grid_spacing):
            painter.drawLine(x, 0, x, self.height())
        
        # Yatay çizgiler
        for y in range(0, self.height(), grid_spacing):
            painter.drawLine(0, y, self.width(), y)
        
        # Merkez çizgileri (kalın)
        painter.setPen(QPen(QColor(styles.COLOR_BORDER), 2))
        painter.drawLine(self.system_x, 0, self.system_x, self.height())
        painter.drawLine(0, self.system_y, self.width(), self.system_y)
        
        # Mesafe çemberleri
        painter.setPen(QPen(QColor(styles.COLOR_BORDER), 1, Qt.DashLine))
        for i in range(1, 4):
            radius = i * (self.grid_size // self.scale)
            painter.drawEllipse(self.system_x - radius, self.system_y - radius,
                              radius * 2, radius * 2)
            
            # Mesafe etiketi
            painter.setPen(QColor(styles.COLOR_TEXT))
            painter.setFont(QFont("Arial", 8))
            painter.drawText(self.system_x + 5, self.system_y - radius + 10,
                           f"{i * self.grid_size}m")
            painter.setPen(QPen(QColor(styles.COLOR_BORDER), 1, Qt.DashLine))
        
        # Sistem konumu (merkez - mavi)
        painter.setPen(QPen(QColor(styles.COLOR_INFO), 2))
        painter.setBrush(QBrush(QColor(styles.COLOR_INFO)))
        painter.drawEllipse(self.system_x - 6, self.system_y - 6, 12, 12)
        
        # Yön göstergesi (üst = kuzey)
        painter.drawLine(self.system_x, self.system_y - 6, 
                        self.system_x, self.system_y - 15)
        
        # Hedefler
        for x, y, target_type, distance in self.targets:
            if target_type == "enemy":
                color = QColor(styles.COLOR_DANGER)
                symbol = "X"
            else:
                color = QColor(styles.COLOR_SUCCESS)
                symbol = "F"
            
            # Hedef noktası
            painter.setPen(QPen(color, 2))
            painter.setBrush(QBrush(color))
            painter.drawEllipse(x - 5, y - 5, 10, 10)
            
            # Hedef çizgisi
            painter.drawLine(self.system_x, self.system_y, x, y)
            
            # Hedef sembolü
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 8, QFont.Bold))
            painter.drawText(x - 4, y + 4, symbol)
            
            # Mesafe
            painter.setPen(color)
            painter.setFont(QFont("Arial", 7))
            painter.drawText(x + 8, y + 4, f"{distance:.1f}m")
        
        # Kenarlık
        painter.setPen(QPen(QColor(styles.COLOR_BORDER), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(1, 1, self.width()-2, self.height()-2)
        
        # Başlık
        painter.fillRect(0, 0, self.width(), 25, QColor(styles.COLOR_SECONDARY))
        painter.setPen(QColor(styles.COLOR_ACCENT))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(10, 17, "🗺 TAKTİK HARİTA")
        
        # Kuzey işareti
        painter.setPen(QColor(styles.COLOR_TEXT))
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(self.width() - 25, 40, "N")
        painter.drawLine(self.width() - 20, 25, self.width() - 20, 35)