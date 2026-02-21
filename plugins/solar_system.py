import math
import random
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QBrush, QPen

from effects import BaseEffect

class SolarSystemEffect(BaseEffect):
    EFFECT_NAME = "solar_system"

    def __init__(self):
        super().__init__()
        self.planets = []
        # Create planets
        num_planets = 8
        for i in range(num_planets):
            dist = 60 + i * 40 + random.randint(0, 20)
            self.planets.append({
                'dist': dist,
                'angle': random.uniform(0, math.pi * 2),
                'speed': 1.0 / math.sqrt(dist) * 5.0, # Kepler-ish
                'size': random.uniform(5, 15),
                'color': QColor.fromHsv(random.randint(0, 360), 200, 200),
                'moons': []
            })
            
            # Add moons
            if random.random() < 0.5:
                num_moons = random.randint(1, 3)
                for _ in range(num_moons):
                    self.planets[-1]['moons'].append({
                        'dist': random.uniform(15, 25),
                        'angle': random.uniform(0, math.pi * 2),
                        'speed': random.uniform(0.05, 0.1),
                        'size': random.uniform(2, 4)
                    })

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        p.fillRect(0, 0, w, h, QColor(5, 5, 10))
        
        cx, cy = w / 2, h / 2
        
        # Draw Sun
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 0)) # Yellow Sun
        p.drawEllipse(QPointF(cx, cy), 30, 30)
        
        # Glow
        grad_col = QColor(255, 200, 0, 50)
        p.setBrush(grad_col)
        p.drawEllipse(QPointF(cx, cy), 50, 50)
        
        # Draw Orbits (faint lines)
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(255, 255, 255, 20), 1))
        for planet in self.planets:
            p.drawEllipse(QPointF(cx, cy), planet['dist'], planet['dist'])
            
        p.setPen(Qt.NoPen)
        
        for planet in self.planets:
            # Update
            planet['angle'] += planet['speed'] * 0.05
            
            px = cx + math.cos(planet['angle']) * planet['dist']
            py = cy + math.sin(planet['angle']) * planet['dist']
            
            # Draw Planet
            p.setBrush(planet['color'])
            p.drawEllipse(QPointF(px, py), planet['size'], planet['size'])
            
            # Draw Moons
            for moon in planet['moons']:
                moon['angle'] += moon['speed']
                mx = px + math.cos(moon['angle']) * moon['dist']
                my = py + math.sin(moon['angle']) * moon['dist']
                
                p.setBrush(QColor(200, 200, 200))
                p.drawEllipse(QPointF(mx, my), moon['size'], moon['size'])
