import math
from PySide6.QtGui import QColor, QLinearGradient, QBrush, QPen
from effects import BaseEffect

class CyberWavesEffect(BaseEffect):
    EFFECT_NAME = "cyber_waves"
    
    def draw(self, p, w, h, phase):
        if self.show_background:
            bg = QLinearGradient(0, 0, 0, h)
            bg.setColorAt(0.0, QColor(10, 10, 20))
            bg.setColorAt(1.0, QColor(30, 10, 40))
            p.fillRect(0, 0, w, h, QBrush(bg))
        
        for i in range(5):
            t = (phase + i * 0.2) % 1.0
            p.setPen(QPen(QColor(0, 150 + i * 20, 255, 100), 2))
            
            path = []
            amp = h // 6
            freq = 0.005 + i * 0.001
            for x in range(0, w + 10, 10):
                y = h // 2 + amp * math.sin(x * freq + phase * 10 + i)
                path.append((x, y))
            
            for j in range(len(path) - 1):
                p.drawLine(path[j][0], path[j][1], path[j+1][0], path[j+1][1])
