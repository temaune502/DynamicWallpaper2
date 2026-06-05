import math
from PySide6.QtGui import QColor, QLinearGradient, QBrush, QPen
from PySide6.QtCore import Qt
from effects import BaseEffect

class NeonGridEffect(BaseEffect):
    EFFECT_NAME = "neon_grid"
    
    def draw(self, p, w, h, phase):
        if self.show_background:
            grad = QLinearGradient(0, 0, w, h)
            grad.setColorAt(0.0, QColor(18, 22, 30))
            grad.setColorAt(1.0, QColor(8, 10, 14))
            p.fillRect(0, 0, w, h, QBrush(grad))

        p.setPen(QPen(QColor(64, 160, 255, 180), 1))
        spacing = max(40, min(80, w // 24))
        drift = int(10 * math.sin(phase * 2))
        for x in range(0, w, spacing):
            p.drawLine(x + drift, 0, x + drift, h)
        for y in range(0, h, spacing):
            p.drawLine(0, y - drift, w, y - drift)

        p.setPen(QPen(QColor(0, 255, 200, 160), 2))
        for i in range(8):
            off = int((phase * 120 + i * 100) % (w + h))
            p.drawLine(0, off // 2, off, 0)
            p.drawLine(w - off, h, w, h - off // 2)

        p.setPen(QPen(QColor(200, 220, 240, 18), 1))
        for y in range(0, h, 3):
            p.drawLine(0, y, w, y)
