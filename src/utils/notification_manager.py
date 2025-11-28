from PyQt5.QtWidgets import QLabel, QGraphicsOpacityEffect
from PyQt5.QtCore import QTimer, QPropertyAnimation, QEasingCurve, Qt
from PyQt5.QtGui import QFont
from gui import styles


class NotificationManager:
    """Bildirim yöneticisi - Toast bildirimleri"""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.notifications = []
        self.current_y = 10
    
    def show_notification(self, message, notification_type="info", duration=3000):
        """
        Bildirim göster
        notification_type: 'success', 'warning', 'error', 'info'
        """
        # Bildirim widget'i oluştur
        notification = QLabel(self.parent)
        notification.setText(message)
        notification.setWordWrap(True)
        notification.setMaximumWidth(300)
        notification.setMinimumHeight(50)
        
        # Stil
        colors = {
            "success": (styles.COLOR_SUCCESS, styles.COLOR_PRIMARY),
            "warning": (styles.COLOR_WARNING, styles.COLOR_PRIMARY),
            "error": (styles.COLOR_DANGER, "white"),
            "info": (styles.COLOR_INFO, "white")
        }
        
        bg_color, text_color = colors.get(notification_type, colors["info"])
        
        notification.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: 10px;
                padding: 15px;
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        
        # İkon ekle
        icons = {
            "success": "✓",
            "warning": "⚠",
            "error": "✗",
            "info": "ℹ"
        }
        icon = icons.get(notification_type, "ℹ")
        notification.setText(f"{icon} {message}")
        
        # Konum
        notification.move(self.parent.width() - 320, self.current_y)
        self.current_y += 70
        
        # Opacity efekti
        opacity_effect = QGraphicsOpacityEffect()
        notification.setGraphicsEffect(opacity_effect)
        
        # Fade in animasyonu
        fade_in = QPropertyAnimation(opacity_effect, b"opacity")
        fade_in.setDuration(300)
        fade_in.setStartValue(0)
        fade_in.setEndValue(1)
        fade_in.setEasingCurve(QEasingCurve.InOutQuad)
        fade_in.start()
        
        notification.show()
        self.notifications.append((notification, fade_in))
        
        # Otomatik kapat
        QTimer.singleShot(duration, lambda: self.hide_notification(notification, opacity_effect))
    
    def hide_notification(self, notification, opacity_effect):
        """Bildirimi gizle"""
        # Fade out animasyonu
        fade_out = QPropertyAnimation(opacity_effect, b"opacity")
        fade_out.setDuration(300)
        fade_out.setStartValue(1)
        fade_out.setEndValue(0)
        fade_out.setEasingCurve(QEasingCurve.InOutQuad)
        fade_out.finished.connect(lambda: self.remove_notification(notification))
        fade_out.start()
    
    def remove_notification(self, notification):
        """Bildirimi kaldır"""
        notification.deleteLater()
        self.current_y -= 70
        
        # Liste'den çıkar
        self.notifications = [(n, a) for n, a in self.notifications if n != notification]