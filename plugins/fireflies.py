import random
import math
from PySide6.QtGui import QColor, QRadialGradient, QBrush
from PySide6.QtCore import Qt, QPointF
from effects import BaseEffect

class FirefliesEffect(BaseEffect):
    EFFECT_NAME = "fireflies"
    
    def __init__(self):
        super().__init__()
        self.count = 60
        self.speed_mult = 1.0
        self.fireflies = []
        
    @classmethod
    def get_schema(cls):
        return {
            "count": {
                "type": "int",
                "min": 10,
                "max": 300,
                "default": 60,
                "label": "Firefly Count"
            },
            "speed": {
                "type": "float",
                "min": 0.1,
                "max": 5.0,
                "default": 1.0,
                "label": "Wander Speed"
            }
        }

    def configure(self, config: dict):
        if 'count' in config:
            self.count = int(config['count'])
            self.fireflies = []
        if 'speed' in config:
            self.speed_mult = float(config['speed'])

    def _init_fireflies(self, w, h):
         self.fireflies = []
         for _ in range(self.count):
            self.fireflies.append({
                'x': random.uniform(0, w),
                'y': random.uniform(0, h),
                'base_x': random.uniform(0, w),
                'base_y': random.uniform(0, h),
                'size': random.uniform(2, 6),
                'phase_offset': random.uniform(0, math.pi * 2),
                'wander_speed': random.uniform(0.5, 1.5)
            })

    def draw(self, p, w, h, phase):
        # Dark forest night background
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(5, 10, 5))

        # Initialize fireflies
        if not self.fireflies:
            self._init_fireflies(w, h)

        p.setPen(Qt.NoPen)
        
        for f in self.fireflies:
            # Natural wandering movement
            t = phase * f['wander_speed'] * self.speed_mult
            
            # Update base position slightly (brownian-like drift)
            f['base_x'] += math.sin(t * 0.3 + f['phase_offset']) * 0.5
            f['base_y'] += math.cos(t * 0.2 + f['phase_offset']) * 0.5
            
            # Add wobbly sine movement on top
            curr_x = f['base_x'] + math.sin(t + f['phase_offset']) * 20
            curr_y = f['base_y'] + math.cos(t * 0.8 + f['phase_offset']) * 20
            
            # Wrap around logic for base coordinates
            f['base_x'] %= w
            f['base_y'] %= h
            
            # Adjust current draw coordinates for wrapping appearance
            # (Simple wrap logic: just draw at wrapped curr_x/y)
            draw_x = curr_x % w
            draw_y = curr_y % h
            
            # Pulse logic
            pulse = (math.sin(phase * 2 + f['phase_offset']) + 1) * 0.5 # 0.0 to 1.0
            alpha = int(50 + 205 * pulse)
            
            # Color: Yellow-Green
            # Core
            p.setBrush(QColor(255, 255, 200, alpha))
            p.drawEllipse(QPointF(draw_x, draw_y), f['size'], f['size'])
            
            # Glow
            glow_alpha = int(alpha * 0.3)
            if glow_alpha > 0:
                p.setBrush(QColor(180, 255, 50, glow_alpha))
                p.drawEllipse(QPointF(draw_x, draw_y), f['size'] * 3, f['size'] * 3)
