import math
import random
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QPen, QBrush

from effects import BaseEffect

class KaleidoscopeEffect(BaseEffect):
    EFFECT_NAME = "kaleidoscope"

    def __init__(self):
        super().__init__()
        self.shapes = []
        for _ in range(20):
            self.shapes.append({
                'r': random.uniform(0.1, 0.9), # radius normalized (0 center, 1 edge)
                'theta': random.uniform(0, math.pi / 4), # angle within slice
                'size': random.uniform(0.05, 0.15),
                'color': QColor.fromHsv(random.randint(0, 360), 200, 255, 180),
                'speed_r': random.uniform(-0.005, 0.005),
                'speed_th': random.uniform(-0.01, 0.01),
                'type': random.choice(['circle', 'rect'])
            })

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        cx, cy = w / 2, h / 2
        radius = math.sqrt(w*w + h*h) / 2
        
        p.fillRect(0, 0, w, h, QColor(10, 10, 10))
        
        # We draw into 8 slices (45 degrees each)
        slices = 8
        slice_angle = 360 / slices
        
        p.setPen(Qt.NoPen)
        
        # Update shapes
        for s in self.shapes:
            s['r'] += s['speed_r']
            if s['r'] > 1.0 or s['r'] < 0.1: s['speed_r'] *= -1
            
            s['theta'] += s['speed_th']
            
            # Keep theta within slice logic? 
            # Actually, let's just rotate the whole canvas
            
        # Draw all shapes in one loop, replicated
        for i in range(slices):
            p.save()
            p.translate(cx, cy)
            p.rotate(i * slice_angle + phase * 20) # Rotate smoothly
            
            # Mirror every other slice for true kaleidoscope
            if i % 2 == 1:
                p.scale(1, -1) # Flip Y
            
            for s in self.shapes:
                # Polar to Cartesian
                curr_r = s['r'] * radius
                curr_th = s['theta'] + phase # Animate angle
                
                x = curr_r * math.cos(curr_th)
                y = curr_r * math.sin(curr_th)
                
                size = s['size'] * radius
                
                p.setBrush(s['color'])
                if s['type'] == 'circle':
                    p.drawEllipse(QPointF(x, y), size, size)
                else:
                    p.drawRect(x - size/2, y - size/2, size, size)
                    
            p.restore()
