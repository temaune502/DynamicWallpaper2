import math
from PySide6.QtGui import QColor, QLinearGradient, QBrush, QPen
from effects import BaseEffect

class GlitchEffect(BaseEffect):
    EFFECT_NAME = "glitch"
    
    def draw(self, p, w, h, phase):
        if self.show_background:
            # Background gradient (dark blue-gray)
            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0.0, QColor(12, 16, 24))
            grad.setColorAt(0.5, QColor(90, 94, 104))
            grad.setColorAt(1.0, QColor(14, 36, 64))
            p.fillRect(0, 0, w, h, QBrush(grad))

        # Scanlines
        p.setPen(QPen(QColor(220, 220, 230, 18), 1))
        for y in range(0, h, 3):
            p.drawLine(0, y, w, y)

        # Glitch bands
        bands = 6
        band_min, band_max = 10, 32
        shift_amp = 12
        col_step, col_w, col_alpha = 180, 10, 50
        band_alpha = 42
        for i in range(bands):
            t = (phase + i * 0.13) % 1.0
            band_h = int(band_min + (band_max - band_min) * (0.5 + 0.5 * abs(math.sin(t * math.pi * 2))))
            yb = int(t * h)
            shift = int(shift_amp * math.sin((phase * 6 + i) * 2))
            p.fillRect(max(0, 0 + shift), yb, max(0, w - abs(shift)), band_h, QColor(180, 190, 210, band_alpha))

            step = max(col_step, w // 8)
            for j in range(0, w, step):
                cx = j + int((math.sin(phase * 24 + j * 0.005 + i) * 0.5 + 0.5) * 30)
                p.fillRect(cx, yb, col_w, band_h, QColor(120, 140, 180, col_alpha))

        # Neon diagonal lines
        neon_color = QColor(64, 160, 255, 140)
        p.setPen(QPen(neon_color, 2))
        for i in range(12):
            offset = int((phase * 140 + i * 60) % (w + h))
            p.drawLine(0, offset, offset, 0)
            p.drawLine(w - offset, h, w, h - offset)

        # Vertical streaks
        p.setPen(QPen(QColor(200, 200, 210, 22), 1))
        for x in range(0, w, max(60, w // 24)):
            jitter = int(5 * math.sin(phase * 10 + x * 0.02))
            p.drawLine(x + jitter, 0, x + jitter, h)
