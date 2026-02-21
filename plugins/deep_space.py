import random
import math
from PySide6.QtGui import QColor, QRadialGradient, QBrush, QLinearGradient, QPen
from PySide6.QtCore import Qt
from effects import BaseEffect

class DeepSpaceEffect(BaseEffect):
    EFFECT_NAME = "deep_space"
    
    def __init__(self):
        super().__init__()
        self.stars = None
        self.planets = None
        self.comets = None
        self.asteroids = None

    def draw(self, p, w, h, phase):
        if self.stars is None:
            self.stars = []
            for _ in range(300):
                self.stars.append([random.uniform(0, w), random.uniform(0, h), random.uniform(0.5, 2), random.randint(150, 255)])
            
            self.planets = []
            for _ in range(3):
                self.planets.append({
                    'x': random.uniform(0, w),
                    'y': random.uniform(0, h),
                    'r': random.uniform(20, 60),
                    'color': QColor(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)),
                    'speed': random.uniform(0.1, 0.3)
                })

            self.comets = []
            for _ in range(2):
                self.comets.append(self._reset_comet(w, h))

            self.asteroids = []
            for _ in range(10):
                self.asteroids.append({
                    'x': random.uniform(0, w),
                    'y': random.uniform(0, h),
                    'size': random.uniform(3, 8),
                    'speed': random.uniform(0.2, 0.5),
                    'rot': random.uniform(0, 360)
                })

        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(2, 2, 8))

        # 1. Stars (with parallax)
        for s in self.stars:
            s[0] = (s[0] - s[2] * 0.5) % w
            alpha = int(s[3] * (0.7 + 0.3 * math.sin(phase * 5 + s[0] * 0.01)))
            p.setPen(QColor(255, 255, 255, alpha))
            p.drawPoint(int(s[0]), int(s[1]))

        # 2. Planets
        for pl in self.planets:
            pl['x'] = (pl['x'] - pl['speed']) % w
            grad = QRadialGradient(pl['x'] - pl['r']*0.3, pl['y'] - pl['r']*0.3, pl['r']*1.5)
            grad.setColorAt(0, pl['color'])
            grad.setColorAt(0.6, pl['color'].darker(200))
            grad.setColorAt(1, Qt.black)
            p.setBrush(QBrush(grad))
            p.setPen(Qt.NoPen)
            p.drawEllipse(int(pl['x'] - pl['r']), int(pl['y'] - pl['r']), int(pl['r']*2), int(pl['r']*2))

        # 3. Asteroids
        p.setBrush(QColor(80, 70, 60))
        for a in self.asteroids:
            a['x'] = (a['x'] - a['speed']) % w
            a['rot'] += 1
            p.save()
            p.translate(a['x'], a['y'])
            p.rotate(a['rot'])
            p.drawRect(int(-a['size']/2), int(-a['size']/2), int(a['size']), int(a['size']))
            p.restore()

        # 4. Comets
        for c in self.comets:
            c['x'] += c['vx']
            c['y'] += c['vy']
            
            # Trail
            grad = QLinearGradient(c['x'], c['y'], c['x'] - c['vx']*20, c['y'] - c['vy']*20)
            grad.setColorAt(0, QColor(200, 230, 255, 200))
            grad.setColorAt(1, QColor(100, 150, 255, 0))
            p.setPen(QPen(QBrush(grad), 3))
            p.drawLine(int(c['x']), int(c['y']), int(c['x'] - c['vx']*20), int(c['y'] - c['vy']*20))
            
            # Head
            p.setBrush(Qt.white)
            p.setPen(Qt.NoPen)
            p.drawEllipse(int(c['x']-2), int(c['y']-2), 4, 4)
            
            if c['x'] < -100 or c['x'] > w + 100 or c['y'] < -100 or c['y'] > h + 100:
                c.update(self._reset_comet(w, h))

    def _reset_comet(self, w, h):
        side = random.randint(0, 3)
        if side == 0: x, y = -50, random.uniform(0, h) # Left
        elif side == 1: x, y = w + 50, random.uniform(0, h) # Right
        elif side == 2: x, y = random.uniform(0, w), -50 # Top
        else: x, y = random.uniform(0, w), h + 50 # Bottom
        
        target_x, target_y = w // 2, h // 2
        angle = math.atan2(target_y - y, target_x - x) + random.uniform(-0.5, 0.5)
        speed = random.uniform(5, 10)
        return {'x': x, 'y': y, 'vx': math.cos(angle) * speed, 'vy': math.sin(angle) * speed}
