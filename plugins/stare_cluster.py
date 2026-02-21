import math
import random
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QCursor

from effects import BaseEffect

class StareClusterEffect(BaseEffect):
    EFFECT_NAME = "stare_cluster"

    def __init__(self):
        super().__init__()
        self.num_eyes = 40
        self.speed = 2.0
        self.eyes = []
        self.cx = 960
        self.cy = 540
        self.vx = 2
        self.vy = 1.5
        self._init_cluster()

    def _init_cluster(self):
        self.eyes = []
        # Build cluster
        for _ in range(self.num_eyes):
            # Random offset from center
            dist = random.uniform(0, 100)
            angle = random.uniform(0, math.pi * 2)
            self.eyes.append({
                'ox': math.cos(angle) * dist, # Offset X
                'oy': math.sin(angle) * dist, # Offset Y
                'size': random.uniform(10, 30),
                'color_iris': QColor.fromHsv(random.randint(0, 360), 100, 200)
            })

    @classmethod
    def get_schema(cls):
        return {
            "count": {
                "type": "int",
                "min": 10,
                "max": 200,
                "default": 40,
                "label": "Eye Count"
            },
            "speed": {
                "type": "float",
                "min": 0.5,
                "max": 10.0,
                "default": 2.0,
                "label": "Drift Speed"
            }
        }

    def configure(self, config: dict):
        if 'count' in config:
            self.num_eyes = int(config['count'])
            self._init_cluster()
        if 'speed' in config:
            self.speed = float(config['speed'])
            # Reset velocity direction maintenance
            self.vx = self.speed if self.vx > 0 else -self.speed
            self.vy = (self.speed * 0.75) if self.vy > 0 else -(self.speed * 0.75)

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        p.fillRect(0, 0, w, h, QColor(30, 0, 0)) # Dark red/fleshy bg
        
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        
        # Move Cluster (Drift)
        self.cx += self.vx
        self.cy += self.vy
        
        margin = 150
        
        # Attraction/Repulsion to mouse (Stronger push)
        dx = self.cx - mx
        dy = self.cy - my
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < 400:
             # Move away strongly
             force = (400 - dist) / 400.0 * 5.0
             self.cx += (dx / dist) * force
             self.cy += (dy / dist) * force
        
        # Clamp & Bounce
        if self.cx < margin:
            self.cx = margin
            self.vx = abs(self.vx) # Bounce Right
        elif self.cx > w - margin:
            self.cx = w - margin
            self.vx = -abs(self.vx) # Bounce Left
            
        if self.cy < margin:
            self.cy = margin
            self.vy = abs(self.vy) # Bounce Down
        elif self.cy > h - margin:
            self.cy = h - margin
            self.vy = -abs(self.vy) # Bounce Up
        
        # Draw connections (Fleshy bits)
        p.setPen(QPen(QColor(100, 50, 50), 5))
        for i in range(len(self.eyes) - 1):
            e1 = self.eyes[i]
            e2 = self.eyes[i+1]
            p.drawLine(QPointF(self.cx + e1['ox'], self.cy + e1['oy']), 
                       QPointF(self.cx + e2['ox'], self.cy + e2['oy']))
        
        p.setPen(Qt.NoPen)
        
        # Draw Eyes
        for eye in self.eyes:
            ex = self.cx + eye['ox']
            ey = self.cy + eye['oy']
            size = eye['size']
            
            # Sclera
            p.setBrush(QColor(255, 230, 230)) # Bloodshot white
            p.drawEllipse(QPointF(ex, ey), size, size)
            
            # Pupil Tracking
            dx = mx - ex
            dy = my - ey
            dist = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx)
            
            limit = size * 0.5
            pupil_dist = min(dist, limit)
            
            px = ex + math.cos(angle) * pupil_dist
            py = ey + math.sin(angle) * pupil_dist
            
            # Iris
            p.setBrush(eye['color_iris'])
            p.drawEllipse(QPointF(px, py), size * 0.5, size * 0.5)
            
            # Pupil
            p.setBrush(QColor(0, 0, 0))
            p.drawEllipse(QPointF(px, py), size * 0.25, size * 0.25)
            
            # Highlight
            p.setBrush(QColor(255, 255, 255, 200))
            p.drawEllipse(QPointF(px - size*0.1, py - size*0.1), size * 0.1, size * 0.1)
