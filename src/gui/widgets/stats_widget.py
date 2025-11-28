import psutil
import time
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QFrame
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QPen
from gui import styles


class FPSGraph(QWidget):
    """FPS grafiği widget'i"""
    
    def __init__(self, width=300, height=100):
        super().__init__()
        self.setFixedSize(width, height)
        self.fps_history = [0] * 60  # Son 60 FPS değeri
        self.max_fps = 60
        
    def update_fps(self, fps):
        """FPS değerini güncelle"""
        self.fps_history.pop(0)
        self.fps_history.append(fps)
        self.update()
    
    def paintEvent(self, event):
        """Grafiği çiz"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Arka plan
        painter.fillRect(self.rect(), QColor(styles.COLOR_SECONDARY))
        
        # Kenarlık
        painter.setPen(QPen(QColor(styles.COLOR_BORDER), 2))
        painter.drawRect(1, 1, self.width()-2, self.height()-2)
        
        # Grid çizgileri
        painter.setPen(QPen(QColor(styles.COLOR_BORDER), 1))
        for i in range(0, self.height(), 20):
            painter.drawLine(0, i, self.width(), i)
        
        # FPS eğrisi
        if len(self.fps_history) > 1:
            painter.setPen(QPen(QColor(styles.COLOR_ACCENT), 2))
            
            step = self.width() / len(self.fps_history)
            for i in range(len(self.fps_history) - 1):
                x1 = i * step
                y1 = self.height() - (self.fps_history[i] / self.max_fps * self.height())
                x2 = (i + 1) * step
                y2 = self.height() - (self.fps_history[i + 1] / self.max_fps * self.height())
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        # FPS değeri
        if self.fps_history[-1] > 0:
            painter.setPen(QColor(styles.COLOR_TEXT))
            painter.drawText(10, 20, f"{int(self.fps_history[-1])} FPS")


class StatsWidget(QWidget):
    """İstatistik paneli widget'i"""
    
    def __init__(self):
        super().__init__()
        self.start_time = None
        self.fire_count = 0
        self.last_fire_time = time.time()
        self.fire_rate = 0
        
        self.init_ui()
        
        # Güncelleme timer'ı
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.start(1000)  # Her 1 saniye
    
    def init_ui(self):
        """UI oluştur"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Başlık
        title = QLabel("📊 İSTATİSTİKLER")
        title.setStyleSheet(f"""
            color: {styles.COLOR_ACCENT};
            font-size: 14px;
            font-weight: bold;
        """)
        layout.addWidget(title)
        
        # FPS Grafiği
        fps_label = QLabel("📈 FPS Grafiği")
        fps_label.setStyleSheet(f"color: {styles.COLOR_TEXT}; font-size: 12px;")
        layout.addWidget(fps_label)
        
        self.fps_graph = FPSGraph()
        layout.addWidget(self.fps_graph)
        
        # CPU Kullanımı
        cpu_label = QLabel("💻 CPU Kullanımı")
        cpu_label.setStyleSheet(f"color: {styles.COLOR_TEXT}; font-size: 12px;")
        layout.addWidget(cpu_label)
        
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setMaximum(100)
        self.cpu_bar.setStyleSheet(self.get_progressbar_style())
        layout.addWidget(self.cpu_bar)
        
        self.cpu_value_label = QLabel("0%")
        self.cpu_value_label.setStyleSheet(f"color: {styles.COLOR_TEXT}; font-size: 11px;")
        layout.addWidget(self.cpu_value_label)
        
        # RAM Kullanımı
        ram_label = QLabel("🧠 RAM Kullanımı")
        ram_label.setStyleSheet(f"color: {styles.COLOR_TEXT}; font-size: 12px;")
        layout.addWidget(ram_label)
        
        self.ram_bar = QProgressBar()
        self.ram_bar.setMaximum(100)
        self.ram_bar.setStyleSheet(self.get_progressbar_style())
        layout.addWidget(self.ram_bar)
        
        self.ram_value_label = QLabel("0 MB / 0 MB")
        self.ram_value_label.setStyleSheet(f"color: {styles.COLOR_TEXT}; font-size: 11px;")
        layout.addWidget(self.ram_value_label)
        
        # Çalışma Süresi
        runtime_label = QLabel("⏱ Çalışma Süresi")
        runtime_label.setStyleSheet(f"color: {styles.COLOR_TEXT}; font-size: 12px;")
        layout.addWidget(runtime_label)
        
        self.runtime_value = QLabel("00:00:00")
        self.runtime_value.setStyleSheet(f"""
            color: {styles.COLOR_ACCENT};
            font-size: 18px;
            font-weight: bold;
        """)
        layout.addWidget(self.runtime_value)
        
        # Ateş Hızı
        fire_rate_label = QLabel("🔥 Ateş Hızı")
        fire_rate_label.setStyleSheet(f"color: {styles.COLOR_TEXT}; font-size: 12px;")
        layout.addWidget(fire_rate_label)
        
        self.fire_rate_value = QLabel("0.0 atış/sn")
        self.fire_rate_value.setStyleSheet(f"""
            color: {styles.COLOR_DANGER};
            font-size: 16px;
            font-weight: bold;
        """)
        layout.addWidget(self.fire_rate_value)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def get_progressbar_style(self):
        """ProgressBar stili"""
        return f"""
        QProgressBar {{
            border: 2px solid {styles.COLOR_BORDER};
            border-radius: 5px;
            text-align: center;
            background-color: {styles.COLOR_SECONDARY};
            color: {styles.COLOR_TEXT};
            font-weight: bold;
        }}
        QProgressBar::chunk {{
            background-color: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {styles.COLOR_SUCCESS},
                stop:0.5 {styles.COLOR_ACCENT},
                stop:1 {styles.COLOR_INFO}
            );
            border-radius: 3px;
        }}
        """
    
    def start_tracking(self):
        """İzlemeyi başlat"""
        self.start_time = datetime.now()
    
    def update_fps(self, fps):
        """FPS grafiğini güncelle"""
        self.fps_graph.update_fps(fps)
    
    def add_fire(self):
        """Ateş sayacını artır"""
        self.fire_count += 1
        current_time = time.time()
        time_diff = current_time - self.last_fire_time
        if time_diff > 0:
            self.fire_rate = 1.0 / time_diff
        self.last_fire_time = current_time
    
    def update_stats(self):
        """İstatistikleri güncelle"""
        # CPU kullanımı
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self.cpu_bar.setValue(int(cpu_percent))
        
        # Renk değiştir
        if cpu_percent > 80:
            color = styles.COLOR_DANGER
        elif cpu_percent > 50:
            color = styles.COLOR_WARNING
        else:
            color = styles.COLOR_SUCCESS
        
        self.cpu_value_label.setText(f"{cpu_percent:.1f}%")
        self.cpu_value_label.setStyleSheet(f"color: {color}; font-size: 11px;")
        
        # RAM kullanımı
        ram = psutil.virtual_memory()
        ram_percent = ram.percent
        ram_used_mb = ram.used / (1024 * 1024)
        ram_total_mb = ram.total / (1024 * 1024)
        
        self.ram_bar.setValue(int(ram_percent))
        self.ram_value_label.setText(f"{ram_used_mb:.0f} MB / {ram_total_mb:.0f} MB")
        
        # Çalışma süresi
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            hours = int(elapsed.total_seconds() // 3600)
            minutes = int((elapsed.total_seconds() % 3600) // 60)
            seconds = int(elapsed.total_seconds() % 60)
            self.runtime_value.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Ateş hızı (son 5 saniyede sıfırsa 0 göster)
        if time.time() - self.last_fire_time > 5:
            self.fire_rate = 0
        
        self.fire_rate_value.setText(f"{self.fire_rate:.1f} atış/sn")