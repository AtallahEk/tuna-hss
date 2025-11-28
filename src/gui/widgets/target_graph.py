from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from gui import styles
import math


class TargetDistanceGraph(QWidget):
    """Hedef mesafe grafiği - Radar görünümü"""
    
    def __init__(self, width=240, height=240):
        super().__init__()
        self.setFixedSize(width, height)
        self.target_distance = 0  # metre
        self.max_distance = 10  # maksimum 10 metre
        self.target_angle = 0  # derece
        self.target_detected = False
        
    def update_target(self, distance, angle, detected=True):
        """Hedef bilgilerini güncelle"""
        self.target_distance = distance
        self.target_angle = angle
        self.target_detected = detected
        self.update()
    
    def paintEvent(self, event):
        """Radar grafiğini çiz"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Arka plan
        painter.fillRect(self.rect(), QColor(styles.COLOR_SECONDARY))
        
        # Merkez ve yarıçap
        center_x = self.width() // 2
        center_y = self.height() // 2
        max_radius = min(center_x, center_y) - 20
        
        # Grid daireleri (2m, 4m, 6m, 8m, 10m)
        painter.setPen(QPen(QColor(styles.COLOR_BORDER), 1))
        for i in range(1, 6):
            radius = (i / 5) * max_radius
            painter.drawEllipse(int(center_x - radius), int(center_y - radius), 
                              int(radius * 2), int(radius * 2))
        
        # Merkez çizgiler (0°, 90°, 180°, 270°)
        painter.setPen(QPen(QColor(styles.COLOR_BORDER), 1))
        painter.drawLine(center_x, center_y - max_radius, center_x, center_y + max_radius)  # Dikey
        painter.drawLine(center_x - max_radius, center_y, center_x + max_radius, center_y)  # Yatay
        
        # Mesafe etiketleri
        painter.setPen(QColor(styles.COLOR_TEXT))
        painter.setFont(painter.font())
        for i in range(1, 6):
            distance_m = i * 2
            radius = (i / 5) * max_radius
            painter.drawText(center_x + 5, center_y - int(radius) - 5, f"{distance_m}m")
        
        # Hedef noktası
        if self.target_detected and self.target_distance > 0:
            # Mesafe oranı
            distance_ratio = min(self.target_distance / self.max_distance, 1.0)
            target_radius = distance_ratio * max_radius
            
            # Açı hesaplama (0° = yukarı, saat yönü)
            angle_rad = math.radians(self.target_angle - 90)
            target_x = center_x + target_radius * math.cos(angle_rad)
            target_y = center_y + target_radius * math.sin(angle_rad)
            
            # Hedef noktası (kırmızı)
            painter.setBrush(QBrush(QColor(styles.COLOR_DANGER)))
            painter.setPen(QPen(QColor(styles.COLOR_DANGER), 2))
            painter.drawEllipse(int(target_x - 6), int(target_y - 6), 12, 12)
            
            # Merkez'den hedefe çizgi
            painter.setPen(QPen(QColor(styles.COLOR_DANGER), 2))
            painter.drawLine(int(center_x), int(center_y), int(target_x), int(target_y))
            
            # Mesafe göster
            painter.drawText(int(target_x + 10), int(target_y - 10), 
                           f"{self.target_distance:.1f}m")
        
        # Kenarlık
        painter.setPen(QPen(QColor(styles.COLOR_BORDER), 2))
        painter.drawRect(1, 1, self.width()-2, self.height()-2)


class TurretAngleGraph(QWidget):
    """Namlu açısı grafiği - Yarım daire göstergesi"""
    
    def __init__(self, width=240, height=140):
        super().__init__()
        self.setFixedSize(width, height)
        self.current_pan = 180  # derece
        self.current_tilt = 30  # derece
        self.target_pan = None
        self.target_tilt = None
        
    def update_angles(self, pan, tilt, target_pan=None, target_tilt=None):
        """Açıları güncelle"""
        self.current_pan = pan
        self.current_tilt = tilt
        self.target_pan = target_pan
        self.target_tilt = target_tilt
        self.update()
    
    def paintEvent(self, event):
        """Açı grafiğini çiz"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Arka plan
        painter.fillRect(self.rect(), QColor(styles.COLOR_SECONDARY))
        
        # Merkez
        center_x = self.width() // 2
        center_y = self.height() - 20
        radius = self.width() // 2 - 30
        
        # Yarım daire (0-360° için)
        painter.setPen(QPen(QColor(styles.COLOR_BORDER), 2))
        painter.drawArc(int(center_x - radius), int(center_y - radius), 
                       int(radius * 2), int(radius * 2), 0, 180 * 16)
        
        # Derece işaretleri (0°, 90°, 180°, 270°, 360°)
        painter.setFont(painter.font())
        angles = [0, 90, 180, 270, 360]
        for angle in angles:
            angle_rad = math.radians(180 - (angle / 2))
            mark_x = center_x + radius * math.cos(angle_rad)
            mark_y = center_y - radius * math.sin(angle_rad)
            
            # İşaret çizgisi
            mark_inner_x = center_x + (radius - 10) * math.cos(angle_rad)
            mark_inner_y = center_y - (radius - 10) * math.sin(angle_rad)
            painter.drawLine(int(mark_inner_x), int(mark_inner_y), 
                           int(mark_x), int(mark_y))
            
            # Derece yazısı
            painter.setPen(QColor(styles.COLOR_TEXT))
            painter.drawText(int(mark_x - 15), int(mark_y + 15), f"{angle}°")
            painter.setPen(QPen(QColor(styles.COLOR_BORDER), 2))
        
        # Mevcut pan açısı (yeşil)
        pan_rad = math.radians(180 - (self.current_pan / 2))
        pan_x = center_x + radius * math.cos(pan_rad)
        pan_y = center_y - radius * math.sin(pan_rad)
        
        painter.setPen(QPen(QColor(styles.COLOR_ACCENT), 3))
        painter.drawLine(int(center_x), int(center_y), int(pan_x), int(pan_y))
        
        painter.setBrush(QBrush(QColor(styles.COLOR_ACCENT)))
        painter.drawEllipse(int(pan_x - 5), int(pan_y - 5), 10, 10)
        
        # Hedef pan açısı (kırmızı)
        if self.target_pan is not None:
            target_rad = math.radians(180 - (self.target_pan / 2))
            target_x = center_x + radius * math.cos(target_rad)
            target_y = center_y - radius * math.sin(target_rad)
            
            painter.setPen(QPen(QColor(styles.COLOR_DANGER), 2, Qt.DashLine))
            painter.drawLine(center_x, center_y, int(target_x), int(target_y))
            
            painter.setBrush(QBrush(QColor(styles.COLOR_DANGER)))
            painter.drawEllipse(int(target_x - 4), int(target_y - 4), 8, 8)
        
        # Tilt göstergesi (sağ alt köşe)
        painter.setPen(QColor(styles.COLOR_TEXT))
        painter.drawText(10, self.height() - 10, 
                        f"Tilt: {self.current_tilt}°")
        
        if self.target_tilt is not None:
            painter.setPen(QColor(styles.COLOR_DANGER))
            painter.drawText(10, self.height() - 25, 
                           f"Hedef Tilt: {self.target_tilt}°")
        
        # Kenarlık
        painter.setPen(QPen(QColor(styles.COLOR_BORDER), 2))
        painter.drawRect(1, 1, self.width()-2, self.height()-2)


class TargetGraphWidget(QWidget):
    """İki grafiği birleştiren widget"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """UI oluştur"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Başlık 1
        title1 = QLabel("🎯 Hedef Konumu")
        title1.setStyleSheet(f"""
            color: {styles.COLOR_ACCENT};
            font-size: 12px;
            font-weight: bold;
        """)
        layout.addWidget(title1)
        
        # Radar grafiği
        self.radar_graph = TargetDistanceGraph(240, 240)
        layout.addWidget(self.radar_graph)
        
        # Başlık 2
        title2 = QLabel("📐 Namlu Açısı")
        title2.setStyleSheet(f"""
            color: {styles.COLOR_INFO};
            font-size: 12px;
            font-weight: bold;
        """)
        layout.addWidget(title2)
        
        # Açı grafiği
        self.angle_graph = TurretAngleGraph(240, 140)
        layout.addWidget(self.angle_graph)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def update_target(self, distance, angle, detected=True):
        """Hedef bilgilerini güncelle"""
        self.radar_graph.update_target(distance, angle, detected)
    
    def update_angles(self, pan, tilt, target_pan=None, target_tilt=None):
        """Açıları güncelle"""
        self.angle_graph.update_angles(pan, tilt, target_pan, target_tilt)