import math
import random
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF
from effects import BaseEffect

class CyberHexagonsEffect(BaseEffect):
    EFFECT_NAME = "cyber_hexagons"

    def __init__(self):
        super().__init__()
        self.hex_size = 40
        self.cells = {}
        
    def _get_hex_points(self, cx, cy, size):
        points = []
        for i in range(6):
            angle_deg = 60 * i + 30
            angle_rad = math.radians(angle_deg)
            points.append(QPointF(cx + size * math.cos(angle_rad),
                                  cy + size * math.sin(angle_rad)))
        return points

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        p.fillRect(0, 0, w, h, QColor(10, 10, 15))
        
        # Hexagon grid calculations
        # Horiz spacing: size * sqrt(3)
        # Vert spacing: size * 1.5
        
        dx = self.hex_size * math.sqrt(3)
        dy = self.hex_size * 1.5
        
        cols = int(w / dx) + 2
        rows = int(h / dy) + 2
        
        offset_y = (phase * 60) % dy # Scroll slightly? No, let's just pulse
        
        for r in range(rows):
            for c in range(cols):
                cx = c * dx
                cy = r * dy
                if r % 2 == 1:
                    cx += dx / 2
                    
                # Visual logic
                # Pulse based on distance from center + phase
                center_dist = math.sqrt((cx - w/2)**2 + (cy - h/2)**2)
                pulse = math.sin(center_dist * 0.01 - phase * 5)
                
                # Active cell?
                key = f"{r},{c}"
                if key not in self.cells:
                     # Random "life" props
                     self.cells[key] = random.random()
                
                # Logic: wave lighting
                brightness = max(0, pulse)
                
                alpha = int(brightness * 200) + 20
                
                if alpha > 40:
                    pen_col = QColor(0, 255, 255, alpha)
                    brush_col = QColor(0, 255, 255, int(alpha * 0.2))
                    
                    p.setPen(QPen(pen_col, 2))
                    p.setBrush(brush_col)
                    
                    poly = QPolygonF(self._get_hex_points(cx, cy, self.hex_size - 2))
                    p.drawPolygon(poly)
