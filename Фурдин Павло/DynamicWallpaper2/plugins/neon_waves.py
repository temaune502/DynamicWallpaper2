import math
from PySide6.QtGui import QColor, QPen, QLinearGradient, QBrush
from PySide6.QtCore import Qt, QPointF
from effects import BaseEffect

class NeonWavesEffect(BaseEffect):
    EFFECT_NAME = "neon_waves"
    
    def draw(self, p, w, h, phase):
        # 1. Retro Background
        if self.show_background:
            bg = QLinearGradient(0, 0, 0, h)
            bg.setColorAt(0.0, QColor(10, 0, 20))
            bg.setColorAt(0.5, QColor(40, 0, 60))
            bg.setColorAt(1.0, QColor(100, 20, 100))
            p.fillRect(0, 0, w, h, QBrush(bg))

        # 2. Perspective Grid (Floor)
        horizon = h * 0.4
        p.setPen(QPen(QColor(255, 0, 255, 60), 1))
        
        # Vanishing point lines
        num_v_lines = 20
        for i in range(num_v_lines + 1):
            x_start = (w / num_v_lines) * i
            p.drawLine(int(w/2), int(horizon), int(x_start), h)

        # Horizontal lines with perspective scaling
        num_h_lines = 15
        for i in range(num_h_lines):
            # Non-linear spacing for perspective
            t = (i / num_h_lines)
            y = horizon + (h - horizon) * (t ** 2)
            alpha = int(20 + 180 * t)
            p.setPen(QPen(QColor(255, 0, 255, alpha), 1))
            p.drawLine(0, int(y), w, int(y))

        # 3. Neon Waves
        num_waves = 3
        for i in range(num_waves):
            p.setBrush(Qt.NoBrush)
            hue = (300 + i * 20) % 360 # Magenta to Purple
            color = QColor.fromHsv(hue, 200, 255, 150)
            p.setPen(QPen(color, 3))
            
            points = []
            wave_y = horizon + (i * 40)
            for x in range(0, w + 10, 10):
                # Complex wave motion
                off = math.sin(x * 0.01 + phase * 2 + i) * 30
                off += math.sin(x * 0.02 - phase * 1.5) * 15
                points.append(QPointF(x, wave_y + off))
            
            p.drawPolyline(points)
            
            # Glow for the wave
            p.setPen(QPen(QColor.fromHsv(hue, 200, 255, 40), 8))
            p.drawPolyline(points)

        # 4. Sun or Horizon Glow
        sun_grad = QLinearGradient(0, horizon - 50, 0, horizon)
        sun_grad.setColorAt(0, Qt.transparent)
        sun_grad.setColorAt(1, QColor(255, 100, 0, 100))
        p.fillRect(0, int(horizon - 50), w, 50, QBrush(sun_grad))
