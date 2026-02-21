import random
import math
from PySide6.QtGui import QColor, QPen, QRadialGradient, QBrush
from PySide6.QtCore import Qt, QPointF
from effects import BaseEffect

class CyberGeometryEffect(BaseEffect):
    EFFECT_NAME = "cyber_geometry"
    
    def __init__(self):
        super().__init__()
        self.shapes = None
        self.grid_alpha = 30
        self.connection_dist = 220

    def draw(self, p, w, h, phase):
        if self.shapes is None:
            self.shapes = []
            for _ in range(18):
                self.shapes.append({
                    'x': random.uniform(0, w),
                    'y': random.uniform(0, h),
                    'size': random.uniform(30, 70),
                    'vx': random.uniform(-0.4, 0.4),
                    'vy': random.uniform(-0.4, 0.4),
                    'type': random.choice(['hex', 'tri', 'square', 'circle']),
                    'rot': random.uniform(0, 360),
                    'rot_v': random.uniform(-0.5, 0.5),
                    'hue': random.uniform(180, 220), # Cyan to Blue
                    'phase_off': random.uniform(0, math.pi * 2)
                })

        # 1. Cyber Background (Grid)
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(5, 10, 20))
            
            # Draw scrolling grid
            grid_size = 50
            p.setPen(QPen(QColor(0, 255, 255, self.grid_alpha), 1))
            
            offset_x = (phase * 20) % grid_size
            offset_y = (phase * 10) % grid_size
            
            for x in range(int(-grid_size + offset_x), w + grid_size, grid_size):
                p.drawLine(x, 0, x, h)
            for y in range(int(-grid_size + offset_y), h + grid_size, grid_size):
                p.drawLine(0, y, w, y)

        # 2. Update and Draw Shapes
        for s in self.shapes:
            s['x'] = (s['x'] + s['vx']) % w
            s['y'] = (s['y'] + s['vy']) % h
            s['rot'] += s['rot_v']
            
            # Pulsing logic
            pulse = math.sin(phase * 2 + s['phase_off']) * 0.2 + 1.0
            size = s['size'] * pulse
            
            p.save()
            p.translate(s['x'], s['y'])
            p.rotate(s['rot'] + phase * 15)
            
            # Glow effect
            main_color = QColor.fromHsv(int(s['hue']), 200, 255, 180)
            glow_grad = QRadialGradient(0, 0, size * 1.5)
            glow_grad.setColorAt(0, QColor.fromHsv(int(s['hue']), 200, 255, 60))
            glow_grad.setColorAt(1, Qt.transparent)
            p.setBrush(QBrush(glow_grad))
            p.setPen(Qt.NoPen)
            p.drawEllipse(int(-size * 1.5), int(-size * 1.5), int(size * 3), int(size * 3))
            
            # Main Shape
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(main_color, 2))
            
            if s['type'] == 'hex':
                self._draw_poly(p, size, 6)
            elif s['type'] == 'tri':
                self._draw_poly(p, size, 3)
            elif s['type'] == 'circle':
                p.drawEllipse(int(-size), int(-size), int(size*2), int(size*2))
            else: # square
                p.drawRect(int(-size), int(-size), int(size*2), int(size*2))
                
            # Inner details
            p.setPen(QPen(QColor.fromHsv(int(s['hue']), 100, 255, 80), 1))
            if s['type'] != 'circle':
                self._draw_poly(p, size * 0.6, 6 if s['type'] == 'hex' else (3 if s['type'] == 'tri' else 4))
            
            p.restore()

        # 3. Connections
        for i, s in enumerate(self.shapes):
            for other in self.shapes[i+1:]:
                dist = math.hypot(s['x'] - other['x'], s['y'] - other['y'])
                if dist < self.connection_dist:
                    alpha = int(120 * (1 - dist / self.connection_dist))
                    # Connection line with small "nodes" or glow
                    p.setPen(QPen(QColor(0, 255, 255, alpha), 1))
                    p.drawLine(int(s['x']), int(s['y']), int(other['x']), int(other['y']))
                    
                    # Optional: small bit of data moving along the line
                    if random.random() < 0.05:
                        t = (phase * 2 + i) % 1.0
                        lx = s['x'] + (other['x'] - s['x']) * t
                        ly = s['y'] + (other['y'] - s['y']) * t
                        p.setPen(QPen(QColor(255, 255, 255, alpha * 2), 2))
                        p.drawPoint(int(lx), int(ly))

    def _draw_poly(self, p, size, sides):
        pts = []
        for i in range(sides + 1):
            ang = i * (math.pi * 2 / sides)
            pts.append(QPointF(size * math.cos(ang), size * math.sin(ang)))
        p.drawPolyline(pts)
