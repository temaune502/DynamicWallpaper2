from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import Qt
import psutil
from widgets import BaseWidget

class CPUUsageWidget(BaseWidget):
    WIDGET_NAME = "cpu"
    
    def __init__(self, config=None):
        super().__init__(config)
        self.config.setdefault('update_interval', 1000)
        self.last_update = 0
        self.cached_cpu = 0
        
    def draw(self, p: QPainter, w: int, h: int, phase: float = 0.0):
        import time
        if time.time() - self.last_update > 1.0:
            self.cached_cpu = psutil.cpu_percent()
            self.last_update = time.time()
            
        cpu = self.cached_cpu
        text = f"CPU: {int(cpu)}%"
        
        p.setFont(QFont("Consolas", self.config.get('font_size', 12)))
        metrics = p.fontMetrics()
        th = metrics.height()
        
        start_x, start_y = self.get_pos(w, h, 120, th + 10)
        
        p.setBrush(QColor(50, 50, 50, 100))
        p.setPen(Qt.NoPen)
        p.drawRect(start_x, start_y + th + 2, 100, 4)
        
        p.setBrush(QColor(0, 255, 100, 200) if cpu < 70 else QColor(255, 50, 50, 200))
        p.drawRect(start_x, start_y + th + 2, int(cpu), 4)
        
        p.setPen(QColor(255, 255, 255, 200))
        p.drawText(start_x, start_y + th, text)
