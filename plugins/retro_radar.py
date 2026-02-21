import math
import random
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QRadialGradient, QBrush, QPen, QPainter, QConicalGradient

from effects import BaseEffect

class RetroRadarEffect(BaseEffect):
    EFFECT_NAME = "retro_radar"

    def __init__(self):
        super().__init__()
        self.blips = []
        for _ in range(5):
            self._add_blip()

    def _add_blip(self):
        self.blips.append({
            'angle': random.uniform(0, 360),
            'distance': random.uniform(0.1, 0.9),
            'life': 1.0,
            'size': random.uniform(3, 8)
        })

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        cx, cy = w / 2, h / 2
        radius = min(w, h) * 0.4
        
        # 1. Background (Dark Green Screen)
        p.fillRect(0, 0, w, h, QColor(0, 20, 0))

        # 2. Radar Grid
        pen = QPen(QColor(0, 100, 0))
        pen.setWidth(1)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        
        # Concentric circles
        for r in [0.25, 0.5, 0.75, 1.0]:
            p.drawEllipse(QPointF(cx, cy), radius * r, radius * r)
        
        # Crosshairs
        p.drawLine(cx - radius, cy, cx + radius, cy)
        p.drawLine(cx, cy - radius, cx, cy + radius)

        # 3. Rotating Beam (Scanner)
        # Phase 0..1 -> Angle 0..360
        # Rotate counter-clockwise for "standard" radar feel or clockwise
        angle = (phase * 360 * 2) % 360  # Speed up 2x
        
        gradient = QConicalGradient(cx, cy, -angle)
        gradient.setColorAt(0, QColor(0, 255, 0, 180))
        gradient.setColorAt(0.1, QColor(0, 255, 0, 0))
        gradient.setColorAt(1, QColor(0, 255, 0, 0))
        
        p.setBrush(QBrush(gradient))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, cy), radius, radius)

        # 4. Blips
        # Update blips
        if random.random() < 0.02:
            self._add_blip()
            
        p.setPen(Qt.NoPen)
        new_blips = []
        for blip in self.blips:
            # Check if beam passed the blip? 
            # Simple approximation: fade out over time
            blip['life'] -= 0.005
            
            # Simple "reveal" logic: if angle is close to blip angle, boost life
            # normalizing angles is tricky, let's just make them pulse randomly or constant fade
            
            alpha = int(blip['life'] * 255)
            if alpha > 0:
                p.setBrush(QColor(0, 255, 0, alpha))
                
                bx = cx + math.cos(math.radians(blip['angle'])) * (blip['distance'] * radius)
                by = cy + math.sin(math.radians(blip['angle'])) * (blip['distance'] * radius)
                
                p.drawEllipse(QPointF(bx, by), blip['size'], blip['size'])
                new_blips.append(blip)
        
        self.blips = new_blips
