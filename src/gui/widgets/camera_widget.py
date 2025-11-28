import cv2
import time
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel
import os


class CameraThread(QThread):
    """Kamera görüntüsü yakalama thread'i"""
    frame_ready = pyqtSignal(object)  # QImage nesnesi gönderir
    fps_updated = pyqtSignal(int)     # FPS değeri gönderir
    
    def __init__(self, camera_index=0, width=1280, height=720, fps=30):
        super().__init__()
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.target_fps = fps
        self.running = False
        self.recording = False
        self.video_writer = None
        
        # FPS hesaplama
        self.fps_counter = 0
        self.fps_time = time.time()
        self.current_fps = 0
        
    def run(self):
        """Thread'in ana döngüsü"""
        self.running = True
        cap = cv2.VideoCapture(self.camera_index)
        
        if not cap.isOpened():
            print("❌ Kamera açılamadı!")
            return
        
        # Kamera ayarları
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        
        print(f"✅ Kamera açıldı: {self.width}x{self.height} @ {self.target_fps} FPS")
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Video kaydı
            if self.recording and self.video_writer is not None:
                self.video_writer.write(frame)
            
            # Nişangah çiz
            frame = self.draw_crosshair(frame)
            
            # FPS hesapla ve göster
            self.calculate_fps()
            cv2.putText(frame, f"FPS: {self.current_fps}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 255, 136), 2)
            
            # Kayıt göstergesi
            if self.recording:
                cv2.circle(frame, (self.width - 30, 30), 10, (0, 0, 255), -1)
                cv2.putText(frame, "REC", 
                           (self.width - 70, 35), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.6, (0, 0, 255), 2)
            
            # Frame'i QImage'e çevir
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Signal gönder
            self.frame_ready.emit(qt_image)
            
            # FPS sınırlama
            time.sleep(1.0 / self.target_fps)
        
        # Temizlik
        if self.video_writer is not None:
            self.video_writer.release()
        cap.release()
        print("🔴 Kamera kapatıldı")
    
    def draw_crosshair(self, frame):
        """Nişangah çizer"""
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        color = (0, 255, 136)  # Yeşil
        thickness = 2
        size = 30
        
        # Merkez artı
        cv2.line(frame, (center_x - size, center_y), (center_x + size, center_y), color, thickness)
        cv2.line(frame, (center_x, center_y - size), (center_x, center_y + size), color, thickness)
        
        # Daire
        cv2.circle(frame, (center_x, center_y), size + 10, color, thickness)
        
        return frame
    
    def calculate_fps(self):
        """FPS hesapla"""
        self.fps_counter += 1
        if time.time() - self.fps_time >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.fps_time = time.time()
            # FPS sinyali gönder
            self.fps_updated.emit(self.current_fps)
    
    def start_recording(self, output_path):
        """Video kaydını başlat"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(
            output_path, fourcc, self.target_fps, 
            (self.width, self.height)
        )
        self.recording = True
        print(f"🔴 Video kaydı başladı: {output_path}")
    
    def stop_recording(self):
        """Video kaydını durdur"""
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
        self.recording = False
        print("⏹ Video kaydı durduruldu")
    
    def stop(self):
        """Thread'i durdur"""
        self.running = False
        self.stop_recording()


class CameraWidget(QLabel):
    """Kamera görüntüsünü gösteren widget"""
    
    def __init__(self, width=1600, height=700):
        super().__init__()
        self.setFixedSize(width, height)
        self.setScaledContents(True)
        self.setAlignment(Qt.AlignCenter)
        
        # Thread
        self.camera_thread = None
        
        # Başlangıç görüntüsü
        self.setText("📷 KAMERA BEKLENIYOR...")
        self.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 2px solid #333333;
                border-radius: 5px;
                font-size: 24px;
                font-weight: bold;
            }
        """)
    
    def start_camera(self, camera_index=0):
        """Kamerayı başlat"""
        if self.camera_thread is not None:
            self.stop_camera()
        
        self.camera_thread = CameraThread(camera_index)
        self.camera_thread.frame_ready.connect(self.update_frame)
        self.camera_thread.start()
    
    def stop_camera(self):
        """Kamerayı durdur"""
        if self.camera_thread is not None:
            self.camera_thread.stop()
            self.camera_thread.wait()
            self.camera_thread = None
        self.setText("📷 KAMERA DURDURULDU")
    
    def update_frame(self, qt_image):
        """Frame güncelle"""
        pixmap = QPixmap.fromImage(qt_image)
        self.setPixmap(pixmap)
    
    def start_recording(self):
        """Video kaydını başlat"""
        if self.camera_thread is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"recordings/video_{timestamp}.mp4"
            self.camera_thread.start_recording(output_path)
            return output_path
        return None
    
    def stop_recording(self):
        """Video kaydını durdur"""
        if self.camera_thread is not None:
            self.camera_thread.stop_recording()