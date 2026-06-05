import math
from PySide6.QtGui import QColor, QLinearGradient, QBrush, QPolygon, QPen
from PySide6.QtCore import Qt, QPoint
from effects import BaseEffect

class LiquidSilkEffect(BaseEffect):
    EFFECT_NAME = "silk"
    
    def draw(self, p, w, h, phase):
        # Base deep background
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(10, 5, 20))
        
        # We draw several overlapping layers of "silk" waves
        num_layers = 4
        for i in range(num_layers):
            t = phase * 0.3 + i * (math.pi * 2 / num_layers)
            
            # Create a complex gradient for each layer
            grad = QLinearGradient(0, 0, w, h)
            
            # Shifting hues for a "pearlescent" effect
            hue1 = (int(phase * 20) + i * 40) % 360
            hue2 = (hue1 + 60) % 360
            
            c1 = QColor.fromHsv(hue1, 180, 255, 40)
            c2 = QColor.fromHsv(hue2, 200, 255, 40)
            
            grad.setColorAt(0, c1)
            grad.setColorAt(0.5, c2)
            grad.setColorAt(1, c1)
            
            p.setBrush(QBrush(grad))
            p.setPen(Qt.NoPen)
            
            # Draw the "silk" wave path
            path = []
            steps = 20
            dx = w / steps
            
            # Top boundary
            for x_step in range(steps + 1):
                x = x_step * dx
                y_off = (
                    math.sin(x * 0.002 + t) * 150 +
                    math.sin(x * 0.005 - t * 1.5) * 80 +
                    math.sin(x * 0.001 + t * 0.5) * 50
                )
                y = h // 2 + y_off
                path.append((int(x), int(y)))
            
            # Bottom boundary
            bottom_path = []
            for x_step in range(steps, -1, -1):
                x = x_step * dx
                y_off = (
                    math.sin(x * 0.002 + t + 0.5) * 180 +
                    math.sin(x * 0.004 - t * 1.2) * 100
                )
                y = h // 2 + y_off + 200
                bottom_path.append((int(x), int(y)))
            
            all_pts = path + bottom_path
            poly = QPolygon([QPoint(pt[0], pt[1]) for pt in all_pts])
            p.drawPolygon(poly)
            
            # Highlight line
            p.setPen(QPen(QColor(255, 255, 255, 30), 2))
            for j in range(len(path) - 1):
                p.drawLine(path[j][0], path[j][1], path[j+1][0], path[j+1][1])
