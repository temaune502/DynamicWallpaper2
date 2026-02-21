import math
import random
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QRadialGradient, QBrush, QPen

from effects import BaseEffect

class GalacticCoreEffect(BaseEffect):
    EFFECT_NAME = "galactic_core"

    def __init__(self):
        super().__init__()
        self.num_stars = 2000
        self.stars = []
        
        # Spiral Galaxy Parameters
        self.arms = 2
        self.arm_spread = 0.5
        
        
        self.color_core = (255, 255, 200)
        self.color_arm_hues = [200, 220, 260, 280]

        # Init stars
        self._init_galaxy()

        self.stars = []
        self._init_galaxy()

    @classmethod
    def get_schema(cls):
        return {
            "stars": {
                "type": "int",
                "min": 100,
                "max": 5000,
                "default": 1000,
                "label": "Star Count"
            },
            "arms": {
                "type": "int",
                "min": 1,
                "max": 10,
                "default": 3,
                "label": "Arms"
            },
            "spread": {
                "type": "float",
                "min": 0.0,
                "max": 2.0,
                "default": 0.5,
                "label": "Spread"
            },
            "color_core": {
                "type": "float",
                "min": 0.0,
                "max": 1.0,
                "default": 0.15,
                "label": "Core Hue"
            },
            "color_arms": {
                "type": "float",
                "min": 0.0,
                "max": 1.0,
                "default": 0.6,
                "label": "Arms Hue"
            }
        }

    def configure(self, config: dict):
        if 'stars' in config: self.num_stars = int(config['stars'])
        if 'arms' in config: self.arms = int(config['arms'])
        if 'spread' in config: self.arm_spread = float(config['spread'])
        
        if 'color_core' in config: self.color_core = tuple(config['color_core'])
        if 'color_arms' in config: self.color_arm_hues = config['color_arms'] # List of hues
        
        # Re-init if structural changes
        if any(k in config for k in ['stars', 'arms', 'spread', 'color_core', 'color_arms']):
            self._init_galaxy()

    def _init_galaxy(self):
        self.stars = []
        for _ in range(self.num_stars):
            # Distance from center (exponential distribution for core density)
            dist = random.expovariate(1.0/300.0)
            if dist > 600: dist = random.uniform(0, 600)
            
            # Angle
            angle = random.uniform(0, math.pi * 2)
            
            # Add spiral offset based on distance
            arm_offset = (random.randint(0, self.arms - 1) * (math.pi * 2 / self.arms))
            
            # Perturbation (scatter)
            scatter = random.gauss(0, self.arm_spread) 
            
            base_angle = arm_offset + scatter
            twist = dist * 0.01
            
            self.stars.append({
                'dist': dist,
                'angle': base_angle + twist,
                'speed': 10.0 / (dist + 10.0), # Inner stars move faster
                'size': random.uniform(0.5, 2.0),
                'color': self._get_star_color(dist),
                'type': 'star'
            })
            
        # Dust lanes (dark particles)
        for _ in range(500):
             dist = random.uniform(100, 500)
             arm_offset = (random.randint(0, self.arms - 1) * (math.pi * 2 / self.arms))
             # Offset slightly from the star arm to create "lane" effect
             base_angle = arm_offset + 0.3 + random.gauss(0, 0.2)
             twist = dist * 0.01
             
             self.stars.append({
                'dist': dist,
                'angle': base_angle + twist,
                'speed': 10.0 / (dist + 10.0),
                'size': random.uniform(2, 4),
                'color': QColor(0, 0, 0, 150), # Dark semi-transparent
                'type': 'dust'
            })

    def _get_star_color(self, dist):
        # Color gradient: Blue/White (hot, young) in arms, Yellow/Red (old) in core
        if dist < 100:
            # Core: Yellow/White
            return QColor.fromHsv(random.randint(40, 60), random.randint(0, 100), 255)
            # We could use self.color_core but hue random is good. 
        else:
            # Arms
             hue = random.choice(self.color_arm_hues)
             return QColor.fromHsv(hue, random.randint(50, 150), 255)

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(0, 0, 5)) # Deep space blue-black
        
        cx, cy = w / 2, h / 2
        
        # Draw Central Bulge Glow
        grad = QRadialGradient(cx, cy, 150)
        grad.setColorAt(0, QColor(255, 255, 200, 100))
        grad.setColorAt(1, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(grad))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, cy), 150, 150)
        
        p.setPen(Qt.NoPen)
        
        # Rotate entire galaxy
        rotation = phase * 0.5
        
        # Sort by type so dust is on top? Or mixed?
        # Better to draw stars first, then dust.
        
        # Draw Stars
        stars = [s for s in self.stars if s['type'] == 'star']
        dust = [s for s in self.stars if s['type'] == 'dust']
        
        for s in stars:
            # Local orbit movement?
            curr_angle = s['angle'] + rotation
             # + s['speed'] * 0.1 # Differential rotation inside the frame?
            
            x = cx + math.cos(curr_angle) * s['dist']
            y = cy + math.sin(curr_angle) * s['dist'] # Tilt? * 0.6
            
            # Simple 3D tilt effect
            y = cy + (y - cy) * 0.6
            
            p.setBrush(s['color'])
            p.drawEllipse(QPointF(x, y), s['size'], s['size'])
            
        # Draw Dust
        for d in dust:
            curr_angle = d['angle'] + rotation
            x = cx + math.cos(curr_angle) * d['dist']
            y = cy + math.sin(curr_angle) * d['dist']
            y = cy + (y - cy) * 0.6
            
            p.setBrush(d['color'])
            p.drawEllipse(QPointF(x, y), d['size'], d['size'])
