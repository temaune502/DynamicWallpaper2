import math
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QCursor, QBrush

from effects import BaseEffect

class MagneticGridEffect(BaseEffect):
    EFFECT_NAME = "magnetic_grid"

    def __init__(self):
        super().__init__()
        self.rows = 20
        self.cols = 30
        self.spacing = 60
        self.points = []
        
        # Initialize grid
        for r in range(self.rows):
            for c in range(self.cols):
                self.points.append({
                    'ox': c * self.spacing + 30, # Original X
                    'oy': r * self.spacing + 30, # Original Y
                    'x': c * self.spacing + 30,
                    'y': r * self.spacing + 30,
                    'vx': 0,
                    'vy': 0
                })

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        p.fillRect(0, 0, w, h, QColor(10, 10, 15))
        
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        
        p.setPen(Qt.NoPen)
        
        range_sq = 200 * 200 # Interaction radius
        
        for pt in self.points:
            # Physics: Spring force to original pos
            dx_o = pt['ox'] - pt['x']
            dy_o = pt['oy'] - pt['y']
            
            pt['vx'] += dx_o * 0.05
            pt['vy'] += dy_o * 0.05
            
            # Physics: Repulsion from mouse
            dx_m = pt['x'] - mx
            dy_m = pt['y'] - my
            dist_sq = dx_m*dx_m + dy_m*dy_m
            
            if dist_sq < range_sq and dist_sq > 1:
                dist = math.sqrt(dist_sq)
                force = (200 - dist) / 200.0
                
                angle = math.atan2(dy_m, dx_m)
                push = force * 5.0
                
                pt['vx'] += math.cos(angle) * push
                pt['vy'] += math.sin(angle) * push
            
            # Damping
            pt['vx'] *= 0.85
            pt['vy'] *= 0.85
            
            pt['x'] += pt['vx']
            pt['y'] += pt['vy']
            
            # Draw
            # Color based on displacement
            disp = math.sqrt(dx_o**2 + dy_o**2)
            hue = (0.6 + disp * 0.005) % 1.0
            
            size = 4 + disp * 0.1
            
            col = QColor.fromHsvF(hue, 0.8, 1.0, 0.8)
            p.setBrush(col)
            p.drawEllipse(QPointF(pt['x'], pt['y']), size, size)
