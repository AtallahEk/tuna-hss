from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt
from gui import styles
import time


class PerformanceWidget(QWidget):
    """Performans metrikleri widget'i"""
    
    def __init__(self):
        super().__init__()
        self.total_shots = 0
        self.total_hits = 0
        self.last_shot_time = 0
        self.reaction_times = []  # Son 10 tepki süresi
        self.max_reaction_times = 10
        
        self.init_ui()
    
    def init_ui(self):
        """UI oluştur"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Başlık
        title = QLabel("📊 PERFORMANS")
        title.setStyleSheet(f"""
            color: {styles.COLOR_ACCENT};
            font-size: 14px;
            font-weight: bold;
        """)
        layout.addWidget(title)
        
        # İsabet Oranı
        hit_label = QLabel("🎯 İsabet Oranı")
        hit_label.setStyleSheet(f"color: {styles.COLOR_TEXT}; font-size: 12px;")
        layout.addWidget(hit_label)
        
        self.hit_rate_bar = QProgressBar()
        self.hit_rate_bar.setMaximum(100)
        self.hit_rate_bar.setValue(0)
        self.hit_rate_bar.setStyleSheet(self.get_progressbar_style())
        layout.addWidget(self.hit_rate_bar)
        
        self.hit_rate_label = QLabel("0 / 0 (0%)")
        self.hit_rate_label.setStyleSheet(f"""
            color: {styles.COLOR_ACCENT};
            font-size: 16px;
            font-weight: bold;
        """)
        layout.addWidget(self.hit_rate_label)
        
        # Ortalama Tepki Süresi
        reaction_label = QLabel("⚡ Ortalama Tepki")
        reaction_label.setStyleSheet(f"color: {styles.COLOR_TEXT}; font-size: 12px;")
        layout.addWidget(reaction_label)
        
        self.reaction_time_label = QLabel("-- ms")
        self.reaction_time_label.setStyleSheet(f"""
            color: {styles.COLOR_INFO};
            font-size: 18px;
            font-weight: bold;
        """)
        layout.addWidget(self.reaction_time_label)
        
        # Son Tepki Süresi
        last_reaction_label = QLabel("⏱ Son Tepki")
        last_reaction_label.setStyleSheet(f"color: {styles.COLOR_TEXT}; font-size: 12px;")
        layout.addWidget(last_reaction_label)
        
        self.last_reaction_label = QLabel("-- ms")
        self.last_reaction_label.setStyleSheet(f"""
            color: {styles.COLOR_WARNING};
            font-size: 16px;
            font-weight: bold;
        """)
        layout.addWidget(self.last_reaction_label)
        
        # Toplam Atış
        total_label = QLabel("💥 Toplam Atış")
        total_label.setStyleSheet(f"color: {styles.COLOR_TEXT}; font-size: 12px;")
        layout.addWidget(total_label)
        
        self.total_shots_label = QLabel("0")
        self.total_shots_label.setStyleSheet(f"""
            color: {styles.COLOR_DANGER};
            font-size: 18px;
            font-weight: bold;
        """)
        layout.addWidget(self.total_shots_label)
        
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
                stop:0 {styles.COLOR_DANGER},
                stop:0.5 {styles.COLOR_WARNING},
                stop:1 {styles.COLOR_SUCCESS}
            );
            border-radius: 3px;
        }}
        """
    
    def record_shot(self, hit=False, target_detected_time=None):
        """Atış kaydı ekle"""
        self.total_shots += 1
        if hit:
            self.total_hits += 1
        
        # Tepki süresi hesapla
        if target_detected_time and self.last_shot_time > 0:
            reaction_time = int((time.time() - target_detected_time) * 1000)  # ms
            self.reaction_times.append(reaction_time)
            
            # Son 10 tepki süresini tut
            if len(self.reaction_times) > self.max_reaction_times:
                self.reaction_times.pop(0)
            
            # Son tepki süresini göster
            self.last_reaction_label.setText(f"{reaction_time} ms")
        
        self.last_shot_time = time.time()
        self.update_display()
    
    def update_display(self):
        """Ekranı güncelle"""
        # İsabet oranı
        if self.total_shots > 0:
            hit_rate = (self.total_hits / self.total_shots) * 100
            self.hit_rate_bar.setValue(int(hit_rate))
            self.hit_rate_label.setText(f"{self.total_hits} / {self.total_shots} ({hit_rate:.1f}%)")
        else:
            self.hit_rate_bar.setValue(0)
            self.hit_rate_label.setText("0 / 0 (0%)")
        
        # Ortalama tepki süresi
        if self.reaction_times:
            avg_reaction = sum(self.reaction_times) / len(self.reaction_times)
            self.reaction_time_label.setText(f"{int(avg_reaction)} ms")
        
        # Toplam atış
        self.total_shots_label.setText(str(self.total_shots))
    
    def reset(self):
        """Metrikleri sıfırla"""
        self.total_shots = 0
        self.total_hits = 0
        self.reaction_times = []
        self.update_display()
        self.last_reaction_label.setText("-- ms")
        self.reaction_time_label.setText("-- ms")