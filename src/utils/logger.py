import logging
import os
from datetime import datetime


class TunaLogger:
    """TUNA HSS için özel logger sınıfı"""
    
    def __init__(self, name="TUNA", log_dir="logs"):
        self.name = name
        self.log_dir = log_dir
        
        # Log klasörünü oluştur
        os.makedirs(log_dir, exist_ok=True)
        
        # Logger oluştur
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Eğer handler yoksa ekle (duplicate önleme)
        if not self.logger.handlers:
            # Dosya handler
            log_file = os.path.join(
                log_dir, 
                f"tuna_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Format
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] %(message)s',
                datefmt='%H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def debug(self, msg):
        self.logger.debug(msg)
    
    def info(self, msg):
        self.logger.info(msg)
    
    def warning(self, msg):
        self.logger.warning(msg)
    
    def error(self, msg):
        self.logger.error(msg)
    
    def critical(self, msg):
        self.logger.critical(msg)
    
    def get_logs(self):
        """Log dosyasının içeriğini döndürür"""
        log_file = os.path.join(
            self.log_dir, 
            f"tuna_{datetime.now().strftime('%Y%m%d')}.log"
        )
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Log okunamadı: {e}"