import math
import random
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QPen, QRadialGradient, QBrush

from effects import BaseEffect

class HyperspaceEffect(BaseEffect):
    EFFECT_NAME = "hyperspace"

    def __init__(self):
        super().__init__()
        self.stars = []
        self.num_stars = 300
        self.speed = 10.0
        # Initialize stars
        for _ in range(self.num_stars):
            self._add_star(random_z=True)

    def _add_star(self, random_z=False):
        # 3D coordinates: x, y in range [-width, width], z in range [1, depth]
        # We simulate a "box" tunnel
        spread = 2000
        x = random.uniform(-spread, spread)
        y = random.uniform(-spread, spread)
        z = random.uniform(1, 2000) if random_z else 2000
        
        self.stars.append({
            'x': x,
            'y': y,
            'z': z,
            'pz': z, # Previous z for trail
            'color_hue': random.randint(200, 280) # Blue-Purple range
        })

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        cx, cy = w / 2, h / 2
        
        # 1. Background with subtle gradient (Central Nebula)
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(0, 0, 10))
            
            grad = QRadialGradient(cx, cy, max(w, h))
            grad.setColorAt(0, QColor(20, 0, 50, 100))
            grad.setColorAt(0.5, QColor(0, 0, 20, 50))
            grad.setColorAt(1, QColor(0, 0, 10, 0))
            p.setBrush(QBrush(grad))
            p.setPen(Qt.NoPen)
            p.drawRect(0, 0, w, h)
        
        # 2. Update and Draw Stars
        finished_stars = []
        
        # Speed modulation (pulse)
        current_speed = self.speed + math.sin(phase * 2) * 2.0
        
        for star in self.stars:
            star['pz'] = star['z']
            star['z'] -= current_speed
            
            # Reset if behind camera
            if star['z'] <= 1:
                # Reuse star object to avoid alloc churn? Or just re-add
                self._add_star()
                continue
                
            finished_stars.append(star)
            
            # Perspective Projection
            # sx = x / z * scale
            fov = 500
            
            sx = (star['x'] / star['z']) * fov + cx
            sy = (star['y'] / star['z']) * fov + cy
            
            # Previous position for streak
            # We can use pz, but if speed is high, pz might be far.
            # To make smooth streaks, we can calculate where it WAS slightly before
            
            psx = (star['x'] / star['pz']) * fov + cx
            psy = (star['y'] / star['pz']) * fov + cy
            
            # Check bounds to avoid drawing massive lines across screen when near 0
            if not (-100 < sx < w+100 and -100 < sy < h+100):
                continue
                
            dist_ratio = 1.0 - (star['z'] / 2000.0) # 0 (far) to 1 (close)
            
            # Size and Opacity
            size = max(1.0, dist_ratio * 4.0)
            alpha = int(dist_ratio * 255)
            
            color = QColor.fromHsv(star['color_hue'], 150, 255)
            color.setAlpha(alpha)
            
            pen = QPen(color)
            pen.setWidthF(size)
            p.setPen(pen)
            
            # Draw streak
            p.drawLine(QPointF(psx, psy), QPointF(sx, sy))
            
        self.stars = finished_stars
