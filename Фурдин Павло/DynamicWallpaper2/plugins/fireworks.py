import random
import math
from PySide6.QtGui import QColor, QBrush, QPen
from PySide6.QtCore import Qt, QPointF
from effects import BaseEffect

class FireworksEffect(BaseEffect):
    EFFECT_NAME = "fireworks"
    
    def __init__(self):
        super().__init__()
        self.particles = []
        self.rockets = []
        self.next_launch = 0
        
    def draw(self, p, w, h, phase):
        # Night sky
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(10, 10, 25))
            
        # Launch rockets logic (using phase as simplistic timer)
        # Assuming phase increases monotonically usually, but if it cycles 0-1 it might be tricky.
        # Let's rely on random chance each frame slightly, assuming 60fps
        if random.random() < 0.03:
            self._launch_rocket(w, h)
            
        # Update and draw Rockets
        for r in self.rockets[:]:
            r['x'] += r['vx']
            r['y'] += r['vy']
            r['vy'] += 0.05 # Gravity
            r['life'] -= 1
            
            p.setPen(QPen(QColor(255, 255, 255), 2))
            p.drawPoint(int(r['x']), int(r['y']))
            
            if r['vy'] >= 0 or r['life'] <= 0: # Peak reached or timeout
                self._explode(r['x'], r['y'], r['color'])
                self.rockets.remove(r)
                
        # Update and draw Particles
        for part in self.particles[:]:
            part['x'] += part['vx']
            part['y'] += part['vy']
            part['vy'] += 0.08 # Gravity
            part['life'] -= 0.02
            
            if part['life'] <= 0:
                self.particles.remove(part)
                continue
                
            alpha = int(part['life'] * 255)
            alpha = max(0, min(255, alpha))
            c = QColor(part['color'])
            c.setAlpha(alpha)
            
            p.setPen(Qt.NoPen)
            p.setBrush(c)
            p.drawEllipse(QPointF(part['x'], part['y']), 2, 2)
            
    def _launch_rocket(self, w, h):
        self.rockets.append({
            'x': random.uniform(w*0.1, w*0.9),
            'y': h,
            'vx': random.uniform(-1, 1),
            'vy': random.uniform(-9, -12),
            'life': 100,
            'color': QColor.fromHsv(random.randint(0, 360), 200, 255)
        })
        
    def _explode(self, x, y, color):
        count = 50
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 4)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.uniform(0.5, 1.5),
                'color': color
            })
