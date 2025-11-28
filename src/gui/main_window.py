from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QSlider, QTextEdit, QFileDialog,
                             QDialog, QSpinBox, QMessageBox, QApplication, QTabWidget)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from datetime import datetime
import os
import time

from gui.widgets.camera_widget import CameraWidget
from gui.widgets.screen_recorder import ScreenRecorderThread
from gui.widgets.stats_widget import StatsWidget
from gui.widgets.target_graph import TargetGraphWidget
from gui.widgets.performance_widget import PerformanceWidget
from gui.widgets.system_status import SystemStatusWidget
from gui.widgets.mini_map import MiniMapWidget
from gui import styles
from utils.logger import TunaLogger
from utils.sound_manager import SoundManager
from utils.theme_manager import ThemeManager
from utils.replay_manager import ReplayManager
from utils.voice_commands import VoiceCommandManager
from utils.notification_manager import NotificationManager


class NoFireZoneDialog(QDialog):
    """Yasak alan belirleme dialogu"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🚫 ATEŞE YASAK ALAN")
        self.setModal(True)
        self.setFixedSize(400, 200)
        self.setStyleSheet(styles.DIALOG_STYLE)
        
        layout = QVBoxLayout()
        
        # Başlangıç açısı
        start_layout = QHBoxLayout()
        start_label = QLabel("Başlangıç Açısı (°):")
        self.start_spin = QSpinBox()
        self.start_spin.setRange(0, 360)
        self.start_spin.setValue(0)
        self.start_spin.setStyleSheet(styles.SPINBOX_STYLE)
        start_layout.addWidget(start_label)
        start_layout.addWidget(self.start_spin)
        
        # Bitiş açısı
        end_layout = QHBoxLayout()
        end_label = QLabel("Bitiş Açısı (°):")
        self.end_spin = QSpinBox()
        self.end_spin.setRange(0, 360)
        self.end_spin.setValue(30)
        self.end_spin.setStyleSheet(styles.SPINBOX_STYLE)
        end_layout.addWidget(end_label)
        end_layout.addWidget(self.end_spin)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("✓ UYGULA VE KAPAT")
        self.apply_btn.setStyleSheet(styles.BUTTON_SUCCESS_STYLE)
        self.apply_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("✗ İPTAL")
        self.cancel_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(start_layout)
        layout.addLayout(end_layout)
        layout.addSpacing(20)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def get_zone(self):
        """Seçilen yasak alanı döndür"""
        return self.start_spin.value(), self.end_spin.value()


class MainWindow(QMainWindow):
    """Ana uygulama penceresi"""
    
    def __init__(self):
        super().__init__()
        
        # Logger
        self.logger = TunaLogger()
        self.logger.info("TUNA HSS Başlatılıyor...")
        
        # Ses yöneticisi
        self.sound = SoundManager(enabled=True)
        
        # Tema yöneticisi
        self.theme_manager = ThemeManager()
        
        # Replay yöneticisi
        self.replay_manager = ReplayManager()
        self.replay_mode = False
        self.replay_start_time = 0
        
        # Ses komutları
        self.voice_manager = VoiceCommandManager()
        self.voice_manager.command_detected.connect(self.handle_voice_command)
        self.voice_manager.start_listening()  # Otomatik başlat
        self.logger.info("🎤 Ses komutları aktif (F/S/R/M/A/Y/ESC)")
        
        # Bildirim sistemi (init_ui'den sonra başlatılacak)
        self.notification_manager = None
        
        # Durum değişkenleri
        self.system_running = False
        self.autonomous_mode = False
        self.semi_auto_mode = False  # Yarı otonom mod
        self.angajman_mode = False  # Angajman mod (QR + Balon)
        self.video_recording = False
        self.screen_recording = False
        self.no_fire_zone = None
        
        # Pan/Tilt değerleri
        self.current_pan = 180
        self.current_tilt = 30
        
        # Angajman mod verileri
        self.qr_zone = None  # "A" veya "B"
        self.target_balloons = []  # [(renk, şekil), ...]
        self.safe_zone_angle = (150, 210)  # Orta güvenli bölge (örnek: 150-210°)
        
        # İmha sayacı
        self.kill_count = 0
        
        # Ekran kaydı thread'i
        self.screen_recorder = ScreenRecorderThread()
        self.screen_recorder.start()
        
        self.init_ui()
        
        # Log timer
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.update_logs)
        self.log_timer.start(1000)  # Her 1 saniyede bir güncelle
        
        # Grafik güncelleme timer
        self.graph_timer = QTimer()
        self.graph_timer.timeout.connect(self.update_graphs)
        self.graph_timer.start(100)  # Her 100ms'de bir güncelle
        
        # Bildirim sistemini başlat
        self.notification_manager = NotificationManager(self)
        
        # Hoş geldin mesajı
        QTimer.singleShot(500, lambda: self.notification_manager.show_notification(
            "TUNA HSS Başarıyla Yüklendi!", "success", 2000
        ))
        
    def init_ui(self):
        """UI'yi oluştur"""
        self.setWindowTitle("🎯 TUNA - Hava Savunma Sistemi")
        
        # Ekran boyutuna göre pencere ayarla
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()
        
        # Ekran boyutunun %95'i
        window_width = int(screen_width * 0.95)
        window_height = int(screen_height * 0.95)
        
        self.setGeometry(
            int((screen_width - window_width) / 2),
            int((screen_height - window_height) / 2),
            window_width,
            window_height
        )
        
        self.setStyleSheet(styles.MAIN_WINDOW_STYLE)
        
        # Merkezi widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 1. Üst Bar
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)
        
        # 2. Orta kısım - BASIT VE TEMİZ TASARIM
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(10)
        
        # ===== SOL: KAMERA (Çok Büyük) =====
        screen = QApplication.primaryScreen().geometry()
        camera_width = int(screen.width() * 0.78)
        camera_height = int(screen.height() * 0.78)
        
        self.camera_widget = CameraWidget(camera_width, camera_height)
        middle_layout.addWidget(self.camera_widget, 5)
        
        # ===== SAĞ: SEKMELER (Kompakt) =====
        self.tab_widget = QTabWidget()
        self.tab_widget.setFixedWidth(300)
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 2px solid {styles.COLOR_BORDER};
                background: {styles.COLOR_SECONDARY};
                border-radius: 5px;
            }}
            QTabBar::tab {{
                background: {styles.COLOR_SECONDARY};
                color: {styles.COLOR_TEXT};
                padding: 8px 12px;
                border: 1px solid {styles.COLOR_BORDER};
                font-size: 10px;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background: {styles.COLOR_ACCENT};
                color: {styles.COLOR_PRIMARY};
            }}
        """)
        
        # Tab 1: Radar + Hedef
        radar_widget = QWidget()
        radar_layout = QVBoxLayout()
        radar_layout.setContentsMargins(5, 5, 5, 5)
        
        self.target_graph = TargetGraphWidget()
        radar_layout.addWidget(self.target_graph)
        
        # Hedef bilgi kartı
        target_info = QWidget()
        target_info.setStyleSheet(f"""
            background: {styles.COLOR_SECONDARY};
            border: 1px solid {styles.COLOR_ACCENT};
            border-radius: 5px;
            padding: 8px;
        """)
        target_info_layout = QVBoxLayout()
        target_info_layout.setSpacing(3)
        
        self.target_type_label = QLabel("⚪ YOK")
        self.target_type_label.setStyleSheet(f"color: {styles.COLOR_TEXT}; font-size: 11px;")
        self.target_distance_label = QLabel("📏 --")
        self.target_distance_label.setStyleSheet(f"color: {styles.COLOR_TEXT}; font-size: 10px;")
        self.target_angle_label = QLabel("📐 --")
        self.target_angle_label.setStyleSheet(f"color: {styles.COLOR_TEXT}; font-size: 10px;")
        
        target_info_layout.addWidget(self.target_type_label)
        target_info_layout.addWidget(self.target_distance_label)
        target_info_layout.addWidget(self.target_angle_label)
        target_info.setLayout(target_info_layout)
        
        radar_layout.addWidget(target_info)
        radar_widget.setLayout(radar_layout)
        self.tab_widget.addTab(radar_widget, "📡 RADAR")
        
        # Tab 2: İstatistik + Performans
        stats_widget = QWidget()
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(5)
        stats_layout.setContentsMargins(5, 5, 5, 5)
        
        self.stats_widget = StatsWidget()
        self.performance_widget = PerformanceWidget()
        
        stats_layout.addWidget(self.stats_widget)
        stats_layout.addWidget(self.performance_widget)
        stats_widget.setLayout(stats_layout)
        self.tab_widget.addTab(stats_widget, "📊 RAPOR")
        
        # Tab 3: Sistem + Harita
        sys_map_widget = QWidget()
        sys_map_layout = QVBoxLayout()
        sys_map_layout.setSpacing(5)
        sys_map_layout.setContentsMargins(5, 5, 5, 5)
        
        self.system_status_widget = SystemStatusWidget()
        self.mini_map = MiniMapWidget(280, 280)
        
        sys_map_layout.addWidget(self.system_status_widget)
        sys_map_layout.addWidget(self.mini_map)
        sys_map_widget.setLayout(sys_map_layout)
        self.tab_widget.addTab(sys_map_widget, "🔌 SİSTEM")
        
        # Tab 4: Loglar
        log_widget = QWidget()
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(5, 5, 5, 5)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(styles.LOG_PANEL_STYLE)
        log_layout.addWidget(self.log_text)
        
        clear_btn = QPushButton("🗑 TEMİZLE")
        clear_btn.setStyleSheet(styles.BUTTON_STYLE)
        clear_btn.clicked.connect(self.clear_logs)
        log_layout.addWidget(clear_btn)
        
        log_widget.setLayout(log_layout)
        self.tab_widget.addTab(log_widget, "📋 LOG")
        
        middle_layout.addWidget(self.tab_widget, 1)
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(10)
        
        # ===== SOL: KAMERA BÖLGESI =====
        left_section = QVBoxLayout()
        left_section.setSpacing(5)
        
        # Kamera widget - daha büyük
        screen = QApplication.primaryScreen().geometry()
        camera_width = int(screen.width() * 0.75)
        camera_height = int(screen.height() * 0.75)
        
        self.camera_widget = CameraWidget(camera_width, camera_height)
        left_section.addWidget(self.camera_widget)
        
        # Alt bilgi satırı (Hedef + Mod + Konum)
        bottom_info = QHBoxLayout()
        bottom_info.setSpacing(10)
        
        # Hedef bilgi kartı
        target_card = self.create_info_card(
            "🎯 HEDEF",
            ["⚪ Hedef: YOK", "📏 Mesafe: --", "📐 Açı: --"]
        )
        self.target_labels = target_card[1]
        bottom_info.addWidget(target_card[0])
        
        # Mod bilgi kartı
        mode_card = self.create_info_card(
            "🎮 MOD",
            ["Manuel", "Pan: 180°", "Tilt: 30°"]
        )
        self.mode_labels = mode_card[1]
        bottom_info.addWidget(mode_card[0])
        
        # Sistem bilgi kartı
        system_card = self.create_info_card(
            "💥 SİSTEM",
            ["İmha: 0", "Atış: 0", "İsabet: 0%"]
        )
        self.system_labels = system_card[1]
        bottom_info.addWidget(system_card[0])
        
        left_section.addLayout(bottom_info)
        middle_layout.addLayout(left_section, 4)
        
        # ===== SAĞ: SEKMELER =====
        self.tab_widget = QTabWidget()
        self.tab_widget.setFixedWidth(320)
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 2px solid {styles.COLOR_ACCENT};
                background: {styles.COLOR_SECONDARY};
                border-radius: 5px;
            }}
            QTabBar::tab {{
                background: {styles.COLOR_SECONDARY};
                color: {styles.COLOR_TEXT};
                padding: 10px 15px;
                border: 1px solid {styles.COLOR_BORDER};
                font-size: 11px;
                font-weight: bold;
                min-width: 90px;
            }}
            QTabBar::tab:selected {{
                background: {styles.COLOR_ACCENT};
                color: {styles.COLOR_PRIMARY};
            }}
            QTabBar::tab:hover {{
                background: {styles.COLOR_BORDER};
            }}
        """)
        
        # Tab 1: Grafikler (Radar + Açı)
        self.target_graph = TargetGraphWidget()
        self.tab_widget.addTab(self.target_graph, "📡 RADAR")
        
        # Tab 2: İstatistikler + Performans
        stats_perf_widget = QWidget()
        stats_perf_layout = QVBoxLayout()
        stats_perf_layout.setSpacing(5)
        stats_perf_layout.setContentsMargins(5, 5, 5, 5)
        
        self.stats_widget = StatsWidget()
        stats_perf_layout.addWidget(self.stats_widget)
        
        self.performance_widget = PerformanceWidget()
        stats_perf_layout.addWidget(self.performance_widget)
        
        stats_perf_widget.setLayout(stats_perf_layout)
        self.tab_widget.addTab(stats_perf_widget, "📊 RAPOR")
        
        # Tab 3: Sistem Durumu
        self.system_status_widget = SystemStatusWidget()
        self.tab_widget.addTab(self.system_status_widget, "🔌 DURUM")
        
        # Tab 4: Taktik Harita
        self.mini_map = MiniMapWidget(300, 300)
        self.tab_widget.addTab(self.mini_map, "🗺 HARİTA")
        
        # Tab 5: Loglar
        log_widget = QWidget()
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(5, 5, 5, 5)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(styles.LOG_PANEL_STYLE)
        log_layout.addWidget(self.log_text)
        
        clear_btn = QPushButton("🗑 TEMİZLE")
        clear_btn.setStyleSheet(styles.BUTTON_STYLE)
        clear_btn.clicked.connect(self.clear_logs)
        log_layout.addWidget(clear_btn)
        
        log_widget.setLayout(log_layout)
        self.tab_widget.addTab(log_widget, "📋 LOG")
        
        middle_layout.addWidget(self.tab_widget, 1)
        
        main_layout.addLayout(middle_layout)
        
        # 3. Alt Kontrol Çubuğu
        control_bar = self.create_control_bar()
        main_layout.addWidget(control_bar)
        
        central_widget.setLayout(main_layout)
        
        self.logger.info("UI Oluşturuldu")
    
    def create_top_bar(self):
        """Üst bar oluştur"""
        top_bar = QWidget()
        top_bar.setFixedHeight(50)
        top_bar.setStyleSheet(styles.TOP_BAR_STYLE)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Logo
        logo_label = QLabel("🎯 TUNA")
        logo_label.setStyleSheet("font-size: 16px; color: #00ff88; font-weight: bold;")
        layout.addWidget(logo_label)
        
        layout.addStretch()
        
        # Kamera durumu
        self.camera_status = QLabel("📷 KAPALI")
        self.camera_status.setStyleSheet(f"color: {styles.COLOR_DANGER}; font-size: 11px;")
        layout.addWidget(self.camera_status)
        
        # ESP32 durumu
        self.esp_status = QLabel("🔌 YOK")
        self.esp_status.setStyleSheet(f"color: {styles.COLOR_WARNING}; font-size: 11px;")
        layout.addWidget(self.esp_status)
        
        # İmha sayacı
        self.kill_label = QLabel("💥 0")
        self.kill_label.setStyleSheet(f"color: {styles.COLOR_ACCENT}; font-size: 11px;")
        layout.addWidget(self.kill_label)
        
        # Saat
        self.time_label = QLabel()
        self.time_label.setStyleSheet(f"color: {styles.COLOR_TEXT}; font-size: 11px;")
        self.update_time()
        layout.addWidget(self.time_label)
        
        # Saat timer
        time_timer = QTimer(self)
        time_timer.timeout.connect(self.update_time)
        time_timer.start(1000)
        
        top_bar.setLayout(layout)
        return top_bar
    
    def create_info_bar(self):
        """Hedef bilgi çubuğu oluştur - artık kullanılmıyor"""
        pass
    
    def create_info_card(self, title, info_lines):
        """Bilgi kartı oluştur"""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {styles.COLOR_SECONDARY};
                border: 2px solid {styles.COLOR_ACCENT};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Başlık
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {styles.COLOR_ACCENT};
            font-size: 13px;
            font-weight: bold;
        """)
        layout.addWidget(title_label)
        
        # Bilgi satırları
        labels = []
        for line in info_lines:
            label = QLabel(line)
            label.setStyleSheet(f"""
                color: {styles.COLOR_TEXT};
                font-size: 11px;
            """)
            layout.addWidget(label)
            labels.append(label)
        
        card.setLayout(layout)
        return (card, labels)
    
    def create_control_bar(self):
        """Kontrol çubuğu - BASİT VE TEMİZ"""
        control_bar = QWidget()
        control_bar.setFixedHeight(80)
        control_bar.setStyleSheet(f"""
            QWidget {{
                background-color: {styles.COLOR_SECONDARY};
                border: 2px solid {styles.COLOR_ACCENT};
                border-radius: 5px;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(20)
        
        btn_style = """
        QPushButton {
            padding: 10px 15px;
            font-size: 11px;
            font-weight: bold;
            min-width: 100px;
            min-height: 40px;
        }
        """
        
        # === MOD SEÇME ===
        self.manual_btn = QPushButton("🎮 MANUEL")
        self.manual_btn.setCheckable(True)
        self.manual_btn.setChecked(True)
        self.manual_btn.setStyleSheet(styles.TOGGLE_BUTTON_ACTIVE_STYLE + btn_style)
        self.manual_btn.clicked.connect(self.toggle_manual_mode)
        layout.addWidget(self.manual_btn)
        
        self.semi_auto_btn = QPushButton("🎯 YARI OTO")
        self.semi_auto_btn.setCheckable(True)
        self.semi_auto_btn.setStyleSheet(styles.BUTTON_STYLE + btn_style)
        self.semi_auto_btn.clicked.connect(self.toggle_semi_auto_mode)
        layout.addWidget(self.semi_auto_btn)
        
        self.auto_btn = QPushButton("🤖 OTONOM")
        self.auto_btn.setCheckable(True)
        self.auto_btn.setStyleSheet(styles.BUTTON_STYLE + btn_style)
        self.auto_btn.clicked.connect(self.toggle_auto_mode)
        layout.addWidget(self.auto_btn)
        
        self.angajman_btn = QPushButton("🎲 ANGAJMAN")
        self.angajman_btn.setCheckable(True)
        self.angajman_btn.setStyleSheet(styles.BUTTON_STYLE + btn_style)
        self.angajman_btn.clicked.connect(self.toggle_angajman_mode)
        layout.addWidget(self.angajman_btn)
        
        layout.addSpacing(20)
        
        # === KONTROL ===
        ctrl_layout = QVBoxLayout()
        ctrl_layout.setSpacing(3)
        
        self.pan_label = QLabel(f"Pan: {self.current_pan}°")
        self.pan_label.setStyleSheet("font-size: 9px;")
        self.pan_slider = QSlider(Qt.Horizontal)
        self.pan_slider.setRange(0, 360)
        self.pan_slider.setValue(self.current_pan)
        self.pan_slider.setStyleSheet(styles.SLIDER_STYLE)
        self.pan_slider.setMaximumWidth(150)
        self.pan_slider.valueChanged.connect(self.update_pan_slider)
        
        ctrl_layout.addWidget(self.pan_label)
        ctrl_layout.addWidget(self.pan_slider)
        layout.addLayout(ctrl_layout)
        
        tilt_layout = QVBoxLayout()
        tilt_layout.setSpacing(3)
        
        self.tilt_label = QLabel(f"Tilt: {self.current_tilt}°")
        self.tilt_label.setStyleSheet("font-size: 9px;")
        self.tilt_slider = QSlider(Qt.Horizontal)
        self.tilt_slider.setRange(0, 60)
        self.tilt_slider.setValue(self.current_tilt)
        self.tilt_slider.setStyleSheet(styles.SLIDER_STYLE)
        self.tilt_slider.setMaximumWidth(150)
        self.tilt_slider.valueChanged.connect(self.update_tilt_slider)
        
        tilt_layout.addWidget(self.tilt_label)
        tilt_layout.addWidget(self.tilt_slider)
        layout.addLayout(tilt_layout)
        
        layout.addSpacing(20)
        
        # === AKSİYON ===
        self.system_btn = QPushButton("▶ BAŞLAT")
        self.system_btn.setCheckable(True)
        self.system_btn.setStyleSheet(styles.BUTTON_SUCCESS_STYLE + btn_style)
        self.system_btn.clicked.connect(self.toggle_system)
        layout.addWidget(self.system_btn)
        
        self.fire_btn = QPushButton("🔥 ATEŞ")
        self.fire_btn.setStyleSheet(styles.BUTTON_DANGER_STYLE + btn_style)
        self.fire_btn.clicked.connect(self.fire)
        layout.addWidget(self.fire_btn)
        
        self.emergency_btn = QPushButton("🛑 ACİL")
        self.emergency_btn.setStyleSheet(styles.BUTTON_DANGER_STYLE + btn_style)
        self.emergency_btn.clicked.connect(self.emergency_stop)
        layout.addWidget(self.emergency_btn)
        
        layout.addSpacing(20)
        
        # === SİSTEM ===
        self.nofire_btn = QPushButton("🚫 YASAK")
        self.nofire_btn.setStyleSheet(styles.BUTTON_STYLE + btn_style)
        self.nofire_btn.clicked.connect(self.set_no_fire_zone)
        layout.addWidget(self.nofire_btn)
        
        self.video_rec_btn = QPushButton("🎥 VİDEO")
        self.video_rec_btn.setCheckable(True)
        self.video_rec_btn.setStyleSheet(styles.BUTTON_STYLE + btn_style)
        self.video_rec_btn.clicked.connect(self.toggle_video_recording)
        layout.addWidget(self.video_rec_btn)
        
        self.sound_btn = QPushButton("🔊")
        self.sound_btn.setCheckable(True)
        self.sound_btn.setChecked(True)
        self.sound_btn.setStyleSheet(styles.TOGGLE_BUTTON_ACTIVE_STYLE + btn_style)
        self.sound_btn.setMaximumWidth(60)
        self.sound_btn.clicked.connect(self.toggle_sound)
        layout.addWidget(self.sound_btn)
        
        control_bar.setLayout(layout)
        return control_bar
        """Kontrol çubuğu oluştur - YENİDEN TASARIM"""
        control_bar = QWidget()
        control_bar.setFixedHeight(90)
        control_bar.setStyleSheet(f"""
            QWidget {{
                background-color: {styles.COLOR_SECONDARY};
                border: 2px solid {styles.COLOR_ACCENT};
                border-radius: 5px;
            }}
        """)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Buton stili
        button_style = """
        QPushButton {
            padding: 8px 12px;
            font-size: 11px;
            font-weight: bold;
            min-width: 90px;
            min-height: 35px;
        }
        """
        
        # ===== GRUP 1: MOD SEÇİMİ =====
        mode_group = QVBoxLayout()
        mode_label = QLabel("🎮 MOD")
        mode_label.setStyleSheet(f"color: {styles.COLOR_ACCENT}; font-size: 10px; font-weight: bold;")
        mode_group.addWidget(mode_label)
        
        mode_buttons = QHBoxLayout()
        mode_buttons.setSpacing(5)
        
        self.manual_btn = QPushButton("MANUEL")
        self.manual_btn.setCheckable(True)
        self.manual_btn.setChecked(True)
        self.manual_btn.setStyleSheet(styles.TOGGLE_BUTTON_ACTIVE_STYLE + button_style)
        self.manual_btn.clicked.connect(self.toggle_manual_mode)
        mode_buttons.addWidget(self.manual_btn)
        
        self.semi_auto_btn = QPushButton("YARI OTO")
        self.semi_auto_btn.setCheckable(True)
        self.semi_auto_btn.setStyleSheet(styles.BUTTON_STYLE + button_style)
        self.semi_auto_btn.clicked.connect(self.toggle_semi_auto_mode)
        mode_buttons.addWidget(self.semi_auto_btn)
        
        self.auto_btn = QPushButton("OTONOM")
        self.auto_btn.setCheckable(True)
        self.auto_btn.setStyleSheet(styles.BUTTON_STYLE + button_style)
        self.auto_btn.clicked.connect(self.toggle_auto_mode)
        mode_buttons.addWidget(self.auto_btn)
        
        mode_group.addLayout(mode_buttons)
        main_layout.addLayout(mode_group)
        
        # Ayırıcı çizgi
        separator1 = QLabel("|")
        separator1.setStyleSheet(f"color: {styles.COLOR_BORDER}; font-size: 30px;")
        main_layout.addWidget(separator1)
        
        # ===== GRUP 2: KONTROL (Slider'lar) =====
        control_group = QVBoxLayout()
        control_label = QLabel("🎛 KONTROL")
        control_label.setStyleSheet(f"color: {styles.COLOR_ACCENT}; font-size: 10px; font-weight: bold;")
        control_group.addWidget(control_label)
        
        sliders = QHBoxLayout()
        sliders.setSpacing(10)
        
        # Pan
        pan_layout = QVBoxLayout()
        pan_layout.setSpacing(2)
        self.pan_label = QLabel(f"Pan: {self.current_pan}°")
        self.pan_label.setStyleSheet("font-size: 9px;")
        self.pan_label.setAlignment(Qt.AlignCenter)
        self.pan_slider = QSlider(Qt.Horizontal)
        self.pan_slider.setRange(0, 360)
        self.pan_slider.setValue(self.current_pan)
        self.pan_slider.setStyleSheet(styles.SLIDER_STYLE)
        self.pan_slider.setMaximumWidth(120)
        self.pan_slider.valueChanged.connect(self.update_pan_slider)
        pan_layout.addWidget(self.pan_label)
        pan_layout.addWidget(self.pan_slider)
        sliders.addLayout(pan_layout)
        
        # Tilt
        tilt_layout = QVBoxLayout()
        tilt_layout.setSpacing(2)
        self.tilt_label = QLabel(f"Tilt: {self.current_tilt}°")
        self.tilt_label.setStyleSheet("font-size: 9px;")
        self.tilt_label.setAlignment(Qt.AlignCenter)
        self.tilt_slider = QSlider(Qt.Horizontal)
        self.tilt_slider.setRange(0, 60)
        self.tilt_slider.setValue(self.current_tilt)
        self.tilt_slider.setStyleSheet(styles.SLIDER_STYLE)
        self.tilt_slider.setMaximumWidth(120)
        self.tilt_slider.valueChanged.connect(self.update_tilt_slider)
        tilt_layout.addWidget(self.tilt_label)
        tilt_layout.addWidget(self.tilt_slider)
        sliders.addLayout(tilt_layout)
        
        control_group.addLayout(sliders)
        main_layout.addLayout(control_group)
        
        # Ayırıcı çizgi
        separator2 = QLabel("|")
        separator2.setStyleSheet(f"color: {styles.COLOR_BORDER}; font-size: 30px;")
        main_layout.addWidget(separator2)
        
        # ===== GRUP 3: AKSİYON =====
        action_group = QVBoxLayout()
        action_label = QLabel("⚡ AKSİYON")
        action_label.setStyleSheet(f"color: {styles.COLOR_ACCENT}; font-size: 10px; font-weight: bold;")
        action_group.addWidget(action_label)
        
        action_buttons = QHBoxLayout()
        action_buttons.setSpacing(5)
        
        self.system_btn = QPushButton("▶ BAŞLAT")
        self.system_btn.setCheckable(True)
        self.system_btn.setStyleSheet(styles.BUTTON_SUCCESS_STYLE + button_style)
        self.system_btn.clicked.connect(self.toggle_system)
        action_buttons.addWidget(self.system_btn)
        
        self.fire_btn = QPushButton("🔥 ATEŞ")
        self.fire_btn.setStyleSheet(styles.BUTTON_DANGER_STYLE + button_style)
        self.fire_btn.clicked.connect(self.fire)
        action_buttons.addWidget(self.fire_btn)
        
        self.emergency_btn = QPushButton("🛑 ACİL")
        self.emergency_btn.setStyleSheet(styles.BUTTON_DANGER_STYLE + button_style)
        self.emergency_btn.clicked.connect(self.emergency_stop)
        action_buttons.addWidget(self.emergency_btn)
        
        action_group.addLayout(action_buttons)
        main_layout.addLayout(action_group)
        
        # Ayırıcı çizgi
        separator3 = QLabel("|")
        separator3.setStyleSheet(f"color: {styles.COLOR_BORDER}; font-size: 30px;")
        main_layout.addWidget(separator3)
        
        # ===== GRUP 4: SİSTEM =====
        system_group = QVBoxLayout()
        system_label = QLabel("⚙ SİSTEM")
        system_label.setStyleSheet(f"color: {styles.COLOR_ACCENT}; font-size: 10px; font-weight: bold;")
        system_group.addWidget(system_label)
        
        system_buttons = QHBoxLayout()
        system_buttons.setSpacing(5)
        
        self.nofire_btn = QPushButton("🚫 YASAK")
        self.nofire_btn.setStyleSheet(styles.BUTTON_STYLE + button_style)
        self.nofire_btn.clicked.connect(self.set_no_fire_zone)
        system_buttons.addWidget(self.nofire_btn)
        
        self.video_rec_btn = QPushButton("🎥 VİDEO")
        self.video_rec_btn.setCheckable(True)
        self.video_rec_btn.setStyleSheet(styles.BUTTON_STYLE + button_style)
        self.video_rec_btn.clicked.connect(self.toggle_video_recording)
        system_buttons.addWidget(self.video_rec_btn)
        
        self.screen_rec_btn = QPushButton("📹 EKRAN")
        self.screen_rec_btn.setCheckable(True)
        self.screen_rec_btn.setStyleSheet(styles.BUTTON_STYLE + button_style)
        self.screen_rec_btn.clicked.connect(self.toggle_screen_recording)
        system_buttons.addWidget(self.screen_rec_btn)
        
        system_group.addLayout(system_buttons)
        main_layout.addLayout(system_group)
        
        # Ayırıcı çizgi
        separator4 = QLabel("|")
        separator4.setStyleSheet(f"color: {styles.COLOR_BORDER}; font-size: 30px;")
        main_layout.addWidget(separator4)
        
        # ===== GRUP 5: EKSTRA =====
        extra_group = QVBoxLayout()
        extra_label = QLabel("🔧 EKSTRA")
        extra_label.setStyleSheet(f"color: {styles.COLOR_ACCENT}; font-size: 10px; font-weight: bold;")
        extra_group.addWidget(extra_label)
        
        extra_buttons = QHBoxLayout()
        extra_buttons.setSpacing(5)
        
        self.log_save_btn = QPushButton("💾 LOG")
        self.log_save_btn.setStyleSheet(styles.BUTTON_STYLE + button_style)
        self.log_save_btn.clicked.connect(self.save_log)
        extra_buttons.addWidget(self.log_save_btn)
        
        self.sound_btn = QPushButton("🔊 SES")
        self.sound_btn.setCheckable(True)
        self.sound_btn.setChecked(True)
        self.sound_btn.setStyleSheet(styles.TOGGLE_BUTTON_ACTIVE_STYLE + button_style)
        self.sound_btn.clicked.connect(self.toggle_sound)
        extra_buttons.addWidget(self.sound_btn)
        
        self.theme_btn = QPushButton("🎨 TEMA")
        self.theme_btn.setStyleSheet(styles.BUTTON_STYLE + button_style)
        self.theme_btn.clicked.connect(self.cycle_theme)
        extra_buttons.addWidget(self.theme_btn)
        
        extra_group.addLayout(extra_buttons)
        main_layout.addLayout(extra_group)
        
        control_bar.setLayout(main_layout)
        return control_bar
        """Kontrol çubuğu oluştur"""
        control_bar = QWidget()
        control_bar.setFixedHeight(100)
        control_bar.setStyleSheet(styles.CONTROL_BAR_STYLE)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Kontrol satırı
        controls_layout = QHBoxLayout()
        
        # Mod butonları
        self.manual_btn = QPushButton("🎮 MANUEL")
        self.manual_btn.setCheckable(True)
        self.manual_btn.setChecked(True)
        self.manual_btn.setStyleSheet(styles.TOGGLE_BUTTON_ACTIVE_STYLE)
        self.manual_btn.clicked.connect(self.toggle_manual_mode)
        self.manual_btn.setMinimumWidth(90)
        controls_layout.addWidget(self.manual_btn)
        
        self.semi_auto_btn = QPushButton("🎯 YARI OTO")
        self.semi_auto_btn.setCheckable(True)
        self.semi_auto_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.semi_auto_btn.clicked.connect(self.toggle_semi_auto_mode)
        self.semi_auto_btn.setMinimumWidth(90)
        controls_layout.addWidget(self.semi_auto_btn)
        
        self.auto_btn = QPushButton("🤖 OTONOM")
        self.auto_btn.setCheckable(True)
        self.auto_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.auto_btn.clicked.connect(self.toggle_auto_mode)
        self.auto_btn.setMinimumWidth(90)
        controls_layout.addWidget(self.auto_btn)
        
        # Pan slider (kompakt)
        pan_layout = QVBoxLayout()
        pan_layout.setSpacing(2)
        pan_label = QLabel(f"Pan: {self.current_pan}°")
        pan_label.setAlignment(Qt.AlignCenter)
        pan_label.setStyleSheet("font-size: 10px;")
        self.pan_slider = QSlider(Qt.Horizontal)
        self.pan_slider.setRange(0, 360)
        self.pan_slider.setValue(self.current_pan)
        self.pan_slider.setStyleSheet(styles.SLIDER_STYLE)
        self.pan_slider.setMaximumWidth(150)
        self.pan_slider.valueChanged.connect(lambda v: self.update_pan(v, pan_label))
        pan_layout.addWidget(pan_label)
        pan_layout.addWidget(self.pan_slider)
        controls_layout.addLayout(pan_layout)
        
        # Tilt slider (kompakt)
        tilt_layout = QVBoxLayout()
        tilt_layout.setSpacing(2)
        tilt_label = QLabel(f"Tilt: {self.current_tilt}°")
        tilt_label.setAlignment(Qt.AlignCenter)
        tilt_label.setStyleSheet("font-size: 10px;")
        self.tilt_slider = QSlider(Qt.Horizontal)
        self.tilt_slider.setRange(0, 60)
        self.tilt_slider.setValue(self.current_tilt)
        self.tilt_slider.setStyleSheet(styles.SLIDER_STYLE)
        self.tilt_slider.setMaximumWidth(150)
        self.tilt_slider.valueChanged.connect(lambda v: self.update_tilt(v, tilt_label))
        tilt_layout.addWidget(tilt_label)
        tilt_layout.addWidget(self.tilt_slider)
        controls_layout.addLayout(tilt_layout)
        
        controls_layout.addSpacing(10)
        
        # Butonlar (kompakt ama yazılı)
        button_style_compact = """
        QPushButton {
            padding: 6px 10px;
            font-size: 10px;
            min-width: 80px;
        }
        """
        
        # Ateş butonu
        self.fire_btn = QPushButton("🔥 ATEŞ")
        self.fire_btn.setStyleSheet(styles.BUTTON_DANGER_STYLE + button_style_compact)
        self.fire_btn.clicked.connect(self.fire)
        controls_layout.addWidget(self.fire_btn)
        
        # Acil durdur
        self.emergency_btn = QPushButton("🛑 ACİL")
        self.emergency_btn.setStyleSheet(styles.BUTTON_DANGER_STYLE + button_style_compact)
        self.emergency_btn.clicked.connect(self.emergency_stop)
        controls_layout.addWidget(self.emergency_btn)
        
        # Sistem başlat/durdur
        self.system_btn = QPushButton("▶ BAŞLAT")
        self.system_btn.setCheckable(True)
        self.system_btn.setStyleSheet(styles.BUTTON_SUCCESS_STYLE + button_style_compact)
        self.system_btn.clicked.connect(self.toggle_system)
        controls_layout.addWidget(self.system_btn)
        
        # Yasak alan
        self.nofire_btn = QPushButton("🚫 YASAK")
        self.nofire_btn.setStyleSheet(styles.BUTTON_STYLE + button_style_compact)
        self.nofire_btn.clicked.connect(self.set_no_fire_zone)
        controls_layout.addWidget(self.nofire_btn)
        
        controls_layout.addSpacing(10)
        
        # Video kayıt
        self.video_rec_btn = QPushButton("🎥 VİDEO")
        self.video_rec_btn.setCheckable(True)
        self.video_rec_btn.setStyleSheet(styles.BUTTON_STYLE + button_style_compact)
        self.video_rec_btn.clicked.connect(self.toggle_video_recording)
        controls_layout.addWidget(self.video_rec_btn)
        
        # Ekran kayıt
        self.screen_rec_btn = QPushButton("📹 EKRAN")
        self.screen_rec_btn.setCheckable(True)
        self.screen_rec_btn.setStyleSheet(styles.BUTTON_STYLE + button_style_compact)
        self.screen_rec_btn.clicked.connect(self.toggle_screen_recording)
        controls_layout.addWidget(self.screen_rec_btn)
        
        controls_layout.addSpacing(10)
        
        # Log kaydet
        self.log_save_btn = QPushButton("💾 LOG")
        self.log_save_btn.setStyleSheet(styles.BUTTON_STYLE + button_style_compact)
        self.log_save_btn.clicked.connect(self.save_log)
        controls_layout.addWidget(self.log_save_btn)
        
        # Ses toggle
        self.sound_btn = QPushButton("🔊 SES")
        self.sound_btn.setCheckable(True)
        self.sound_btn.setChecked(True)
        self.sound_btn.setStyleSheet(styles.TOGGLE_BUTTON_ACTIVE_STYLE + button_style_compact)
        self.sound_btn.clicked.connect(self.toggle_sound)
        controls_layout.addWidget(self.sound_btn)
        
        # Tam ekran
        self.fullscreen_btn = QPushButton("⛶ TAM")
        self.fullscreen_btn.setStyleSheet(styles.BUTTON_STYLE + button_style_compact)
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        controls_layout.addWidget(self.fullscreen_btn)
        
        # Tema değiştir
        self.theme_btn = QPushButton("🎨 TEMA")
        self.theme_btn.setStyleSheet(styles.BUTTON_STYLE + button_style_compact)
        self.theme_btn.clicked.connect(self.cycle_theme)
        controls_layout.addWidget(self.theme_btn)
        
        controls_layout.addSpacing(10)
        
        # Replay kayıt
        self.replay_rec_btn = QPushButton("📹 GÖREV")
        self.replay_rec_btn.setCheckable(True)
        self.replay_rec_btn.setStyleSheet(styles.BUTTON_STYLE + button_style_compact)
        self.replay_rec_btn.clicked.connect(self.toggle_replay_recording)
        controls_layout.addWidget(self.replay_rec_btn)
        
        layout.addLayout(controls_layout)
        control_bar.setLayout(layout)
        return control_bar
    
    def create_log_panel(self):
        """Log paneli oluştur - artık kullanılmıyor, tab içinde"""
        pass
    
    def update_time(self):
        """Saati güncelle"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(f"🕐 {current_time}")
    
    def update_pan(self, value, label):
        """Pan değerini güncelle - ESKİ"""
        pass
    
    def update_tilt(self, value, label):
        """Tilt değerini güncelle - ESKİ"""
        pass
    
    def update_pan_slider(self, value):
        """Pan slider güncelle"""
        self.current_pan = value
        self.pan_label.setText(f"Pan: {value}°")
        self.target_graph.update_angles(self.current_pan, self.current_tilt)
        self.logger.debug(f"Pan: {value}°")
    
    def update_tilt_slider(self, value):
        """Tilt slider güncelle"""
        self.current_tilt = value
        self.tilt_label.setText(f"Tilt: {value}°")
        self.target_graph.update_angles(self.current_pan, self.current_tilt)
        self.logger.debug(f"Tilt: {value}°")
    
    def update_graphs(self):
        """Grafikleri güncelle"""
        # Simülasyon: Rastgele hedef (gerçek uygulamada YOLO'dan gelecek)
        import random
        if self.system_running and (self.semi_auto_mode or self.autonomous_mode):
            # Simüle edilmiş hedef
            target_distance = random.uniform(3, 8)
            target_angle = random.uniform(0, 360)
            target_pan = random.randint(90, 270)
            target_tilt = random.randint(20, 40)
            
            # Grafikleri güncelle
            self.target_graph.update_target(target_distance, target_angle, True)
            self.target_graph.update_angles(self.current_pan, self.current_tilt, 
                                          target_pan, target_tilt)
            
            # Mini map'e hedef ekle (her 2 saniyede bir)
            if random.random() < 0.05:  # %5 şans
                self.mini_map.clear_targets()
                target_type = "enemy" if random.random() > 0.3 else "friend"
                self.mini_map.add_target(target_angle, target_distance, target_type)
            
            # Hedef bilgilerini göster
            self.target_type_label.setText(f"🔴 DÜŞMAN")
            self.target_type_label.setStyleSheet(f"color: {styles.COLOR_DANGER}; font-size: 11px;")
            self.target_distance_label.setText(f"📏 {target_distance:.1f}m")
            self.target_angle_label.setText(f"📐 {target_angle:.0f}°")
        else:
            # Hedef yok
            self.target_graph.update_target(0, 0, False)
            self.target_graph.update_angles(self.current_pan, self.current_tilt)
            self.target_type_label.setText("⚪ YOK")
            self.target_type_label.setStyleSheet(f"color: {styles.COLOR_TEXT}; font-size: 11px;")
    
    def toggle_manual_mode(self):
        """Manuel moda geç"""
        if not self.manual_btn.isChecked():
            self.manual_btn.setChecked(True)
            return
        
        self.autonomous_mode = False
        self.semi_auto_mode = False
        self.angajman_mode = False
        self.auto_btn.setChecked(False)
        self.semi_auto_btn.setChecked(False)
        self.angajman_btn.setChecked(False)
        self.auto_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.semi_auto_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.angajman_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.manual_btn.setStyleSheet(styles.TOGGLE_BUTTON_ACTIVE_STYLE)
        
        # Slider ve ateş butonunu göster
        self.pan_slider.setEnabled(True)
        self.tilt_slider.setEnabled(True)
        self.fire_btn.setVisible(True)
        
        self.logger.info("🎮 MANUEL MOD Aktif")
    
    def toggle_semi_auto_mode(self):
        """Yarı otonom moda geç"""
        if not self.semi_auto_btn.isChecked():
            self.semi_auto_btn.setChecked(True)
            return
        
        self.autonomous_mode = False
        self.semi_auto_mode = True
        self.angajman_mode = False
        self.manual_btn.setChecked(False)
        self.auto_btn.setChecked(False)
        self.angajman_btn.setChecked(False)
        self.manual_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.auto_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.angajman_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.semi_auto_btn.setStyleSheet(styles.TOGGLE_BUTTON_ACTIVE_STYLE)
        
        # Slider'ları devre dışı bırak ama ateş butonunu göster
        self.pan_slider.setEnabled(False)
        self.tilt_slider.setEnabled(False)
        self.fire_btn.setVisible(True)
        
        self.logger.info("🎯 YARI OTONOM MOD Aktif - Otomatik takip, manuel ateş")
    
    def toggle_angajman_mode(self):
        """Angajman moda geç"""
        if not self.angajman_btn.isChecked():
            self.angajman_btn.setChecked(True)
            return
        
        self.angajman_mode = True
        self.autonomous_mode = False
        self.semi_auto_mode = False
        
        self.manual_btn.setChecked(False)
        self.semi_auto_btn.setChecked(False)
        self.auto_btn.setChecked(False)
        
        self.manual_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.semi_auto_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.auto_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.angajman_btn.setStyleSheet(styles.TOGGLE_BUTTON_ACTIVE_STYLE)
        
        # Slider ve ateş kontrolü
        self.pan_slider.setEnabled(False)
        self.tilt_slider.setEnabled(False)
        self.fire_btn.setVisible(False)
        
        self.logger.info("🎲 ANGAJMAN MOD Aktif")
        self.notification_manager.show_notification("Angajman Mod: QR okuma başladı", "info")
        
        # QR kod simülasyonu (gerçekte kamera ile QR okuyacak)
        QTimer.singleShot(2000, self.simulate_qr_read)
    
    def simulate_qr_read(self):
        """QR kod okuma simülasyonu"""
        import random
        
        # Rastgele A veya B
        self.qr_zone = random.choice(["A", "B"])
        
        # Rastgele hedef balonlar
        colors = ["kırmızı", "mavi", "yeşil", "sarı"]
        shapes = ["daire", "üçgen", "kare"]
        
        num_balloons = random.randint(2, 4)
        self.target_balloons = [
            (random.choice(colors), random.choice(shapes))
            for _ in range(num_balloons)
        ]
        
        balloon_text = ", ".join([f"{c} {s}" for c, s in self.target_balloons])
        
        self.logger.info(f"🎲 QR Kod Okundu: Bölge {self.qr_zone}")
        self.logger.info(f"🎈 Hedef Balonlar: {balloon_text}")
        
        self.notification_manager.show_notification(
            f"Bölge: {self.qr_zone} | Hedefler: {balloon_text}",
            "warning",
            5000
        )
        
        QMessageBox.information(self, "Angajman Görevi",
                               f"📍 Bölge: {self.qr_zone}\n\n"
                               f"🎈 Hedef Balonlar:\n{balloon_text}\n\n"
                               f"⚠ Orta bölge güvenli - Ateş etme!\n"
                               f"   Güvenli açı: {self.safe_zone_angle[0]}° - {self.safe_zone_angle[1]}°")
    
    def check_safe_zone(self, angle):
        """Güvenli bölgede mi kontrol et"""
        start, end = self.safe_zone_angle
        return start <= angle <= end
    
    def toggle_auto_mode(self):
        """Otonom moda geç"""
        if not self.auto_btn.isChecked():
            self.auto_btn.setChecked(True)
            return
        
        self.autonomous_mode = True
        self.semi_auto_mode = False
        self.angajman_mode = False
        self.manual_btn.setChecked(False)
        self.semi_auto_btn.setChecked(False)
        self.angajman_btn.setChecked(False)
        self.manual_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.semi_auto_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.angajman_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.auto_btn.setStyleSheet(styles.TOGGLE_BUTTON_ACTIVE_STYLE)
        
        # Slider ve ateş butonunu gizle
        self.pan_slider.setEnabled(False)
        self.tilt_slider.setEnabled(False)
        self.fire_btn.setVisible(False)
        
        self.logger.info("🤖 OTONOM MOD Aktif - Otomatik takip ve ateş")
    
    def toggle_system(self):
        """Sistemi başlat/durdur"""
        if self.system_btn.isChecked():
            # Sistem başlat
            self.system_running = True
            self.system_btn.setText("⏸ DURDUR")
            self.system_btn.setStyleSheet(styles.BUTTON_DANGER_STYLE + """
            QPushButton { padding: 6px 10px; font-size: 10px; min-width: 80px; }
            """)
            self.camera_widget.start_camera()
            
            # FPS sinyalini bağla
            if self.camera_widget.camera_thread:
                self.camera_widget.camera_thread.fps_updated.connect(self.stats_widget.update_fps)
            
            self.camera_status.setText("📷 AÇIK")
            self.camera_status.setStyleSheet(f"color: {styles.COLOR_SUCCESS}; font-size: 11px;")
            self.stats_widget.start_tracking()
            self.sound.play_system_start()
            
            # Sistem durumu güncelle
            self.system_status_widget.update_camera_status(True)
            self.notification_manager.show_notification("Sistem başlatıldı", "success")
            
            self.logger.info("▶ Sistem BAŞLATILDI")
        else:
            # Sistem durdur
            self.system_running = False
            self.system_btn.setText("▶ BAŞLAT")
            self.system_btn.setStyleSheet(styles.BUTTON_SUCCESS_STYLE + """
            QPushButton { padding: 6px 10px; font-size: 10px; min-width: 80px; }
            """)
            self.camera_widget.stop_camera()
            self.camera_status.setText("📷 KAPALI")
            self.camera_status.setStyleSheet(f"color: {styles.COLOR_DANGER}; font-size: 11px;")
            self.sound.play_system_stop()
            
            # Sistem durumu güncelle
            self.system_status_widget.update_camera_status(False)
            self.notification_manager.show_notification("Sistem durduruldu", "warning")
            
            self.logger.info("⏸ Sistem DURDURULDU")
    
    def fire(self):
        """Ateş et"""
        if not self.system_running:
            QMessageBox.warning(self, "Uyarı", "⚠ Sistem çalışmıyor! Önce sistemi başlatın.")
            self.sound.play_error()
            self.logger.warning("❌ Ateş reddedildi: Sistem kapalı")
            return
        
        # Angajman modda güvenli bölge kontrolü
        if self.angajman_mode:
            if self.check_safe_zone(self.current_pan):
                QMessageBox.critical(self, "GÜVENLİ BÖLGE!", 
                                    f"🚫 ORTA BÖLGE GÜVENLİ!\n\n"
                                    f"Mevcut açı: {self.current_pan}°\n"
                                    f"Güvenli bölge: {self.safe_zone_angle[0]}°-{self.safe_zone_angle[1]}°\n\n"
                                    f"Bu bölgeye ATEŞ ETMEYİN!")
                self.sound.play_emergency()
                self.logger.critical(f"❌❌❌ GÜVENLİ BÖLGEYE ATEŞ GİRİŞİMİ: {self.current_pan}°")
                self.notification_manager.show_notification("GÜVENLİ BÖLGE İHLALİ!", "error", 3000)
                return
        
        # Yasak alan kontrolü
        if self.no_fire_zone:
            start, end = self.no_fire_zone
            if start <= self.current_pan <= end:
                QMessageBox.warning(self, "Yasak Alan", "🚫 Bu açıya ateş etmek yasak!")
                self.sound.play_error()
                self.logger.warning(f"❌ Ateş reddedildi: Yasak alan ({start}°-{end}°)")
                return
        
        self.kill_count += 1
        self.kill_label.setText(f"💥 {self.kill_count}")
        self.stats_widget.add_fire()
        
        # Performans kaydı
        import random
        hit = random.choice([True, False])
        self.performance_widget.record_shot(hit, time.time() - random.uniform(0.5, 2.0))
        
        # Replay kaydı
        self.replay_manager.record_event("fire", {
            "pan": self.current_pan,
            "tilt": self.current_tilt,
            "hit": hit,
            "mode": "angajman" if self.angajman_mode else "normal"
        })
        
        self.sound.play_fire()
        self.notification_manager.show_notification(f"Ateş! İsabet: {'✓' if hit else '✗'}", "info", 1500)
        self.logger.info(f"🔥 ATEŞ AÇILDI! (Pan: {self.current_pan}°, Tilt: {self.current_tilt}°)")
    
    def emergency_stop(self):
        """Acil durdur"""
        self.system_running = False
        self.system_btn.setChecked(False)
        self.system_btn.setText("▶ BAŞLAT")
        self.system_btn.setStyleSheet(styles.BUTTON_SUCCESS_STYLE)
        self.camera_widget.stop_camera()
        self.sound.play_emergency()
        self.logger.critical("🛑 ACİL DURDUR AKTİF!")
        QMessageBox.critical(self, "Acil Durdur", "🛑 Sistem acil durduruldu!")
    
    def set_no_fire_zone(self):
        """Yasak alan belirle"""
        dialog = NoFireZoneDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.no_fire_zone = dialog.get_zone()
            start, end = self.no_fire_zone
            self.sound.play_success()
            self.logger.info(f"🚫 Yasak alan belirlendi: {start}° - {end}°")
            QMessageBox.information(self, "Yasak Alan", 
                                   f"✅ Yasak alan ayarlandı:\n{start}° - {end}°")
    
    def toggle_video_recording(self):
        """Video kaydını başlat/durdur"""
        if self.video_rec_btn.isChecked():
            path = self.camera_widget.start_recording()
            self.video_rec_btn.setText("⏹ DURDUR")
            self.video_rec_btn.setStyleSheet(styles.BUTTON_DANGER_STYLE + """
            QPushButton { padding: 6px 10px; font-size: 10px; min-width: 80px; }
            """)
            self.video_recording = True
            self.logger.info(f"🎥 Video kaydı başladı: {path}")
        else:
            self.camera_widget.stop_recording()
            self.video_rec_btn.setText("🎥 VİDEO")
            self.video_rec_btn.setStyleSheet(styles.BUTTON_STYLE + """
            QPushButton { padding: 6px 10px; font-size: 10px; min-width: 80px; }
            """)
            self.video_recording = False
            self.logger.info("⏹ Video kaydı durduruldu")
    
    def toggle_screen_recording(self):
        """Ekran kaydını başlat/durdur"""
        if self.screen_rec_btn.isChecked():
            path = self.screen_recorder.start_recording()
            self.screen_rec_btn.setText("⏹ DURDUR")
            self.screen_rec_btn.setStyleSheet(styles.BUTTON_DANGER_STYLE + """
            QPushButton { padding: 6px 10px; font-size: 10px; min-width: 80px; }
            """)
            self.screen_recording = True
            self.logger.info(f"📹 Ekran kaydı başladı: {path}")
        else:
            self.screen_recorder.stop_recording()
            self.screen_rec_btn.setText("📹 EKRAN")
            self.screen_rec_btn.setStyleSheet(styles.BUTTON_STYLE + """
            QPushButton { padding: 6px 10px; font-size: 10px; min-width: 80px; }
            """)
            self.screen_recording = False
            self.logger.info("⏹ Ekran kaydı durduruldu")
    
    def save_log(self):
        """Log dosyasını kaydet"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"tuna_log_{timestamp}.txt"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Log Kaydet", default_name, "Text Files (*.txt)"
        )
        
        if file_path:
            try:
                logs = self.logger.get_logs()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(logs)
                self.logger.info(f"💾 Log kaydedildi: {file_path}")
                QMessageBox.information(self, "Başarılı", f"✅ Log kaydedildi:\n{file_path}")
            except Exception as e:
                self.logger.error(f"❌ Log kaydetme hatası: {e}")
                QMessageBox.critical(self, "Hata", f"❌ Log kaydedilemedi:\n{e}")
    
    def update_logs(self):
        """Log panelini güncelle"""
        logs = self.logger.get_logs()
        # Son 50 satırı göster
        log_lines = logs.split('\n')[-50:]
        self.log_text.setPlainText('\n'.join(log_lines))
        # En alta scroll
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def clear_logs(self):
        """Log panelini temizle"""
        self.log_text.clear()
        # Timer'ı geçici durdur
        self.log_timer.stop()
        self.logger.info("🗑 Log paneli temizlendi")
        # 2 saniye sonra timer'ı tekrar başlat
        QTimer.singleShot(2000, self.log_timer.start)
    
    def toggle_sound(self):
        """Sesi aç/kapat"""
        enabled = self.sound.toggle()
        if enabled:
            self.sound_btn.setText("🔊 SES")
            self.sound_btn.setStyleSheet(styles.TOGGLE_BUTTON_ACTIVE_STYLE + """
            QPushButton { padding: 6px 10px; font-size: 10px; min-width: 80px; }
            """)
            self.sound.play_click()
            self.logger.info("🔊 Ses aktif")
        else:
            self.sound_btn.setText("🔇 SESSİZ")
            self.sound_btn.setStyleSheet(styles.BUTTON_STYLE + """
            QPushButton { padding: 6px 10px; font-size: 10px; min-width: 80px; }
            """)
            self.logger.info("🔇 Ses kapatıldı")
    
    def toggle_fullscreen(self):
        """Tam ekran modu"""
        if self.isFullScreen():
            self.showNormal()
            self.fullscreen_btn.setText("⛶ TAM")
            self.logger.info("↕ Normal ekran")
        else:
            self.showFullScreen()
            self.fullscreen_btn.setText("◱ ÇIKIŞ")
            self.logger.info("⛶ Tam ekran modu")
        self.sound.play_click()
    
    def cycle_theme(self):
        """Temayı değiştir"""
        themes = ["dark", "light", "night", "blue"]
        current_index = themes.index(self.theme_manager.current_theme)
        next_index = (current_index + 1) % len(themes)
        new_theme = themes[next_index]
        
        self.theme_manager.set_theme(new_theme)
        self.apply_theme(new_theme)
        self.sound.play_click()
        
        theme_names = {
            "dark": "Karanlık",
            "light": "Aydınlık",
            "night": "Gece Görüşü",
            "blue": "Mavi"
        }
        self.logger.info(f"🎨 Tema değiştirildi: {theme_names[new_theme]}")
    
    def apply_theme(self, theme_name):
        """Temayı uygula"""
        colors = self.theme_manager.get_theme(theme_name)
        
        # Ana pencere
        self.setStyleSheet(f"QMainWindow {{ background-color: {colors['primary']}; }}")
        
        # Tüm widget'leri güncelle (basitleştirilmiş)
        # Gerçek uygulamada tüm widget'lerin stilini güncellemeniz gerekir
        self.logger.info(f"🎨 Tema uygulandı: {theme_name}")
    
    def toggle_replay_recording(self):
        """Görev kaydını başlat/durdur"""
        if self.replay_rec_btn.isChecked():
            self.replay_manager.start_recording()
            self.replay_rec_btn.setText("⏹ KAYIT")
            self.replay_rec_btn.setStyleSheet(styles.BUTTON_DANGER_STYLE + """
            QPushButton { padding: 6px 10px; font-size: 10px; min-width: 80px; }
            """)
            self.logger.info("📹 Görev kaydı başladı")
        else:
            self.replay_manager.stop_recording()
            filepath = self.replay_manager.save_replay()
            self.replay_rec_btn.setText("📹 GÖREV")
            self.replay_rec_btn.setStyleSheet(styles.BUTTON_STYLE + """
            QPushButton { padding: 6px 10px; font-size: 10px; min-width: 80px; }
            """)
            if filepath:
                self.logger.info(f"💾 Görev kaydedildi: {filepath}")
                QMessageBox.information(self, "Kayıt Tamamlandı", 
                                       f"Görev kaydedildi:\n{filepath}")
    
    def handle_voice_command(self, command):
        """Ses komutunu işle"""
        self.logger.info(f"🎤 Ses komutu: {command}")
        
        if command == "fire":
            if self.fire_btn.isVisible():
                self.fire()
        elif command == "stop":
            if self.system_running:
                self.system_btn.setChecked(False)
                self.toggle_system()
        elif command == "start":
            if not self.system_running:
                self.system_btn.setChecked(True)
                self.toggle_system()
        elif command == "manual":
            self.manual_btn.setChecked(True)
            self.toggle_manual_mode()
        elif command == "auto":
            self.auto_btn.setChecked(True)
            self.toggle_auto_mode()
        elif command == "semi_auto":
            self.semi_auto_btn.setChecked(True)
            self.toggle_semi_auto_mode()
        elif command == "emergency":
            self.emergency_stop()
    
    def keyPressEvent(self, event):
        """Klavye tuşlarını yakala"""
        if self.voice_manager.enabled:
            key = event.key()
            key_map = {
                0x46: "f",      # F
                0x53: "s",      # S
                0x52: "r",      # R
                0x4D: "m",      # M
                0x41: "a",      # A
                0x59: "y",      # Y
                0x01000000: "esc"  # ESC
            }
            
            if key in key_map:
                self.voice_manager.simulate_voice_command(key_map[key])
    
    def closeEvent(self, event):
        """Pencere kapatılırken"""
        self.camera_widget.stop_camera()
        self.screen_recorder.stop()
        self.screen_recorder.wait()
        self.logger.info("❌ Uygulama kapatıldı")
        event.accept()