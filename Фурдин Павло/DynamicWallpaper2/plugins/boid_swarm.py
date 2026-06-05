import random
import math
import numpy as np
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QCursor, QPolygonF

from effects import BaseEffect

class BoidSwarmEffect(BaseEffect):
    EFFECT_NAME = "boid_swarm"

    def __init__(self):
        super().__init__()
        self.num_boids = 100
        self.color_hue_min = 150
        self.color_hue_max = 250
        
        # Arrays
        self.pos = None # (N, 2)
        self.vel = None # (N, 2)
        self.colors = None # (N,) hue values
        
        self._init_boids()
        
    @classmethod
    def get_schema(cls):
        return {
            "count": {
                "type": "int",
                "min": 50,
                "max": 2000, # Increased max due to optimization
                "default": 100,
                "label": "Boid Count"
            },
            "hue_min": {
                "type": "int",
                "min": 0,
                "max": 360,
                "default": 150,
                "label": "Hue Min"
            },
            "hue_max": {
                "type": "int",
                "min": 0,
                "max": 360,
                "default": 250,
                "label": "Hue Max"
            }
        }

    def configure(self, config: dict):
        if 'count' in config: self.num_boids = int(config['count'])
        if 'hue_min' in config: self.color_hue_min = int(config['hue_min'])
        if 'hue_max' in config: self.color_hue_max = int(config['hue_max'])
        
        if 'count' in config:
            self._init_boids()

    def _init_boids(self):
        # Initialize arrays
        self.pos = np.random.rand(self.num_boids, 2).astype(np.float32)
        self.pos[:, 0] *= 1920
        self.pos[:, 1] *= 1080
        
        self.vel = np.random.uniform(-2, 2, (self.num_boids, 2)).astype(np.float32)
        self.colors = np.random.randint(self.color_hue_min, self.color_hue_max + 1, self.num_boids)

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(10, 20, 30))
        
        if self.pos is None or len(self.pos) != self.num_boids:
            self._init_boids()
            
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        mouse_target = np.array([mx, my], dtype=np.float32)
        
        # --- Vectorized Logic ---
        
        # 1. Attraction to mouse
        # vector to mouse = mouse - pos
        diff = mouse_target - self.pos # (N, 2)
        dist_sq = np.sum(diff**2, axis=1) # (N,)
        dist = np.sqrt(dist_sq)
        
        # Avoid division by zero
        mask = dist > 0
        
        # Update velocity (attraction)
        # Boids move towards mouse. Factor 0.5 is strength.
        # Check shapes: diff[mask] is (M, 2), dist[mask] is (M,) -> reshape to (M, 1)
        force = (diff[mask] / dist[mask][:, np.newaxis]) * 0.5
        self.vel[mask] += force
                
        # 2. Speed Limit
        speed_sq = np.sum(self.vel**2, axis=1)
        speed = np.sqrt(speed_sq)
        
        max_speed = 6.0
        fast_mask = speed > max_speed
        
        # Normalize and scale to max_speed
        if np.any(fast_mask):
            self.vel[fast_mask] = (self.vel[fast_mask] / speed[fast_mask][:, np.newaxis]) * max_speed
            
        # 3. Move
        self.pos += self.vel
        
        # 4. Draw
        p.setPen(Qt.NoPen)
        
        # Pre-calculate angles for drawing
        angles = np.arctan2(self.vel[:, 1], self.vel[:, 0])
        
        # We can't vectorized QPainter calls easily without OpenGL, 
        # but we can loop faster over numpy arrays.
        
        # To optimize drawing, we construct polygons in local space and map them?
        # Or just loop. Loop is fine for < 2000 in Python if logic is offset.
        
        # Cache polygon shape
        poly_points = [QPointF(10, 0), QPointF(-5, 5), QPointF(-5, -5)]
        base_poly = QPolygonF(poly_points)
        
        for i in range(self.num_boids):
            p.save()
            p.translate(float(self.pos[i, 0]), float(self.pos[i, 1]))
            p.rotate(math.degrees(angles[i]))
            
            p.setBrush(QColor.fromHsv(int(self.colors[i]), 200, 255))
            p.drawPolygon(base_poly)
            p.restore()
