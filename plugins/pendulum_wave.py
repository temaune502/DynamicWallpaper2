import math
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QBrush, QPen

from effects import BaseEffect

class PendulumWaveEffect(BaseEffect):
    EFFECT_NAME = "pendulum_wave"

    def __init__(self):
        super().__init__()
        self.num_pendulums = 20
        self.base_freq = 0.5 # Oscillations per second
        self.duration = 60 # Cycle length in seconds for pattern repeat
        
        # Precompute lengths
        # Frequency of pendulum i = base_freq + i / duration
        # Length ~ 1 / freq^2
        self.pendulums = []
        for i in range(self.num_pendulums):
            freq = self.base_freq + (i / float(self.duration))
            # L = g / (4 * pi^2 * f^2). Proportional to 1/f^2
            length_factor = 1.0 / (freq * freq) * 100 # arbitrary scale
            
            self.pendulums.append({
                'freq': freq,
                'length_factor': length_factor,
                'color': QColor.fromHsv(int(360 * i / self.num_pendulums), 200, 255)
            })

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        p.fillRect(0, 0, w, h, QColor(10, 10, 20)) # Dark blue-grey bg
        
        cx = w / 2
        cy = h * 0.2 # Mounting point
        
        max_swing_angle = math.pi / 4 # 45 degrees
        
        # Scale lengths so longest fits on screen
        max_len_factor = self.pendulums[0]['length_factor']
        screen_scale = (h * 0.7) / max_len_factor
        
        # Draw mounting bar
        p.setPen(QPen(QColor(200, 200, 200), 4))
        p.drawLine(cx - 200, cy, cx + 200, cy)
        
        # Use absolute time for correct physics phase
        # phase is usually strictly increasing?
        # Assuming phase is seconds or frame count.
        t = phase
        
        for pen in self.pendulums:
            # Angle: sin(2 * pi * f * t)
            angle = max_swing_angle * math.cos(2 * math.pi * pen['freq'] * t)
            
            length = pen['length_factor'] * screen_scale
            
            # Position
            x = cx + math.sin(angle) * length
            y = cy + math.cos(angle) * length
            
            # Draw String
            p.setPen(QPen(QColor(255, 255, 255, 50), 1))
            p.drawLine(cx, cy, x, y)
            
            # Draw Bob
            p.setPen(Qt.NoPen)
            p.setBrush(pen['color'])
            p.drawEllipse(QPointF(x, y), 10, 10)
            
            # Visualization: Trails? Or just snapshot.
            # Pendulum waves look best as snapshot of positions forming a curve.
            
        # Draw curve connecting bobs?
        # p.setPen(QPen(QColor(255, 255, 255, 100), 2))
        # p.setBrush(Qt.NoBrush)
        # points = []
        # for pen in self.pendulums: ...
