from PySide6.QtCore import Qt, QDateTime, QRectF
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from widgets import BaseWidget

class DigitalClockWidget(BaseWidget):
    WIDGET_NAME = "digital_clock"
    
    def __init__(self, config=None):
        super().__init__(config)
        self.use_24h = self.config.get('use_24h', True)
        self.show_seconds = self.config.get('show_seconds', True)
        self.show_date = self.config.get('show_date', True)

    def draw(self, p: QPainter, w: int, h: int, phase: float = 0.0):
        now = QDateTime.currentDateTime()
        
        # Dimensions
        total_w = 300
        total_h = 150
        x, y = self.get_pos(w, h, total_w, total_h)
        
        # Transparent BG (optional, mostly clean)
        # p.setBrush(QColor(0,0,0,10))
        # p.drawRoundedRect(x, y, total_w, total_h, 10, 10)
        
        p.setRenderHint(QPainter.Antialiasing)
        
        # Time String
        fmt = "HH:mm" if self.use_24h else "h:mm AP"
        time_str = now.toString(fmt)
        
        # Font Setup
        p.setFont(QFont("Segoe UI", 60, QFont.Bold))
        p.setPen(QColor(255, 255, 255, 240))
        
        # Draw Time
        # Align Left or Center? Center usually looks better for standalone clock
        # But BaseWidget uses x,y as top-left of the box.
        
        # Let's center text in the box we defined
        rect_time = QRectF(x, y, total_w, 80)
        p.drawText(rect_time, Qt.AlignCenter, time_str)
        
        # Seconds Bar (Animated line below time)
        if self.show_seconds:
            seconds = now.time().second()
            msec = now.time().msec()
            smooth_sec = seconds + msec / 1000.0
            
            bar_w = 200
            bar_h = 4
            bx = x + (total_w - bar_w) / 2
            by = y + 90
            
            # Background track
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 255, 255, 30))
            p.drawRoundedRect(bx, by, bar_w, bar_h, 2, 2)
            
            # Progress
            prog = smooth_sec / 60.0
            p.setBrush(QColor(0, 255, 255, 200))
            p.drawRoundedRect(bx, by, bar_w * prog, bar_h, 2, 2)
            
        # Date
        if self.show_date:
            date_str = now.toString("dddd, MMMM d")
            p.setFont(QFont("Segoe UI", 14))
            p.setPen(QColor(220, 220, 220, 200))
            rect_date = QRectF(x, y + 100, total_w, 30)
            p.drawText(rect_date, Qt.AlignCenter, date_str)
