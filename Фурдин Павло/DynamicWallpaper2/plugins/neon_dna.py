import math
from PySide6.QtGui import QColor, QPen
from PySide6.QtCore import Qt
from effects import BaseEffect

class NeonDNAEffect(BaseEffect):
    EFFECT_NAME = "neon_dna"
    
    def draw(self, p, w, h, phase):
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(0, 0, 0))
        
        num_points = 40
        spacing = h // num_points
        center_x = w // 2
        amplitude = w // 4
        
        for i in range(num_points):
            y = i * spacing + (phase * spacing * 10) % spacing
            t = phase * 5 + i * 0.3
            
            x1 = center_x + math.sin(t) * amplitude
            x2 = center_x + math.sin(t + math.pi) * amplitude
            
            # Draw connecting line
            p.setPen(QPen(QColor(100, 100, 255, 50), 1))
            p.drawLine(int(x1), int(y), int(x2), int(y))
            
            # Draw points
            size = 8 + math.cos(t) * 4
            p.setPen(Qt.NoPen)
            
            # Point 1
            p.setBrush(QColor(0, 255, 255, 200))
            p.drawEllipse(int(x1 - size/2), int(y - size/2), int(size), int(size))
            
            # Point 2
            p.setBrush(QColor(255, 0, 255, 200))
            p.drawEllipse(int(x2 - size/2), int(y - size/2), int(size), int(size))
