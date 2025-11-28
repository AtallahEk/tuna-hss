from PyQt5.QtWidgets import QSplashScreen, QProgressBar, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
from gui import styles


class SplashScreen(QSplashScreen):
    """Profesyonel başlangıç ekranı"""
    
    def __init__(self):
        # Boş pixmap oluştur
        pixmap = QPixmap(600, 400)
        pixmap.fill(QColor(styles.COLOR_PRIMARY))
        super().__init__(pixmap)
        
        # Widget oluştur
        self.setup_ui()
        
        # Progress
        self.progress = 0
        self.status_text = "Başlatılıyor..."
        
    def setup_ui(self):
        """UI oluştur"""
        # Pencere özellikleri
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
    def drawContents(self, painter):
        """İçeriği çiz"""
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Arka plan
        painter.fillRect(self.rect(), QColor(styles.COLOR_PRIMARY))
        
        # Kenarlık
        painter.setPen(QColor(styles.COLOR_ACCENT))
        painter.drawRect(0, 0, self.width()-1, self.height()-1)
        painter.drawRect(5, 5, self.width()-11, self.height()-11)
        
        # Logo ve başlık
        painter.setPen(QColor(styles.COLOR_ACCENT))
        font = QFont("Arial", 48, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter | Qt.AlignTop, 
                        "\n🎯 TUNA")
        
        # Alt başlık
        painter.setPen(QColor(styles.COLOR_TEXT))
        font = QFont("Arial", 16)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, 
                        "Hava Savunma Sistemi")
        
        # Versiyon
        font = QFont("Arial", 10)
        painter.setFont(font)
        painter.drawText(20, self.height() - 60, "v1.0.0 BETA")
        
        # Progress bar
        bar_width = self.width() - 100
        bar_height = 20
        bar_x = 50
        bar_y = self.height() - 80
        
        # Progress arka plan
        painter.setPen(QColor(styles.COLOR_BORDER))
        painter.setBrush(QColor(styles.COLOR_SECONDARY))
        painter.drawRoundedRect(bar_x, bar_y, bar_width, bar_height, 10, 10)
        
        # Progress
        if self.progress > 0:
            progress_width = int((bar_width - 4) * (self.progress / 100))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(styles.COLOR_ACCENT))
            painter.drawRoundedRect(bar_x + 2, bar_y + 2, 
                                   progress_width, bar_height - 4, 8, 8)
        
        # Progress text
        painter.setPen(QColor(styles.COLOR_TEXT))
        font = QFont("Arial", 9)
        painter.setFont(font)
        painter.drawText(bar_x, bar_y + bar_height + 15, self.status_text)
        
        # Copyright
        painter.drawText(self.width() - 150, self.height() - 15, 
                        "© 2025 TUNA Team")
    
    def set_progress(self, value, status="Yükleniyor..."):
        """Progress güncelle"""
        self.progress = value
        self.status_text = status
        self.repaint()
    
    def finish_loading(self, main_window):
        """Yükleme tamamlandı"""
        self.finish(main_window)