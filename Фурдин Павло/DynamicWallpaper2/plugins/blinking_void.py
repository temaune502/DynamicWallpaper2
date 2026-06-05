import random
import math
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QCursor

from effects import BaseEffect

class BlinkingVoidEffect(BaseEffect):
    EFFECT_NAME = "blinking_void"

    def __init__(self):
        super().__init__()
        self.num_eyes = 30
        self.blink_chance = 0.01
        self.eyes = []
        self._init_eyes()

    def _init_eyes(self):
        self.eyes = []
        # Pool of eyes
        for _ in range(self.num_eyes):
            self.eyes.append(self._create_eye())

    @classmethod
    def get_schema(cls):
        return {
            "count": {
                "type": "int",
                "min": 5,
                "max": 100,
                "default": 30,
                "label": "Eye Count"
            },
            "blink_chance": {
                "type": "float",
                "min": 0.001,
                "max": 0.1,
                "default": 0.01,
                "label": "Blink Chance"
            }
        }

    def configure(self, config: dict):
        if 'count' in config:
            self.num_eyes = int(config['count'])
            self._init_eyes()
        if 'blink_chance' in config:
            self.blink_chance = float(config['blink_chance'])

    def _create_eye(self):
        return {
            'x': random.uniform(50, 1870),
            'y': random.uniform(50, 1030),
            'size': random.uniform(20, 50),
            'state': 'CLOSED', # CLOSED, OPENING, OPEN, CLOSING
            'lid_open': 0.0, # 0.0 to 1.0
            'timer': random.randint(0, 100) # Random start offset
        }

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        p.fillRect(0, 0, w, h, QColor(0, 0, 0))
        
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        
        # Draw eyes
        for eye in self.eyes:
            # Logic
            eye['timer'] -= 1
            
            if eye['state'] == 'CLOSED':
                if eye['timer'] <= 0:
                    eye['state'] = 'OPENING'
                    # Relocate sometimes
                    if random.random() < 0.5:
                         eye['x'] = random.uniform(50, w-50)
                         eye['y'] = random.uniform(50, h-50)
            
            elif eye['state'] == 'OPENING':
                eye['lid_open'] += 0.1
                if eye['lid_open'] >= 1.0:
                    eye['lid_open'] = 1.0
                    eye['state'] = 'OPEN'
                    eye['timer'] = random.randint(50, 200) # Stay open for a bit
            
            elif eye['state'] == 'OPEN':
                if eye['timer'] <= 0:
                    eye['state'] = 'CLOSING'
                # Occasional blink
                if random.random() < self.blink_chance:
                    eye['state'] = 'CLOSING'
                    
            elif eye['state'] == 'CLOSING':
                 eye['lid_open'] -= 0.1
                 if eye['lid_open'] <= 0.0:
                     eye['lid_open'] = 0.0
                     eye['state'] = 'CLOSED'
                     eye['timer'] = random.randint(20, 100)
            
            # Draw if partially open
            if eye['lid_open'] > 0.01:
                # Sclera (White part)
                # Draw as an ellipse clipped by eyelids? 
                # Simpler: Draw Sclera, then Pupil, then draw Eyelids (black) on top
                
                size = eye['size']
                
                # 1. Background Sclera
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(200, 200, 200))
                p.drawEllipse(QPointF(eye['x'], eye['y']), size, size * 0.6)
                
                # 2. Pupil (Tracks mouse)
                dx = mx - eye['x']
                dy = my - eye['y']
                dist = math.sqrt(dx*dx + dy*dy)
                angle = math.atan2(dy, dx)
                
                # Limit pupil movement
                pupil_dist = min(dist, size * 0.4)
                px = eye['x'] + math.cos(angle) * pupil_dist
                py = eye['y'] + math.sin(angle) * pupil_dist * 0.6
                
                p.setBrush(QColor(0, 0, 0))
                p.drawEllipse(QPointF(px, py), size * 0.3, size * 0.3)
                
                # Highlight
                p.setBrush(QColor(255, 255, 255))
                p.drawEllipse(QPointF(px - size*0.1, py - size*0.1), size * 0.1, size * 0.1)
                
                # 3. Eyelids (Black rects/arcs to cover)
                # Top Lid
                p.setBrush(QColor(0, 0, 0))
                lid_height = size * 0.6 * (1.0 - eye['lid_open'])
                
                # Simple rect approach for lids
                # Top
                p.drawRect(eye['x'] - size, eye['y'] - size * 0.6, size * 2, lid_height)
                # Bottom
                p.drawRect(eye['x'] - size, eye['y'] + size * 0.6 - lid_height, size * 2, lid_height)
