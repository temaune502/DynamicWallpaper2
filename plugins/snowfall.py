import random
import math
import numpy as np
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from effects import BaseEffect

class SnowfallEffect(BaseEffect):
    EFFECT_NAME = "snowfall"
    
    def __init__(self):
        super().__init__()
        self.count = 250
        self.speed_mult = 1.0
        self.pos = None # (N, 2)
        self.params = None # (N, 3) speed, size, drift
        self.opacities = None # (N,)
        self._init_flakes(1920, 1080)

    @classmethod
    def get_schema(cls):
        return {
            "count": {
                "type": "int",
                "min": 50,
                "max": 2000,
                "default": 250,
                "label": "Snowflake Count"
            },
            "speed": {
                "type": "float",
                "min": 0.1,
                "max": 3.0,
                "default": 1.0,
                "label": "Speed"
            }
        }

    def configure(self, config: dict):
        if 'count' in config:
            self.count = int(config['count'])
            self._init_flakes(1920, 1080)
        if 'speed' in config:
            self.speed_mult = float(config['speed'])

    def _init_flakes(self, w, h):
        self.pos = np.empty((self.count, 2), dtype=np.float32)
        self.pos[:, 0] = np.random.uniform(0, w, self.count)
        self.pos[:, 1] = np.random.uniform(-h, h, self.count)
        
        self.params = np.empty((self.count, 3), dtype=np.float32)
        self.params[:, 0] = np.random.uniform(1, 3, self.count) # speed
        self.params[:, 1] = np.random.uniform(2, 5, self.count) # size
        self.params[:, 2] = np.random.uniform(0.5, 1.5, self.count) # drift
        
        self.opacities = np.random.randint(100, 255, self.count).astype(np.int32)

    def draw(self, p, w, h, phase):
        if self.pos is None or len(self.pos) != self.count:
            self._init_flakes(w, h)

        p.setPen(Qt.NoPen)
        
        # Vectorized Update
        # y += speed * speed_mult
        self.pos[:, 1] += self.params[:, 0] * self.speed_mult
        
        # x += sin(phase * 2 + y * 0.01) * drift
        self.pos[:, 0] += np.sin(phase * 2 + self.pos[:, 1] * 0.01) * self.params[:, 2]
        
        # Reset if off screen
        reset_mask = self.pos[:, 1] > h
        if np.any(reset_mask):
            self.pos[reset_mask, 1] = -20
            self.pos[reset_mask, 0] = np.random.uniform(0, w, np.sum(reset_mask))

        # Draw
        # Loop for variable opacity and size (QPainter is the bottleneck now)
        # Optimized approach: Maybe bin by opacity? 
        # For now, standard loop is fine as logic is the heavy part usually.
        
        for i in range(self.count):
            size = int(self.params[i, 1])
            p.setBrush(QColor(255, 255, 255, int(self.opacities[i])))
            x = int(self.pos[i, 0])
            y = int(self.pos[i, 1])
            p.drawEllipse(x, y, size, size)
            
            # Subtle glow for larger flakes
            if size > 4:
                p.setBrush(QColor(255, 255, 255, 40))
                p.drawEllipse(x - 2, y - 2, size + 4, size + 4)
