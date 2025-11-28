import json
import time
from datetime import datetime
import os


class ReplayManager:
    """Görev kayıt ve tekrar oynatma yöneticisi"""
    
    def __init__(self):
        self.recording = False
        self.replay_data = []
        self.start_time = None
        self.current_replay = None
        self.replay_index = 0
        
    def start_recording(self):
        """Kayıt başlat"""
        self.recording = True
        self.replay_data = []
        self.start_time = time.time()
        print("📹 Görev kaydı başladı")
    
    def stop_recording(self):
        """Kayıt durdur"""
        self.recording = False
        print(f"⏹ Görev kaydı durduruldu - {len(self.replay_data)} olay kaydedildi")
    
    def record_event(self, event_type, data):
        """Olay kaydet"""
        if not self.recording:
            return
        
        timestamp = time.time() - self.start_time
        event = {
            "timestamp": timestamp,
            "type": event_type,
            "data": data
        }
        self.replay_data.append(event)
    
    def save_replay(self, filepath=None):
        """Kaydı dosyaya kaydet"""
        if not self.replay_data:
            print("❌ Kaydedilecek veri yok")
            return None
        
        if filepath is None:
            os.makedirs("replays", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"replays/replay_{timestamp}.json"
        
        replay_file = {
            "version": "1.0",
            "duration": self.replay_data[-1]["timestamp"] if self.replay_data else 0,
            "events": self.replay_data
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(replay_file, f, indent=2)
            print(f"💾 Replay kaydedildi: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Replay kaydetme hatası: {e}")
            return None
    
    def load_replay(self, filepath):
        """Kaydı yükle"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.current_replay = json.load(f)
            self.replay_index = 0
            print(f"📂 Replay yüklendi: {filepath}")
            print(f"   Süre: {self.current_replay['duration']:.1f}s")
            print(f"   Olaylar: {len(self.current_replay['events'])}")
            return True
        except Exception as e:
            print(f"❌ Replay yükleme hatası: {e}")
            return False
    
    def get_next_event(self, current_time):
        """Belirli zamandaki olayları getir"""
        if not self.current_replay:
            return None
        
        events = []
        while self.replay_index < len(self.current_replay['events']):
            event = self.current_replay['events'][self.replay_index]
            if event['timestamp'] <= current_time:
                events.append(event)
                self.replay_index += 1
            else:
                break
        
        return events if events else None
    
    def is_replay_finished(self):
        """Replay bitti mi?"""
        if not self.current_replay:
            return True
        return self.replay_index >= len(self.current_replay['events'])
    
    def get_replay_duration(self):
        """Replay süresi"""
        if not self.current_replay:
            return 0
        return self.current_replay.get('duration', 0)
    
    def reset_replay(self):
        """Replay'i başa sar"""
        self.replay_index = 0