import random
import math
from PySide6.QtGui import QColor, QPen, QRadialGradient, QBrush
from PySide6.QtCore import Qt
from effects import BaseEffect

class FlowFieldEffect(BaseEffect):
    EFFECT_NAME = "flow"
    
    def __init__(self):
        super().__init__()
        self.particles = None
        self.grid_size = 30
        self.num_particles = 600

    def draw(self, p, w, h, phase):
        if self.particles is None:
            self.particles = []
            for _ in range(self.num_particles):
                self.particles.append({
                    'x': random.uniform(0, w),
                    'y': random.uniform(0, h),
                    'px': 0,
                    'py': 0,
                    'speed': random.uniform(1, 3),
                    'hue': random.uniform(0.4, 0.6),
                    'life': random.uniform(0.5, 1.0)
                })
            for pt in self.particles:
                pt['px'], pt['py'] = pt['x'], pt['y']

        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(5, 5, 10))

        for pt in self.particles:
            scale = 0.002
            t = phase * 2
            
            angle = (
                math.sin(pt['x'] * scale + t) * math.pi +
                math.cos(pt['y'] * scale - t * 0.5) * math.pi +
                math.sin((pt['x'] + pt['y']) * scale * 0.5 + t) * math.pi
            )
            
            pt['px'], pt['py'] = pt['x'], pt['y']
            pt['x'] += math.cos(angle) * pt['speed']
            pt['y'] += math.sin(angle) * pt['speed']
            
            if pt['x'] < 0 or pt['x'] > w or pt['y'] < 0 or pt['y'] > h:
                pt['x'] = random.uniform(0, w)
                pt['y'] = random.uniform(0, h)
                pt['px'], pt['py'] = pt['x'], pt['y']
                pt['life'] = 0
            
            pt['life'] += 0.01
            alpha_val = min(1.0, math.sin(pt['life'] * 0.5)) * 150
            alpha_f = max(0.0, min(1.0, alpha_val / 255.0))
            
            color = QColor.fromHsvF(max(0.0, min(1.0, pt['hue'])), 0.6, 1.0, alpha_f)
            # Use integer width for better performance
            p.setPen(QPen(color, 1, Qt.SolidLine, Qt.RoundCap))
            p.drawLine(int(pt['px']), int(pt['py']), int(pt['x']), int(pt['y']))
            
            pt['hue'] = (pt['hue'] + 0.0001) % 1.0

        # Removed expensive radial gradient overlay for performance
        # grad = QRadialGradient(w/2, h/2, max(w, h))
        # grad.setColorAt(0, Qt.transparent)
        # grad.setColorAt(1, QColor(0, 0, 0, 100))
        # if self.show_background:
        #    p.fillRect(0, 0, w, h, QBrush(grad))
