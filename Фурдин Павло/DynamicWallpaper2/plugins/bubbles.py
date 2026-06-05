import random
import math
from PySide6.QtGui import QColor, QLinearGradient, QBrush, QPen
from PySide6.QtCore import Qt, QPointF
from effects import BaseEffect

class BubblesEffect(BaseEffect):
    EFFECT_NAME = "bubbles"
    
    def __init__(self):
        super().__init__()
        self.bubble_count = 60
        self.max_speed = 4.0
        self.bubbles = []

    @classmethod
    def get_schema(cls):
        return {
            "count": {
                "type": "int",
                "min": 10,
                "max": 200,
                "default": 60,
                "label": "Bubble Count"
            },
            "speed": {
                "type": "float",
                "min": 1.0,
                "max": 10.0,
                "default": 4.0,
                "label": "Max Speed"
            }
        }

    def configure(self, config: dict):
        if 'count' in config:
            self.bubble_count = int(config['count'])
            self.bubbles = []
        if 'speed' in config:
            self.max_speed = float(config['speed'])

    def _init_bubbles(self, w, h):
         self.bubbles = []
         for _ in range(self.bubble_count):
            self.bubbles.append({
                'x': random.uniform(0, w),
                'y': random.uniform(0, h),
                'size': random.uniform(10, 40),
                'speed': random.uniform(1, self.max_speed),
                'wobble_phase': random.uniform(0, math.pi * 2),
                'wobble_width': random.uniform(10, 30)
            })
        
    def draw(self, p, w, h, phase):
        # Underwater gradient background
        if self.show_background:
            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0, QColor(0, 60, 100))  # Lighter top
            grad.setColorAt(1, QColor(0, 15, 30))   # Darker deep bottom
            p.fillRect(0, 0, w, h, QBrush(grad))
            
        if not self.bubbles:
            self._init_bubbles(w, h)

        p.setPen(QPen(QColor(255, 255, 255, 80), 1.5))
        p.setBrush(QColor(255, 255, 255, 15))

        for b in self.bubbles:
            # Rise
            b['y'] -= b['speed']
            
            # Wobble (sinusoidal x movement)
            # Use phase + unique offset
            x_wobble = math.sin(phase * 3 + b['wobble_phase']) * (b['wobble_width'] * 0.2)
            draw_x = b['x'] + x_wobble
            
            # Reset if completely off top
            if b['y'] + b['size'] < -50:
                b['y'] = h + random.uniform(20, 100)
                b['x'] = random.uniform(0, w)
            
            # Draw main bubble
            p.drawEllipse(QPointF(draw_x, b['y']), b['size'], b['size'])
            
            # Draw highlight (reflection)
            # Save painter state implicitly by manually setting/unsetting or carefully ordering
            p_pen = p.pen()
            p_brush = p.brush()
            
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 255, 255, 120))
            
            # Small shine on top-left of bubble
            shine_size = b['size'] * 0.25
            shine_x = draw_x + b['size'] * 0.2
            shine_y = b['y'] + b['size'] * 0.2
            p.drawEllipse(QPointF(shine_x, shine_y), shine_size, shine_size)
            
            # Restore style for next bubble
            p.setPen(p_pen)
            p.setBrush(p_brush)
