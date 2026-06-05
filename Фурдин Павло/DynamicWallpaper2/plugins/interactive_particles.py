import random
import math
import numpy as np
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QBrush, QCursor

from effects import BaseEffect

class InteractiveParticlesEffect(BaseEffect):
    EFFECT_NAME = "interactive_particles"

    def __init__(self):
        super().__init__()
        self.num_particles = 800
        # Arrays
        self.pos = None
        self.vel = None
        self.sizes = None
        self.colors = None # Stores hue
        
        self._init_particles()
        
    @classmethod
    def get_schema(cls):
        return {
            "count": {
                "type": "int",
                "min": 100,
                "max": 3000, # Increased limit
                "default": 800,
                "label": "Particle Count"
            }
        }

    def configure(self, config: dict):
        if 'count' in config:
            self.num_particles = int(config['count'])
            self._init_particles()

    def _init_particles(self):
        # Default area 1920x1080, will wrap anyway
        self.pos = np.random.rand(self.num_particles, 2).astype(np.float32)
        self.pos[:, 0] *= 1920
        self.pos[:, 1] *= 1080
        
        self.vel = np.random.uniform(-1, 1, (self.num_particles, 2)).astype(np.float32)
        self.sizes = np.random.uniform(2, 5, self.num_particles).astype(np.float32)
        self.colors = np.random.randint(100, 201, self.num_particles) # Hue 100-200

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        if self.pos is None or len(self.pos) != self.num_particles:
            self._init_particles()
            
        # 1. Background
        p.fillRect(0, 0, w, h, QColor(10, 15, 20))
        
        # 2. Physics & Interaction
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        mouse_active = (-100 < mx < w + 100) and (-100 < my < h + 100)
        
        # Update Position
        self.pos += self.vel
        
        # Friction
        self.vel *= 0.98
        
        # Mouse Interaction
        if mouse_active:
            # Vector to mouse
            # Reset target to mouse pos array broadcast
            target = np.array([mx, my], dtype=np.float32)
            diff = target - self.pos
            dist_sq = np.sum(diff**2, axis=1)
            
            # Mask for close particles (< 500px radius -> 250000)
            # Optimize: only sqrt where needed
            mask = dist_sq < 250000
            
            if np.any(mask):
                dist = np.sqrt(dist_sq[mask])
                # Avoid div by zero
                dist[dist < 1.0] = 1.0
                
                # Force: (1.0 - dist/500) * 0.5
                force_mag = (1.0 - dist / 500.0) * 0.5
                
                # Normalized Direction * Force
                # diff[mask] is (M, 2)
                # dist is (M,)
                force = (diff[mask] / dist[:, np.newaxis]) * force_mag[:, np.newaxis]
                
                # Apply force (+ optionally swirl?)
                # Just attraction for now
                self.vel[mask] += force
                
        # Drift (Speed Init)
        # If speed ~ 0, add random impulse
        # abs(vx) < 0.5 and abs(vy) < 0.5
        slow_mask = (np.abs(self.vel[:, 0]) < 0.5) & (np.abs(self.vel[:, 1]) < 0.5)
        if np.any(slow_mask):
            count = np.sum(slow_mask)
            self.vel[slow_mask] += np.random.uniform(-0.05, 0.05, (count, 2))
            
        # Bounds Wrap
        # Use modulo arithmetic for wrapping? 
        # But we need floating point modulo which fits to [0, w].
        # np.remainder is good.
        self.pos[:, 0] = np.remainder(self.pos[:, 0], w)
        self.pos[:, 1] = np.remainder(self.pos[:, 1], h)

        # 3. Draw
        p.setPen(Qt.NoPen)
        
        # Prepare alpha based on speed
        speed_sq = np.sum(self.vel**2, axis=1)
        speed = np.sqrt(speed_sq)
        alphas = np.clip(100 + speed * 20, 0, 255).astype(np.int32)
        
        # Mouse Glow Logic
        # If close to mouse (< 100px radius -> 10000), white color
        if mouse_active:
            # We already have dist_sq? calc it again or reuse if fully masked?
            # Re-calc simpler diff for drawing logic if needed or just use current pos
            diff_draw = np.array([mx, my], dtype=np.float32) - self.pos
            dist_sq_draw = np.sum(diff_draw**2, axis=1)
            glow_mask = dist_sq_draw < 10000
        else:
            glow_mask = np.zeros(self.num_particles, dtype=bool)

        # Optimized Loop
        # Still need loop for drawing (p.drawEllipse)
        
        # Pre-create connection pen if needed?
        # Drawing 3000 lines is heavy. Only draw if VERY close to mouse?
        
        for i in range(self.num_particles):
            # Color
            if glow_mask[i]:
                 col = QColor(255, 255, 255, 255)
            else:
                 col = QColor.fromHsv(int(self.colors[i]), 200, 255, int(alphas[i]))
            
            p.setBrush(col)
            x = int(self.pos[i, 0])
            y = int(self.pos[i, 1])
            s = int(self.sizes[i])
            p.drawEllipse(x, y, s, s)
            
            # Line connection (only for subset or if very close)
            # Doing this in loop for 100px radius is fine (~few particles)
            if glow_mask[i]:
                 # dist_sq_draw[i] known < 10000
                 strength = 1.0 - dist_sq_draw[i] / 10000.0
                 alpha_line = int(strength * 150)
                 p.setPen(QColor(255, 255, 255, alpha_line))
                 p.drawLine(x, y, mx, my)
                 p.setPen(Qt.NoPen)
