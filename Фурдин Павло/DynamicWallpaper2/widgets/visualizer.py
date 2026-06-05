from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import Qt
import math
from widgets import BaseWidget

class VisualizerWidget(BaseWidget):
    WIDGET_NAME = "visualizer"
    
    def draw(self, p: QPainter, w: int, h: int, phase: float = 0.0):
        num_bars = 12
        bar_w = 4
        spacing = 3
        total_w = num_bars * (bar_w + spacing)
        
        start_x, start_y = self.get_pos(w, h, total_w, 30)
        
        p.setPen(Qt.NoPen)
        for i in range(num_bars):
            val = 5 + 20 * (0.5 + 0.5 * math.sin(phase * 2 * math.pi * 4 + i * 0.5))
            p.setBrush(QColor(0, 255, 255, 150))
            p.drawRect(int(start_x + i * (bar_w + spacing)), int(start_y + 30 - val), bar_w, int(val))
