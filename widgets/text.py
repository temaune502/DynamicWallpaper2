from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import Qt
import math
from widgets import BaseWidget

class SystemInfoWidget(BaseWidget):
    WIDGET_NAME = "text"
    
    def draw(self, p: QPainter, w: int, h: int, phase: float = 0.0):
        text = self.config.get('text', "System Active")
        font_size = self.config.get('font_size', 14)
        
        color_data = self.config.get('color', [0, 255, 255, 150])
        if isinstance(color_data, list):
            color = QColor(*color_data)
        else:
            color = QColor(color_data)
        
        font = QFont("Consolas", font_size)
        p.setFont(font)
        metrics = p.fontMetrics()
        rect = metrics.boundingRect(text)
        
        start_x, start_y = self.get_pos(w, h, rect.width(), rect.height())
        
        shift = 0.5 + 0.5 * math.sin(phase * 2 * math.pi * 2)
        color.setAlpha(int(100 + 100 * shift))
        
        p.setPen(color)
        p.drawText(start_x, start_y + rect.height(), text)
