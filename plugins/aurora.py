import random
import math
from PySide6.QtGui import QColor, QLinearGradient, QBrush, QPen
from PySide6.QtCore import Qt, QPointF
from effects import BaseEffect

class AuroraEffect(BaseEffect):
    EFFECT_NAME = "aurora"
    
    def __init__(self):
        super().__init__()
        self.bands = 3

    def draw(self, p, w, h, phase):
        # Draw sky background
        if self.show_background:
            bg = QLinearGradient(0, 0, 0, h)
            bg.setColorAt(0, QColor(0, 5, 15))
            bg.setColorAt(1, QColor(5, 0, 10))
            p.fillRect(0, 0, w, h, QBrush(bg))

        # 1. Stars background (static)
        p.setPen(QColor(255, 255, 255, 150))
        random.seed(42) # Fixed seed for static stars
        for _ in range(100):
            p.drawPoint(random.randint(0, w), random.randint(0, h))
        random.seed() # Reset seed

        # 2. Aurora layers
        p.setPen(Qt.NoPen)
        for i in range(self.bands):
            t = phase * 0.3 + i * 1.2
            
            # Create a more organic path for the aurora
            points = []
            steps = 30
            for j in range(steps + 1):
                x = j * (w / steps)
                # Smoother wave patterns
                y_base = h * 0.5 + i * 70
                wave1 = math.sin(x * 0.001 + t) * 100
                wave2 = math.sin(x * 0.0025 - t * 0.4) * 40
                y = y_base + wave1 + wave2
                points.append(QPointF(x, y))

            # Aurora colors: mostly greens and teals (120-200 in HSV)
            hue = (140 + i * 25 + int(math.sin(phase * 0.5) * 20)) % 360
            base_color = QColor.fromHsv(hue, 230, 255)
            
            for j in range(len(points) - 1):
                p1 = points[j]
                
                # Dynamic beam height
                beam_h = 300 + math.sin(j * 0.3 + t) * 120
                grad = QLinearGradient(p1.x(), p1.y() - beam_h, p1.x(), p1.y())
                
                # Richer gradient with higher opacity
                alpha_main = 80 + i * 10
                grad.setColorAt(0, QColor(base_color.red(), base_color.green(), base_color.blue(), 0))
                grad.setColorAt(0.4, QColor(base_color.red(), base_color.green(), base_color.blue(), alpha_main))
                grad.setColorAt(1, QColor(base_color.red(), base_color.green(), base_color.blue(), 0))
                
                p.setPen(QPen(QBrush(grad), w/steps + 5, Qt.SolidLine, Qt.FlatCap))
                p.drawLine(p1, QPointF(p1.x(), p1.y() - beam_h))
