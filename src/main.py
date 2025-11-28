import sys
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from gui.main_window import MainWindow
from gui.splash_screen import SplashScreen


def main():
    """Ana uygulama"""
    app = QApplication(sys.argv)
    
    # Uygulama bilgileri
    app.setApplicationName("TUNA HSS")
    app.setOrganizationName("TUNA Team")
    
    # Splash screen göster
    splash = SplashScreen()
    splash.show()
    app.processEvents()
    
    # Yükleme simülasyonu
    loading_steps = [
        (20, "Modüller yükleniyor..."),
        (40, "Kamera başlatılıyor..."),
        (60, "AI modeli yükleniyor..."),
        (80, "Sistem kontrolleri yapılıyor..."),
        (100, "Hazırlanıyor...")
    ]
    
    for progress, status in loading_steps:
        splash.set_progress(progress, status)
        app.processEvents()
        time.sleep(0.3)  # Simülasyon gecikmesi
    
    # Ana pencere
    window = MainWindow()
    
    # Splash'i kapat ve ana pencereyi göster
    splash.finish_loading(window)
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()