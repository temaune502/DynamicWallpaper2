import random
import numpy as np
from PySide6.QtGui import QColor, QPen
from PySide6.QtCore import Qt
from effects import BaseEffect

class RainEffect(BaseEffect):
    EFFECT_NAME = "rain"
    
    def __init__(self):
        super().__init__()
        self.drop_count = 400
        self.speed_mult = 1.0
        self.pos = None # (N, 2) x, y
        self.params = None # (N, 3) speed, length, z(depth)
        self.opacities = None # (N,)
        self._init_drops(1920, 1080)
        
    @classmethod
    def get_schema(cls):
        return {
            "count": {
                "type": "int",
                "min": 100,
                "max": 5000, # Increased max
                "default": 400,
                "label": "Drop Count"
            },
            "speed": {
                "type": "float",
                "min": 0.5,
                "max": 3.0,
                "default": 1.0,
                "label": "Speed"
            }
        }

    def configure(self, config: dict):
        if 'count' in config:
            self.drop_count = int(config['count'])
            self._init_drops(1920, 1080)
        if 'speed' in config:
            self.speed_mult = float(config['speed'])

    def _init_drops(self, w, h):
        self.pos = np.empty((self.drop_count, 2), dtype=np.float32)
        self.pos[:, 0] = np.random.uniform(0, w, self.drop_count)
        self.pos[:, 1] = np.random.uniform(0, h, self.drop_count)
        
        # params: speed, length, z
        self.params = np.empty((self.drop_count, 3), dtype=np.float32)
        z = np.random.uniform(0.5, 2.0, self.drop_count)
        self.params[:, 2] = z
        self.params[:, 0] = np.random.uniform(15, 25, self.drop_count) * z # speed
        self.params[:, 1] = np.random.uniform(10, 20, self.drop_count) * z # length
        
        self.opacities = (100 * z).astype(np.int32)

    def draw(self, p, w, h, phase):
        # Dark rainy night background
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(10, 15, 30))
            
        if self.pos is None or len(self.pos) != self.drop_count:
            self._init_drops(w, h)

        # Vectorized Update
        # y += speed * speed_mult
        self.pos[:, 1] += self.params[:, 0] * self.speed_mult
        
        # Reset if off screen
        # Find indices where y > h
        reset_mask = self.pos[:, 1] > h
        if np.any(reset_mask):
            self.pos[reset_mask, 1] = -self.params[reset_mask, 1] # reset to -length
            self.pos[reset_mask, 0] = np.random.uniform(0, w, np.sum(reset_mask))
            
        # Draw
        # QPainter doesn't support drawLines from numpy array directly efficiently without loop
        # But we can optimize pen creation
        
        # Optimization: Group by depth or just loop?
        # Loop is unavoidable for variable pens.
        
        pen_color = QColor(160, 210, 255)
        
        for i in range(self.drop_count):
            pen_color.setAlpha(int(self.opacities[i]))
            p.setPen(QPen(pen_color, 1 * float(self.params[i, 2])))
            x = int(self.pos[i, 0])
            y = int(self.pos[i, 1])
            length = int(self.params[i, 1])
            p.drawLine(x, y, x, y + length)
