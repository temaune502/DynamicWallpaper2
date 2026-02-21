import math
from PySide6.QtGui import QColor, QLinearGradient, QBrush
from PySide6.QtCore import Qt
from effects import BaseEffect

class PlasmaFogEffect(BaseEffect):
    EFFECT_NAME = "plasma_fog"
    
    def draw(self, p, w, h, phase):
        # Background
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(20, 0, 30))
        
        # We'll use large gradients to simulate plasma
        for i in range(3):
            t = phase * 2 * math.pi + i * (2 * math.pi / 3)
            cx = w/2 + math.sin(t) * w/3
            cy = h/2 + math.cos(t * 0.7) * h/3
            
            radius = min(w, h) // 1.5
            grad = QLinearGradient(cx - radius, cy - radius, cx + radius, cy + radius)
            
            colors = [
                (QColor(255, 0, 150, 40), QColor(0, 200, 255, 40)),
                (QColor(0, 255, 150, 40), QColor(200, 0, 255, 40)),
                (QColor(255, 200, 0, 40), QColor(0, 100, 255, 40))
            ]
            
            c1, c2 = colors[i]
            grad.setColorAt(0, c1)
            grad.setColorAt(1, c2)
            
            p.setBrush(QBrush(grad))
            p.setPen(Qt.NoPen)
            p.drawEllipse(int(cx - radius), int(cy - radius), int(radius * 2), int(radius * 2))
