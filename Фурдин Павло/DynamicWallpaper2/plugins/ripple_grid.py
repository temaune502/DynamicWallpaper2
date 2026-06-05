import math
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QCursor, QPen

from effects import BaseEffect

class RippleGridEffect(BaseEffect):
    EFFECT_NAME = "ripple_grid"

    def __init__(self):
        super().__init__()
        self.spacing = 40
        self.color_grid = (0, 150, 255)
        self.rows = 0
        self.cols = 0
        
        self.rows = 0
        self.cols = 0
        
    @classmethod
    def get_schema(cls):
        return {
            "spacing": {
                "type": "int",
                "min": 20,
                "max": 100,
                "default": 40,
                "label": "Grid Spacing"
            },
            "color": {
                "type": "color",
                "default": (0, 150, 255),
                "label": "Grid Color"
            }
        }

    def configure(self, config: dict):
        if 'spacing' in config: self.spacing = int(config['spacing'])
        if 'color' in config: self.color_grid = tuple(config['color'])
        
    def draw(self, p: QPainter, w: int, h: int, phase: float):
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(5, 5, 10))
        
        self.cols = w // self.spacing + 2
        self.rows = h // self.spacing + 2
        
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        
        p.setPen(QPen(QColor(*self.color_grid), 1))
        
        # Horizontal lines
        for r in range(self.rows):
            path_points = []
            for c in range(self.cols):
                x = c * self.spacing
                y = r * self.spacing
                
                # Ripple Math
                dx = x - mx
                dy = y - my
                dist = math.sqrt(dx*dx + dy*dy)
                
                # Wave function
                # Amp decays with distance
                amp = 100 * math.exp(-dist * 0.005)
                z = math.sin(dist * 0.05 - phase * 10) * amp
                
                # Project 3D to 2D (Isometric-ish)
                # Just offset Y by Z
                draw_y = y - z
                
                path_points.append(QPointF(x, draw_y))
                
            # Draw line strip
            if len(path_points) > 1:
                for i in range(len(path_points) - 1):
                    p.drawLine(path_points[i], path_points[i+1])
                    
        # Vertical lines (Optional, for grid look)
        c = QColor(*self.color_grid)
        c.setAlpha(100)
        p.setPen(QPen(c, 1))
        for c in range(self.cols):
             path_points = []
             for r in range(self.rows):
                x = c * self.spacing
                y = r * self.spacing
                
                dx = x - mx
                dy = y - my
                dist = math.sqrt(dx*dx + dy*dy)
                
                amp = 100 * math.exp(-dist * 0.005)
                z = math.sin(dist * 0.05 - phase * 10) * amp
                
                draw_y = y - z
                path_points.append(QPointF(x, draw_y))

             if len(path_points) > 1:
                for i in range(len(path_points) - 1):
                    p.drawLine(path_points[i], path_points[i+1])
