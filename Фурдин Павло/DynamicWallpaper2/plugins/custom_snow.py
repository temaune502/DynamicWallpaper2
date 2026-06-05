import random
import math
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from effects import BaseEffect

class CustomSnowflakeEffect(BaseEffect):
    EFFECT_NAME = "custom_snow"
    
    def __init__(self):
        super().__init__()
        self.snowflakes = None
        self.matrix_large = [
            [1, 1, 1, 1, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 1, 0, 0, 0],
            [1, 0, 0, 1, 0, 0, 0],
            [1, 0, 0, 1, 1, 1, 1]
        ]

    def draw(self, p, w, h, phase):
        if self.snowflakes is None:
            self.snowflakes = []
            for _ in range(100):
                self.snowflakes.append({
                    'x': random.uniform(0, w),
                    'y': random.uniform(-h, h),
                    'speed': random.uniform(1.5, 3.5),
                    'pixel_size': random.randint(2, 4),
                    'drift': random.uniform(0.3, 1.0),
                    'rot': random.uniform(0, 360),
                    'rot_v': random.uniform(-2, 2),
                    'opacity': random.randint(150, 255)
                })

        p.setPen(Qt.NoPen)
        matrix = self.matrix_large
        rows = len(matrix)
        cols = len(matrix[0])
        
        for s in self.snowflakes:
            s['y'] += s['speed']
            s['x'] += math.sin(phase + s['y'] * 0.01) * s['drift']
            s['rot'] += s['rot_v']
            
            if s['y'] > h + 50:
                s['y'] = -50
                s['x'] = random.uniform(0, w)

            p.save()
            p.translate(s['x'], s['y'])
            p.rotate(s['rot'])
            p.setBrush(QColor(255, 255, 255, s['opacity']))
            
            ps = s['pixel_size']
            offset_x = -(cols * ps) / 2
            offset_y = -(rows * ps) / 2
            
            for r in range(rows):
                for c in range(cols):
                    if matrix[r][c] == 1:
                        p.drawRect(int(offset_x + c * ps), int(offset_y + r * ps), ps, ps)
            
            p.setBrush(QColor(255, 255, 255, 40))
            p.drawEllipse(int(offset_x), int(offset_y), int(cols * ps), int(rows * ps))
            p.restore()
