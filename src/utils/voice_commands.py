"""
Ses komutları modülü
NOT: Gerçek ses tanıma için 'speech_recognition' kütüphanesi gerekir
pip install SpeechRecognition pyaudio

Şimdilik klavye kısayolları ile simüle ediyoruz
"""

from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import threading


class VoiceCommandManager(QObject):
    """Ses komutları yöneticisi"""
    
    # Sinyaller
    command_detected = pyqtSignal(str)  # Komut algılandı
    
    def __init__(self):
        super().__init__()
        self.enabled = False
        self.listening = False
        
        # Komut listesi
        self.commands = {
            "ateş": "fire",
            "ateş et": "fire",
            "fire": "fire",
            "dur": "stop",
            "stop": "stop",
            "durdur": "stop",
            "başlat": "start",
            "start": "start",
            "manuel": "manual",
            "otonom": "auto",
            "yarı otonom": "semi_auto",
            "acil": "emergency",
            "acil durdur": "emergency",
        }
        
        print("🎤 Ses komutları hazır (Klavye simülasyonu)")
        print("   Klavye kısayolları:")
        print("   F = Ateş")
        print("   S = Dur/Durdur")
        print("   R = Başlat")
        print("   M = Manuel")
        print("   A = Otonom")
        print("   Y = Yarı Otonom")
        print("   ESC = Acil Durdur")
    
    def start_listening(self):
        """Dinlemeyi başlat"""
        self.listening = True
        self.enabled = True
        print("🎤 Ses komutları aktif")
    
    def stop_listening(self):
        """Dinlemeyi durdur"""
        self.listening = False
        self.enabled = False
        print("🎤 Ses komutları devre dışı")
    
    def process_command(self, text):
        """Komutu işle"""
        text = text.lower().strip()
        
        if text in self.commands:
            command = self.commands[text]
            print(f"🎤 Komut algılandı: '{text}' -> {command}")
            self.command_detected.emit(command)
            return True
        
        return False
    
    def simulate_voice_command(self, key_text):
        """Klavye ile ses komutunu simüle et"""
        key_map = {
            "f": "ateş",
            "s": "dur",
            "r": "başlat",
            "m": "manuel",
            "a": "otonom",
            "y": "yarı otonom",
            "esc": "acil durdur"
        }
        
        if key_text.lower() in key_map:
            command_text = key_map[key_text.lower()]
            return self.process_command(command_text)
        
        return False


# Gerçek ses tanıma için (isteğe bağlı)
class RealVoiceRecognition:
    """
    Gerçek ses tanıma implementasyonu
    Kullanım için gerekli: pip install SpeechRecognition pyaudio
    """
    
    def __init__(self, callback):
        self.callback = callback
        self.running = False
        self.recognizer = None
        self.microphone = None
        
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            print("🎤 Gerçek ses tanıma hazır")
        except ImportError:
            print("⚠ SpeechRecognition yüklü değil. Klavye simülasyonu kullanılıyor.")
    
    def start(self):
        """Ses tanımayı başlat"""
        if not self.recognizer:
            return
        
        self.running = True
        thread = threading.Thread(target=self._listen_loop, daemon=True)
        thread.start()
    
    def stop(self):
        """Ses tanımayı durdur"""
        self.running = False
    
    def _listen_loop(self):
        """Dinleme döngüsü"""
        import speech_recognition as sr
        
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            print("🎤 Dinleniyor...")
            
            while self.running:
                try:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    text = self.recognizer.recognize_google(audio, language='tr-TR')
                    print(f"🎤 Algılanan: {text}")
                    self.callback(text)
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except Exception as e:
                    print(f"🎤 Hata: {e}")