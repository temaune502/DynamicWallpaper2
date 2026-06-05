import random
import math
from PySide6.QtGui import QColor, QPen
from PySide6.QtCore import Qt
from effects import BaseEffect

class FractalWebEffect(BaseEffect):
    EFFECT_NAME = "fractal_web"
    
    def __init__(self):
        super().__init__()
        self.nodes = None

    def draw(self, p, w, h, phase):
        if self.nodes is None:
            self.nodes = []
            for _ in range(60):
                self.nodes.append({
                    'x': random.uniform(0, w),
                    'y': random.uniform(0, h),
                    'vx': random.uniform(-1, 1),
                    'vy': random.uniform(-1, 1)
                })

        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(5, 5, 10))
        
        # Update and draw nodes
        for node in self.nodes:
            node['x'] = (node['x'] + node['vx']) % w
            node['y'] = (node['y'] + node['vy']) % h
            
            # Find neighbors
            for other in self.nodes:
                dist = math.hypot(node['x'] - other['x'], node['y'] - other['y'])
                if dist < 150:
                    alpha = int(255 * (1 - dist / 150))
                    p.setPen(QPen(QColor(0, 200, 255, alpha), 1))
                    p.drawLine(int(node['x']), int(node['y']), int(other['x']), int(other['y']))

        for node in self.nodes:
            p.setBrush(QColor(255, 255, 255, 200))
            p.setPen(Qt.NoPen)
            p.drawEllipse(int(node['x'] - 2), int(node['y'] - 2), 4, 4)
