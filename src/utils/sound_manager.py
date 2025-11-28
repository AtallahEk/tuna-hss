import winsound
import threading


class SoundManager:
    """Ses efektleri yöneticisi"""
    
    def __init__(self, enabled=True):
        self.enabled = enabled
    
    def _play_async(self, frequency, duration):
        """Sesi ayrı thread'de çal"""
        if not self.enabled:
            return
        
        def play():
            try:
                winsound.Beep(frequency, duration)
            except:
                pass
        
        thread = threading.Thread(target=play, daemon=True)
        thread.start()
    
    def play_fire(self):
        """Ateş sesi"""
        self._play_async(800, 100)
    
    def play_system_start(self):
        """Sistem başlatma sesi"""
        self._play_async(1000, 200)
    
    def play_system_stop(self):
        """Sistem durdurma sesi"""
        self._play_async(500, 200)
    
    def play_emergency(self):
        """Acil durdur sesi"""
        def emergency_sound():
            for _ in range(3):
                winsound.Beep(1500, 150)
                winsound.Beep(1000, 150)
        
        if self.enabled:
            thread = threading.Thread(target=emergency_sound, daemon=True)
            thread.start()
    
    def play_success(self):
        """Başarı sesi"""
        self._play_async(1200, 100)
    
    def play_error(self):
        """Hata sesi"""
        self._play_async(300, 300)
    
    def play_click(self):
        """Tıklama sesi"""
        self._play_async(600, 50)
    
    def toggle(self):
        """Sesi aç/kapat"""
        self.enabled = not self.enabled
        return self.enabled