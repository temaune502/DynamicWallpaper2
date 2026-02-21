import random
import math
import time
from PySide6.QtGui import QColor, QPen, QBrush, QRadialGradient, QFont
from PySide6.QtCore import Qt, QPointF
from effects import BaseEffect

class ConstellationClockEffect(BaseEffect):
    EFFECT_NAME = "constellation_clock"
    
    def __init__(self):
        super().__init__()
        self.stars = None
        self.num_stars = 120
        self.connections = []
        self.last_time = ""

    def draw(self, p, w, h, phase):
        cx, cy = w // 2, h // 2
        radius = min(w, h) * 0.35
        
        if self.stars is None:
            self.stars = []
            for _ in range(self.num_stars):
                self.stars.append({
                    'x': random.uniform(0, w),
                    'y': random.uniform(0, h),
                    'vx': random.uniform(-0.2, 0.2),
                    'vy': random.uniform(-0.2, 0.2),
                    'size': random.uniform(1, 3),
                    'blink_off': random.uniform(0, math.pi * 2)
                })

        # 1. Cosmic Background
        if self.show_background:
            bg_grad = QRadialGradient(cx, cy, max(w, h) * 0.7)
            bg_grad.setColorAt(0, QColor(10, 10, 30))
            bg_grad.setColorAt(1, QColor(0, 0, 5))
            p.fillRect(0, 0, w, h, QBrush(bg_grad))

        # 2. Update and Draw Stars
        p.setPen(Qt.NoPen)
        for s in self.stars:
            s['x'] = (s['x'] + s['vx']) % w
            s['y'] = (s['y'] + s['vy']) % h
            
            # Blinking effect
            blink = (math.sin(phase * 3 + s['blink_off']) * 0.5 + 0.5) * 200 + 55
            p.setBrush(QColor(255, 255, 255, int(blink)))
            p.drawEllipse(QPointF(s['x'], s['y']), s['size'], s['size'])

        # 3. Geometric Clock Core
        t = time.localtime()
        hr = t.tm_hour % 12
        mn = t.tm_min
        sc = t.tm_sec
        
        # Calculate hand angles
        sc_ang = (sc / 60) * math.pi * 2 - math.pi / 2
        mn_ang = (mn / 60) * math.pi * 2 - math.pi / 2
        hr_ang = ((hr + mn/60) / 12) * math.pi * 2 - math.pi / 2

        # Draw central nexus
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(100, 150, 255, 40), 1, Qt.DashLine))
        p.drawEllipse(cx - radius, cy - radius, radius * 2, radius * 2)
        
        # 4. Connecting lines (The "Constellation" part)
        # Connect stars to clock hands if they are close
        hand_points = [
            (cx + math.cos(sc_ang) * radius, cy + math.sin(sc_ang) * radius, QColor(255, 100, 100, 150)),
            (cx + math.cos(mn_ang) * radius * 0.8, cy + math.sin(mn_ang) * radius * 0.8, QColor(100, 255, 150, 150)),
            (cx + math.cos(hr_ang) * radius * 0.6, cy + math.sin(hr_ang) * radius * 0.6, QColor(100, 200, 255, 150))
        ]

        for hx, hy, hcol in hand_points:
            p.setPen(QPen(hcol, 2))
            p.drawLine(cx, cy, int(hx), int(hy))
            
            # Connect nearby stars to the hand tip
            for s in self.stars:
                dist = math.hypot(s['x'] - hx, s['y'] - hy)
                if dist < 120:
                    alpha = int(100 * (1 - dist / 120))
                    p.setPen(QPen(QColor(hcol.red(), hcol.green(), hcol.blue(), alpha), 1))
                    p.drawLine(int(s['x']), int(s['y']), int(hx), int(hy))

        # 5. Inner clock geometry
        p.setPen(QPen(QColor(255, 255, 255, 80), 1))
        for i in range(12):
            ang = (i / 12) * math.pi * 2
            tx = cx + math.cos(ang) * radius
            ty = cy + math.sin(ang) * radius
            p.drawEllipse(QPointF(tx, ty), 2, 2)
            
            # Connect clock points to each other (fractal look)
            if i % 3 == 0:
                next_ang = ((i + 4) / 12) * math.pi * 2
                nx = cx + math.cos(next_ang) * radius
                ny = cy + math.sin(next_ang) * radius
                p.setPen(QPen(QColor(100, 200, 255, 30), 1))
                p.drawLine(int(tx), int(ty), int(nx), int(ny))

        # 6. Digital Time Overlay (Stylized)
        time_str = time.strftime("%H:%M:%S")
        p.setPen(QColor(255, 255, 255, 180))
        font = QFont("Orbitron", 24) if "Orbitron" in QFont().families() else QFont("Monospace", 20)
        p.setFont(font)
        p.drawText(cx - 60, cy + radius + 60, time_str)
        
        # Pulse effect in center
        pulse = (math.sin(phase * 2) * 0.5 + 0.5) * 10 + 5
        p.setBrush(QColor(100, 200, 255, 100))
        p.drawEllipse(cx - int(pulse/2), cy - int(pulse/2), int(pulse), int(pulse))
