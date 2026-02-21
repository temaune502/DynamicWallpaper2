import random
from PySide6.QtGui import QColor, QLinearGradient, QBrush, QPen
from PySide6.QtCore import Qt
from effects import BaseEffect

class WaterRippleEffect(BaseEffect):
    EFFECT_NAME = "water"
    
    def __init__(self):
        super().__init__()
        self.spawn_chance = 0.1
        self.ripples = None

    @classmethod
    def get_schema(cls):
        return {
            "chance": {
                "type": "float",
                "min": 0.0,
                "max": 1.0,
                "default": 0.1,
                "label": "Ripple Chance"
            }
        }

    def configure(self, config: dict):
        if 'chance' in config: self.spawn_chance = float(config['chance'])

    def draw(self, p, w, h, phase):
        if self.ripples is None:
            self.ripples = []
            for _ in range(15):
                self.ripples.append(self._create_ripple(w, h))

        if self.show_background:
            bg = QLinearGradient(0, 0, 0, h)
            bg.setColorAt(0, QColor(0, 20, 40))
            bg.setColorAt(1, QColor(0, 5, 10))
            p.fillRect(0, 0, w, h, QBrush(bg))

        if random.random() < self.spawn_chance:
            self.ripples.append(self._create_ripple(w, h))

        p.setBrush(Qt.NoBrush)
        active_ripples = []
        for r in self.ripples:
            r['age'] += 1
            r['radius'] += r['speed']
            
            opacity = int(255 * (1.0 - r['age'] / r['max_age']))
            if opacity > 0:
                p.setPen(QPen(QColor(150, 200, 255, opacity), 2))
                for i in range(2):
                    radius = r['radius'] - i * 15
                    if radius > 0:
                        p.drawEllipse(int(r['x'] - radius), int(r['y'] - radius * 0.7), 
                                     int(radius * 2), int(radius * 1.4))
                active_ripples.append(r)
        
        self.ripples = active_ripples

    def _create_ripple(self, w, h):
        return {
            'x': random.uniform(0, w),
            'y': random.uniform(0, h),
            'radius': 0,
            'speed': random.uniform(1.0, 2.5),
            'age': 0,
            'max_age': random.randint(60, 120)
        }
