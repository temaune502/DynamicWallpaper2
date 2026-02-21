import math
import random
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QCursor, QBrush, QPen

from effects import BaseEffect

class WatcherEyesEffect(BaseEffect):
    EFFECT_NAME = "watcher_eyes"

    def __init__(self):
        super().__init__()
        self.rows = 10
        self.cols = 16
        self.eyes = []
        self._init_eyes()
        
    def _init_eyes(self):
        self.eyes = []
        # Assume 1920x1080 default scaling if w/h unknown, but typically we 
        # should defer or just use fixed grid.
        # Let's use generic spacing and map later? No, fixed grid is easier.
        spacing_x = 1920 / self.cols
        spacing_y = 1080 / self.rows
        
        for r in range(self.rows):
            for c in range(self.cols):
                self.eyes.append({
                    'x': c * spacing_x + spacing_x/2,
                    'y': r * spacing_y + spacing_y/2,
                    'size': min(spacing_x, spacing_y) * 0.4
                })

    @classmethod
    def get_schema(cls):
        return {
            "rows": {
                "type": "int",
                "min": 2,
                "max": 30,
                "default": 10,
                "label": "Rows"
            },
            "cols": {
                "type": "int",
                "min": 2,
                "max": 40,
                "default": 16,
                "label": "Columns"
            }
        }

    def configure(self, config: dict):
        if 'rows' in config: self.rows = int(config['rows'])
        if 'cols' in config: self.cols = int(config['cols'])
        self._init_eyes()

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        p.fillRect(0, 0, w, h, QColor(20, 20, 25))
        
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        
        p.setPen(QPen(QColor(0, 0, 0), 2))
        
        for eye in self.eyes:
            ex, ey = eye['x'], eye['y']
            size = eye['size']
            
            # Draw Sclera (White)
            p.setBrush(QColor(240, 240, 240))
            p.drawEllipse(QPointF(ex, ey), size, size)
            
            # Pupil Calculation
            dx = mx - ex
            dy = my - ey
            angle = math.atan2(dy, dx)
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Pupil limit
            limit = size * 0.6
            pupil_dist = min(dist, limit)
            
            px = ex + math.cos(angle) * pupil_dist
            py = ey + math.sin(angle) * pupil_dist
            
            # Draw Pupil
            p.setBrush(QColor(0, 0, 0))
            p.drawEllipse(QPointF(px, py), size * 0.4, size * 0.4)
            
            # Specular highlight (optional)
            p.setBrush(QColor(255, 255, 255))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(px - size*0.1, py - size*0.1), size*0.1, size*0.1)
            p.setPen(QPen(QColor(0, 0, 0), 2))
