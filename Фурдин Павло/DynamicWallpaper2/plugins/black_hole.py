import math
import random
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QRadialGradient, QBrush, QPen

from effects import BaseEffect

class BlackHoleEffect(BaseEffect):
    EFFECT_NAME = "black_hole"

    def __init__(self):
        super().__init__()
        self.particles = []
        self.num_particles = 1000
        self.accretion_disk = []
        
        self.disk_color_hue = 30 # Orange
        
        # Initialize particles for background stars
        self._init_stars()
            
        # Initialize accretion disk particles
        self._init_disk()

        self._init_disk()

    @classmethod
    def get_schema(cls):
        return {
            "stars": {
                "type": "int",
                "min": 10,
                "max": 1000,
                "default": 200,
                "label": "Star Count"
            },
            "disk_hue": {
                "type": "float",
                "min": 0.0,
                "max": 1.0,
                "default": 0.08,
                "label": "Disk Hue (0-1)"
            }
        }

    def configure(self, config: dict):
        if 'star_count' in config:
            self.num_particles = int(config['star_count'])
            self._init_stars()
            
        if 'disk_color' in config:
             # Expects hue 0-360
             self.disk_color_hue = int(config['disk_color'])
             self._init_disk()

    def _init_stars(self):
        self.particles = []
        for _ in range(self.num_particles):
            self.particles.append({
                'x': random.uniform(-1000, 3000),
                'y': random.uniform(-1000, 2000),
                'size': random.uniform(0.5, 2.0),
                'color': QColor(255, 255, 255, random.randint(100, 255))
            })

    def _init_disk(self):
        self.accretion_disk = []
        for _ in range(500):
             angle = random.uniform(0, math.pi * 2)
             dist = random.uniform(100, 300)
             self.accretion_disk.append({
                 'angle': angle,
                 'dist': dist,
                 'speed': 5.0 / math.sqrt(dist), # Keplerian-ish
                 'size': random.uniform(1, 3),
                 'color': QColor.fromHsv(random.randint(self.disk_color_hue - 15, self.disk_color_hue + 15), 200, 255) 
             })

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(0, 0, 0))
        
        cx, cy = w / 2, h / 2
        
        # 1. Background lensing
        # Draw stars, but displace them based on distance to black hole (Lensing)
        p.setPen(Qt.NoPen)
        for pt in self.particles:
            dx = pt['x'] - cx
            dy = pt['y'] - cy
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Simple interaction/drift
            # pt['x'] -= 0.1 # Slow drift
            
            real_x, real_y = pt['x'], pt['y']
            
            # Lensing math (Einstein radius approx)
            # Deflect light AROUND the event horizon (radius ~80)
            if dist > 10 and dist < 400:
                # Push away from center
                force = 5000.0 / dist
                path_x = real_x + (dx / dist) * force
                path_y = real_y + (dy / dist) * force
            else:
                path_x, path_y = real_x, real_y
                
            p.setBrush(pt['color'])
            p.drawEllipse(QPointF(path_x, path_y), pt['size'], pt['size'])

        # 2. Accretion Disk (Back)
        # We need 3D projection for a tilted disk. 
        # Tilt angle ~60 deg
        tilt = 0.4
        
        self.accretion_disk.sort(key=lambda p: math.sin(p['angle'])) # Sort by depth (y-coord in 2D before tilt)
        # Actually for a simple tilted circle loop:
        # y_screen = cy + sin(a) * r * tilt
        # z = sin(a) * r  <-- depth
        # We draw back half (z > 0 or whatever) first, then BH, then front half.
        
        disk_back = [p for p in self.accretion_disk if math.sin(p['angle']) < 0]
        disk_front = [p for p in self.accretion_disk if math.sin(p['angle']) >= 0]
        
        # Draw Back Disk
        for part in disk_back:
            part['angle'] += part['speed'] * 0.1
            
            # Draw
            x = cx + math.cos(part['angle']) * part['dist']
            y = cy + math.sin(part['angle']) * part['dist'] * tilt
            
            p.setBrush(part['color'])
            p.drawEllipse(QPointF(x, y), part['size'], part['size'])

        # 3. Event Horizon (The Black Hole)
        p.setBrush(QColor(0, 0, 0))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, cy), 80, 80)
        
        # Photon Ring (Glowing edge)
        pen = QPen(QColor(255, 200, 150, 100), 2)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), 82, 82)
        p.setPen(Qt.NoPen)

        # 4. Accretion Disk (Front)
        for part in disk_front:
            part['angle'] += part['speed'] * 0.1
            
            # Doppler beaming? Make approaching side brighter.
            # approaching is when cos(angle) > 0 (right side moving towards us? depends on rotation)
            # Let's just draw
            x = cx + math.cos(part['angle']) * part['dist']
            y = cy + math.sin(part['angle']) * part['dist'] * tilt
            
            p.setBrush(part['color'])
            p.drawEllipse(QPointF(x, y), part['size'], part['size'])
