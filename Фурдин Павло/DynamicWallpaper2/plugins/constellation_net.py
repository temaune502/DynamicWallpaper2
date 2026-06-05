import math
import random
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QCursor

from effects import BaseEffect

class ConstellationNetEffect(BaseEffect):
    EFFECT_NAME = "constellation_net"

    def __init__(self):
        super().__init__()
        self.num_points = 100
        self.color_hue_min = 180
        self.color_hue_max = 240
        self.points = []
        self._init_points()

        self.hue_max = 60
        self.points = []
        self._init_points()

    @classmethod
    def get_schema(cls):
        return {
            "points": {
                "type": "int",
                "min": 50,
                "max": 300,
                "default": 150,
                "label": "Point Count"
            },
            "hue_min": {
                "type": "int",
                "min": 0,
                "max": 360,
                "default": 0,
                "label": "Hue Min"
            },
            "hue_max": {
                "type": "int",
                "min": 0,
                "max": 360,
                "default": 60,
                "label": "Hue Max"
            }
        }

    def configure(self, config: dict):
        if 'points' in config: self.num_points = int(config['points'])
        if 'hue_min' in config: self.color_hue_min = int(config['hue_min'])
        if 'hue_max' in config: self.color_hue_max = int(config['hue_max'])
        
        # Re-init if points changed or just re-color? 
        # Easier to re-init for points count.
        if 'points' in config or 'hue_min' in config or 'hue_max' in config:
             self._init_points()

    def _init_points(self):
        self.points = []
        for _ in range(self.num_points):
            self.points.append(self._create_point())

    def _create_point(self):
        return {
            'x': random.uniform(0, 1920),
            'y': random.uniform(0, 1080),
            'vx': random.uniform(-1, 1),
            'vy': random.uniform(-1, 1),
            'size': random.uniform(2, 4),
            'color': QColor.fromHsv(random.randint(self.color_hue_min, self.color_hue_max), 100, 255) 
        }

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(10, 10, 15))
        
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        
        # Interaction radius
        mouse_rad_sq = 200 * 200
        
        # Connection distance
        conn_dist_sq = 150 * 150
        
        # Update Points
        for pt in self.points:
            pt['x'] += pt['vx']
            pt['y'] += pt['vy']
            
            # Bounce
            if pt['x'] < 0 or pt['x'] > w: pt['vx'] *= -1
            if pt['y'] < 0 or pt['y'] > h: pt['vy'] *= -1
            
            # Clamp
            pt['x'] = max(0, min(w, pt['x']))
            pt['y'] = max(0, min(h, pt['y']))
            
            # Mouse Interaction (Repel/Attract)
            dx = pt['x'] - mx
            dy = pt['y'] - my
            dist_sq = dx*dx + dy*dy
            
            if dist_sq < mouse_rad_sq:
                # Push away softly
                dist = math.sqrt(dist_sq)
                if dist < 1: dist = 1
                force = (200 - dist) / 200.0 * 2.0
                
                angle = math.atan2(dy, dx)
                pt['x'] += math.cos(angle) * force
                pt['y'] += math.sin(angle) * force
        
        # Draw Lines and Points
        p.setBrush(QBrush(QColor(255, 255, 255)))
        
        # We need a classic O(N^2) loop? For 100 points it's fine (10,000 checks).
        # Optimization: Spatial hashing if N > 500.
        
        for i in range(self.num_points):
            pt1 = self.points[i]
            
            # Draw Point
            p.setPen(Qt.NoPen)
            p.setBrush(pt1['color'])
            p.drawEllipse(QPointF(pt1['x'], pt1['y']), pt1['size'], pt1['size'])
            
            # Connections
            for j in range(i + 1, self.num_points):
                pt2 = self.points[j]
                
                dx = pt1['x'] - pt2['x']
                dy = pt1['y'] - pt2['y']
                dist_sq = dx*dx + dy*dy
                
                if dist_sq < conn_dist_sq:
                    # Alpha based on distance
                    alpha = int(255 * (1 - dist_sq / conn_dist_sq))
                    pen_col = QColor(pt1['color'])
                    pen_col.setAlpha(alpha)
                    
                    p.setPen(QPen(pen_col, 1))
                    p.drawLine(QPointF(pt1['x'], pt1['y']), QPointF(pt2['x'], pt2['y']))
