from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import Qt
import psutil
from widgets import BaseWidget

class RAMUsageWidget(BaseWidget):
    WIDGET_NAME = "ram"
    
    def __init__(self, config=None):
        super().__init__(config)
        self.config.setdefault('update_interval', 1000)

    def draw(self, p: QPainter, w: int, h: int, phase: float = 0.0):
        ram = psutil.virtual_memory().percent
        text = f"RAM: {ram}%"
        
        p.setFont(QFont("Consolas", self.config.get('font_size', 12)))
        metrics = p.fontMetrics()
        th = metrics.height()
        
        start_x, start_y = self.get_pos(w, h, 120, th + 10)
        
        p.setBrush(QColor(50, 50, 50, 100))
        p.setPen(Qt.NoPen)
        p.drawRect(start_x, start_y + th + 2, 100, 4)
        
        p.setBrush(QColor(0, 150, 255, 200) if ram < 80 else QColor(255, 150, 0, 200))
        p.drawRect(start_x, start_y + th + 2, int(ram), 4)
        
        p.setPen(QColor(255, 255, 255, 200))
        p.drawText(start_x, start_y + th, text)
