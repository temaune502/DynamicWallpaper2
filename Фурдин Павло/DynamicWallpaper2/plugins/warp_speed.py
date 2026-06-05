import random
import math
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QPen

from effects import BaseEffect

class WarpSpeedEffect(BaseEffect):
    EFFECT_NAME = "warp_speed"

    def __init__(self):
        super().__init__()
        self.num_stars = 500
        self.base_speed = 20.0
        self.warp_factor = 2.0
        self.speed_base = 60.0
        
        self._init_stars()

    def _init_stars(self):
        self.stars = []
        for _ in range(self.num_stars):
            self.stars.append(self._create_star())

    @classmethod
    def get_schema(cls):
        return {
            "stars": {
                "type": "int",
                "min": 100,
                "max": 2000,
                "default": 800,
                "label": "Star Count"
            },
            "speed": {
                "type": "float",
                "min": 10.0,
                "max": 200.0,
                "default": 60.0,
                "label": "Warp Speed"
            }
        }

    def configure(self, config: dict):
        if 'stars' in config:
            self.num_stars = int(config['stars'])
            # Re-init
            self.stars = []
            for _ in range(self.num_stars):
                self.stars.append(self._create_star())
                
        if 'speed' in config: self.base_speed = float(config['speed'])

    def _create_star(self):
        # Spawn randomly in pseudo-3D space
        # x, y are -1 to 1
        return {
            'x': random.uniform(-1, 1) * 1000,
            'y': random.uniform(-1, 1) * 1000,
            'z': random.uniform(10, 1000), # distance
            'pz': 0 # Previous Z for trail
        }

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(0, 0, 0))
        
        cx, cy = w / 2, h / 2
        
        # Speed modulation
        speed = self.base_speed + math.sin(phase * 2) * (self.base_speed * 0.5)
        
        for s in self.stars:
            s['pz'] = s['z']
            s['z'] -= speed
            
            # Reset if behind camera
            if s['z'] <= 1:
                s['z'] = 1000
                s['pz'] = 1000
                s['x'] = random.uniform(-1, 1) * 1000
                s['y'] = random.uniform(-1, 1) * 1000
                
            # Project 3D to 2D
            k = 128.0 / s['z']
            px = s['x'] * k + cx
            py = s['y'] * k + cy
            
            # Previous position for trail
            pk = 128.0 / s['pz']
            ppx = s['x'] * pk + cx
            ppy = s['y'] * pk + cy
            
            # Determine brightness/color based on Z
            # Nearby = brighter
            b = int(255 * (1 - s['z'] / 1000.0))
            if b < 0: b = 0
            if b > 255: b = 255
            
            # Color shift based on speed?
            # Blue shift!
            col = QColor(b, b, 255)
            
            # Draw trail
            if s['z'] < 900: # Don't draw if just spawned
                p.setPen(QPen(col, 2))
                p.drawLine(QPointF(ppx, ppy), QPointF(px, py))
                
        # Draw central glow
        # p.setPen(Qt.NoPen)
        # p.setBrush(QColor(255, 255, 255, 5))
        # p.drawEllipse(QPointF(cx, cy), 50, 50)
