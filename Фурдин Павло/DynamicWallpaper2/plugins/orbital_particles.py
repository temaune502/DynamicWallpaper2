import random
import math
from PySide6.QtGui import QColor, QLinearGradient, QBrush
from PySide6.QtCore import Qt
from effects import BaseEffect

class OrbitalParticlesEffect(BaseEffect):
    EFFECT_NAME = "orbital"
    
    def __init__(self):
        super().__init__()
        self.particles = None

    def draw(self, p, w, h, phase):
        if self.particles is None:
            self.particles = []
            for _ in range(50):
                self.particles.append({
                    'orbit': random.uniform(50, w//3),
                    'speed': random.uniform(0.5, 2.0),
                    'size': random.uniform(2, 6),
                    'color': QColor(random.randint(100, 255), random.randint(150, 255), 255, 180),
                    'offset': random.uniform(0, math.pi * 2)
                })

        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(10, 10, 15))
        cx, cy = w // 2, h // 2
        
        # Center glow
        grad = QLinearGradient(cx - 100, cy - 100, cx + 100, cy + 100)
        grad.setColorAt(0, QColor(255, 255, 255, 50))
        grad.setColorAt(1, QColor(0, 100, 255, 0))
        p.setBrush(QBrush(grad))
        p.setPen(Qt.NoPen)
        p.drawEllipse(cx - 100, cy - 100, 200, 200)

        for part in self.particles:
            angle = phase * 5 * part['speed'] + part['offset']
            rx = part['orbit'] * math.cos(angle)
            ry = (part['orbit'] * 0.6) * math.sin(angle) # Elliptical
            
            # Perspective effect
            z = math.sin(angle)
            scale = 0.5 + 0.5 * z
            current_size = part['size'] * scale
            
            x = cx + rx
            y = cy + ry
            
            p.setBrush(part['color'])
            p.drawEllipse(int(x - current_size/2), int(y - current_size/2), int(current_size), int(current_size))
