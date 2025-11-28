import cv2
import numpy as np
import time
from datetime import datetime
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication
import os


class ScreenRecorderThread(QThread):
    """Ekran kaydı thread'i"""
    
    def __init__(self, fps=30):
        super().__init__()
        self.fps = fps
        self.running = False
        self.recording = False
        self.video_writer = None
        self.output_path = None
        
    def run(self):
        """Thread'in ana döngüsü"""
        self.running = True
        
        while self.running:
            if self.recording and self.video_writer is not None:
                try:
                    # Ekranı yakala
                    screen = QApplication.primaryScreen()
                    screenshot = screen.grabWindow(0)
                    
                    # QPixmap'i numpy array'e çevir
                    size = screenshot.size()
                    width = size.width()
                    height = size.height()
                    
                    # QImage'e çevir
                    qimage = screenshot.toImage()
                    qimage = qimage.convertToFormat(qimage.Format_RGB888)
                    
                    # Numpy array'e çevir
                    ptr = qimage.bits()
                    ptr.setsize(height * width * 3)
                    arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 3))
                    
                    # BGR'ye çevir (OpenCV için)
                    frame = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
                    
                    # Yaz
                    self.video_writer.write(frame)
                    
                except Exception as e:
                    print(f"Ekran kaydı hatası: {e}")
            
            # FPS sınırlama
            time.sleep(1.0 / self.fps)
        
        # Temizlik
        if self.video_writer is not None:
            self.video_writer.release()
        print("🔴 Ekran kaydı durduruldu")
    
    def start_recording(self):
        """Ekran kaydını başlat"""
        if self.recording:
            return None
        
        # Çıktı dosyası
        os.makedirs("recordings", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_path = f"recordings/screen_{timestamp}.mp4"
        
        # Ekran boyutunu al
        screen = QApplication.primaryScreen()
        size = screen.size()
        width = size.width()
        height = size.height()
        
        # Video writer oluştur
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(
            self.output_path, fourcc, self.fps, 
            (width, height)
        )
        
        self.recording = True
        print(f"🔴 Ekran kaydı başladı: {self.output_path}")
        return self.output_path
    
    def stop_recording(self):
        """Ekran kaydını durdur"""
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
        self.recording = False
        print(f"⏹ Ekran kaydı tamamlandı: {self.output_path}")
    
    def stop(self):
        """Thread'i durdur"""
        self.running = False
        self.stop_recording()