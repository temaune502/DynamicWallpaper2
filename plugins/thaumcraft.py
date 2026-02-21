import random
import math
from PySide6.QtGui import QColor, QRadialGradient, QBrush, QPen
from PySide6.QtCore import Qt
from effects import BaseEffect

class ThaumcraftEffect(BaseEffect):
    EFFECT_NAME = "thaumcraft"
    
    def __init__(self):
        super().__init__()
        self.num_nodes = 5
        self.num_particles = 100
        self.nodes = None
        self.particles = None
        
    @classmethod
    def get_schema(cls):
        return {
            "nodes": {
                "type": "int",
                "min": 1,
                "max": 30,
                "default": 5,
                "label": "Node Count"
            },
            "particles": {
                "type": "int",
                "min": 10,
                "max": 500,
                "default": 100,
                "label": "Particle Count"
            }
        }

    def configure(self, config: dict):
        if 'nodes' in config: self.num_nodes = int(config['nodes'])
        if 'particles' in config: self.num_particles = int(config['particles'])
        self.nodes = None # Force re-init

    def _init_scene(self, w, h):
        self.nodes = []
        for _ in range(self.num_nodes):
            self.nodes.append({
                'x': random.uniform(w*0.2, w*0.8),
                'y': random.uniform(h*0.2, h*0.8),
                'size': random.uniform(40, 80),
                'color': QColor(180, 50, 255, 150),
                'rot': random.uniform(0, math.pi * 2)
            })
        
        self.particles = []
        for _ in range(self.num_particles):
            self.particles.append({
                'x': random.uniform(0, w),
                'y': random.uniform(0, h),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-0.5, 0.5),
                'size': random.uniform(1, 3),
                'hue': random.choice([280, 300, 200]) # Purple, Pink, Teal
            })

    def draw(self, p, w, h, phase):
        if self.nodes is None:
            self._init_scene(w, h)

        # Magical background
        bg = QRadialGradient(w/2, h/2, max(w, h))
        bg.setColorAt(0, QColor(15, 5, 25))
        bg.setColorAt(1, QColor(5, 0, 10))
        if self.show_background:
            p.fillRect(0, 0, w, h, QBrush(bg))

        # 1. Vis Particles
        p.setPen(Qt.NoPen)
        for pt in self.particles:
            pt['x'] = (pt['x'] + pt['vx']) % w
            pt['y'] = (pt['y'] + pt['vy']) % h
            
            # Pulsing size
            s = pt['size'] * (1 + 0.5 * math.sin(phase * 10 + pt['x']))
            color = QColor.fromHsv(pt['hue'], 200, 255, 150)
            p.setBrush(color)
            p.drawEllipse(int(pt['x'] - s/2), int(pt['y'] - s/2), int(s), int(s))

        # 2. Nodes
        for node in self.nodes:
            # Subtle movement
            nx = node['x'] + math.sin(phase * 2 + node['y']) * 20
            ny = node['y'] + math.cos(phase * 1.5 + node['x']) * 20
            
            # Central glow
            grad = QRadialGradient(nx, ny, node['size'])
            grad.setColorAt(0, node['color'])
            grad.setColorAt(0.7, QColor(100, 0, 200, 50))
            grad.setColorAt(1, Qt.transparent)
            p.setBrush(QBrush(grad))
            p.drawEllipse(int(nx - node['size']), int(ny - node['size']), int(node['size']*2), int(node['size']*2))
            
            # Rotating rings/runes
            p.setPen(QPen(QColor(200, 100, 255, 100), 2))
            p.setBrush(Qt.NoBrush)
            
            node['rot'] += 0.02
            for i in range(3):
                r = node['size'] * (0.8 + i * 0.3)
                rot = node['rot'] * (1 if i % 2 == 0 else -1)
                
                # Draw "ring" with gaps
                p.save()
                p.translate(nx, ny)
                p.rotate(math.degrees(rot))
                p.drawArc(int(-r), int(-r), int(r*2), int(r*2), 0, 60 * 16)
                p.drawArc(int(-r), int(-r), int(r*2), int(r*2), 120 * 16, 60 * 16)
                p.drawArc(int(-r), int(-r), int(r*2), int(r*2), 240 * 16, 60 * 16)
                
                # Geometric "rune"
                if i == 1:
                    pts = []
                    for j in range(6):
                        ang = j * (math.pi * 2 / 6)
                        pts.append((int(r * math.cos(ang)), int(r * math.sin(ang))))
                    for j in range(6):
                        p.drawLine(pts[j][0], pts[j][1], pts[(j+1)%6][0], pts[(j+1)%6][1])
                p.restore()
