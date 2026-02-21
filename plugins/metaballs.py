import random
import math
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QRadialGradient, QBrush

from effects import BaseEffect

class MetaballsEffect(BaseEffect):
    EFFECT_NAME = "metaballs"

    def __init__(self):
        super().__init__()
        self.balls = []
        for _ in range(15):
            self.balls.append({
                'x': random.uniform(0, 800),
                'y': random.uniform(0, 600),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-2, 2),
                'radius': random.uniform(60, 120),
                'hue': random.random()
            })

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        # Dark background
        p.fillRect(0, 0, w, h, QColor(20, 10, 30))
        
        # We use composition mode to blend "lights"
        p.setCompositionMode(QPainter.CompositionMode_Screen)
        
        for ball in self.balls:
            ball['x'] += ball['vx']
            ball['y'] += ball['vy']
            
            # Bounce
            if ball['x'] < -ball['radius']: ball['vx'] = abs(ball['vx'])
            elif ball['x'] > w + ball['radius']: ball['vx'] = -abs(ball['vx'])
            
            if ball['y'] < -ball['radius']: ball['vy'] = abs(ball['vy'])
            elif ball['y'] > h + ball['radius']: ball['vy'] = -abs(ball['vy'])
            
            # Dynamic color pulsing
            hue = (ball['hue'] + phase * 0.1) % 1.0
            color = QColor.fromHsvF(hue, 0.8, 0.9, 1.0)
            
            # Gradient for "soft" ball look
            grad = QRadialGradient(ball['x'], ball['y'], ball['radius'])
            grad.setColorAt(0, color)
            grad.setColorAt(0.7, QColor.fromHsvF(hue, 0.8, 0.5, 0.5))
            grad.setColorAt(1, Qt.transparent)
            
            p.setBrush(QBrush(grad))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(ball['x'], ball['y']), ball['radius'], ball['radius'])
            
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)
