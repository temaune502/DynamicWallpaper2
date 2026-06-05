import random
import math
from PySide6.QtGui import QColor, QBrush, QPen
from PySide6.QtCore import Qt, QPointF
from effects import BaseEffect

class BokehLightsEffect(BaseEffect):
    EFFECT_NAME = "bokeh_lights"
    
    def __init__(self):
        super().__init__()
        self.lights = []
        
    def draw(self, p, w, h, phase):
        # Soft dark gradient or solid fill
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(20, 10, 30))
            
        if not self.lights:
            for _ in range(30):
                self.lights.append({
                    'x': random.uniform(0, w),
                    'y': random.uniform(0, h),
                    'radius': random.uniform(30, 100),
                    'speed_x': random.uniform(-0.5, 0.5),
                    'speed_y': random.uniform(-0.5, 0.5),
                    'hue': random.uniform(0, 360),
                    'phase_offset': random.uniform(0, math.pi * 2)
                })
                
        p.setPen(Qt.NoPen)
        
        for light in self.lights:
            # Move
            light['x'] += light['speed_x']
            light['y'] += light['speed_y']
            
            # Wrap
            if light['x'] < -100: light['x'] = w + 100
            if light['x'] > w + 100: light['x'] = -100
            if light['y'] < -100: light['y'] = h + 100
            if light['y'] > h + 100: light['y'] = -100
            
            # Pulse Opacity
            pulse = math.sin(phase + light['phase_offset'])
            alpha = int(30 + (pulse + 1) * 0.5 * 30) # 30 to 60 (very subtle)
            
            color = QColor.fromHsv(int(light['hue']), 150, 255, alpha)
            p.setBrush(color)
            
            p.drawEllipse(QPointF(light['x'], light['y']), light['radius'], light['radius'])
