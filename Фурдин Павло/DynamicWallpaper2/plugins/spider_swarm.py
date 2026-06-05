import random
import math
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QCursor, QPen, QBrush

from effects import BaseEffect

class SpiderSwarmEffect(BaseEffect):
    EFFECT_NAME = "spider_swarm"

    def __init__(self):
        super().__init__()
        self.num_spiders = 100
        self.color_spider = (10, 10, 10)
        self.color_eyes = (255, 0, 0)
        self.spiders = []
        self._init_spiders()
        
        self.spiders = []
        self._init_spiders()
        
    @classmethod
    def get_schema(cls):
        return {
            "count": {
                "type": "int",
                "min": 10,
                "max": 500,
                "default": 100,
                "label": "Spider Count"
            },
            "color_body": {
                "type": "color",
                "default": (10, 10, 10),
                "label": "Body Color"
            },
            "color_eyes": {
                "type": "color",
                "default": (255, 0, 0),
                "label": "Eye Color"
            }
        }

    def configure(self, config: dict):
        if 'count' in config: self.num_spiders = int(config['count'])
        if 'color_body' in config: self.color_spider = tuple(config['color_body'])
        if 'color_eyes' in config: self.color_eyes = tuple(config['color_eyes'])
        
        if 'count' in config:
            self._init_spiders()

    def _init_spiders(self):
        self.spiders = []
        for _ in range(self.num_spiders):
            self.spiders.append(self._create_spider())
            
        self.last_mouse_pos = None
        self.mouse_speed = 0

    def _create_spider(self):
        return {
            'x': random.uniform(0, 1920),
            'y': random.uniform(0, 1080),
            'vx': 0,
            'vy': 0,
            'angle': random.uniform(0, math.pi * 2),
            'speed': random.uniform(2, 5),
            'size': random.uniform(3, 5),
            'leg_phase': random.random() # For animation
        }

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(20, 15, 15)) # Dark, slightly reddish bg
        
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        
        # Calculate mouse speed
        if self.last_mouse_pos:
            dx = mx - self.last_mouse_pos.x()
            dy = my - self.last_mouse_pos.y()
            dist = math.sqrt(dx*dx + dy*dy)
            self.mouse_speed = self.mouse_speed * 0.8 + dist * 0.2
        self.last_mouse_pos = mouse_pos
        
        flee_mode = self.mouse_speed > 20.0
        
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 0, 0))
        
        for i, s in enumerate(self.spiders):
            dx = mx - s['x']
            dy = my - s['y']
            dist = math.sqrt(dx*dx + dy*dy)
            angle_to_mouse = math.atan2(dy, dx)
            
            target_angle = s['angle']
            target_speed = 0
            
            # --- Flocking: Separation (Don't clump!) ---
            sep_x = 0
            sep_y = 0
            separation_dist = 30 # Maintain this distance
            
            # Check against other spiders
            # Optimization: Not N^2 every frame if possible, but N=100 is fine (10k ops)
            count = 0
            for j, other in enumerate(self.spiders):
                if i == j: continue
                sdx = s['x'] - other['x']
                sdy = s['y'] - other['y']
                sdist_sq = sdx*sdx + sdy*sdy
                
                if sdist_sq < separation_dist**2 and sdist_sq > 0:
                     # Push away
                     sdist = math.sqrt(sdist_sq)
                     force = (separation_dist - sdist) / separation_dist
                     sep_x += (sdx / sdist) * force * 5.0 # Weight of separation
                     sep_y += (sdy / sdist) * force * 5.0
                     count += 1
            
            if flee_mode:
                # Flee!
                if dist < 400:
                    target_angle = angle_to_mouse + math.pi # Away
                    target_speed = s['speed'] * 3.0
                else:
                    target_speed = s['speed'] * 0.5
                    target_angle = s['angle'] + random.uniform(-0.1, 0.1)
            else:
                # Hunt (Swarm) if close enough/visible
                if dist < 600:
                    target_angle = angle_to_mouse
                    target_speed = s['speed'] * 1.5
                    
                    if dist < 60: # Circle/Stop distance
                        target_speed = s['speed'] * 0.2
                        target_angle += math.pi / 2 # Circle?
                else:
                     target_speed = s['speed'] * 0.2
                     target_angle = s['angle'] + random.uniform(-0.1, 0.1)
            
            # Apply Separation
            # We treat separation as a nudge to the desired angle/velocity
            # OR we simply modify x/y directly (simpler collision) 
            # OR we modify vx/vy. 
            # Let's modify the target movement vector.
            
            move_vx = math.cos(target_angle) * target_speed
            move_vy = math.sin(target_angle) * target_speed
            
            final_vx = move_vx + sep_x
            final_vy = move_vy + sep_y
            
            # Turn towards final vector
            final_angle = math.atan2(final_vy, final_vx)
            final_speed = math.sqrt(final_vx**2 + final_vy**2)
            
            # Smooth turn
            diff = final_angle - s['angle']
            while diff > math.pi: diff -= 2*math.pi
            while diff < -math.pi: diff += 2*math.pi
            s['angle'] += diff * 0.1
            
            # Move
            s['vx'] = math.cos(s['angle']) * final_speed
            s['vy'] = math.sin(s['angle']) * final_speed
            
            s['x'] += s['vx']
            s['y'] += s['vy']
            
            # Keep in bounds
            s['x'] = max(0, min(w, s['x']))
            s['y'] = max(0, min(h, s['y']))
            
            # Animate Legs?
            moving = final_speed > 0.1
            if moving:
                s['leg_phase'] += 0.5
            
            # Draw Spider
            p.save()
            p.translate(s['x'], s['y'])
            p.rotate(math.degrees(s['angle']))
            
            
            # Body
            p.setBrush(QColor(*self.color_spider))
            p.drawEllipse(QPointF(0, 0), s['size'], s['size'] * 0.8)
            
            # Eyes (Glowing red dots)
            p.setBrush(QColor(*self.color_eyes))
            p.drawEllipse(QPointF(2, -1), 1, 1)
            p.drawEllipse(QPointF(2, 1), 1, 1)
            
            # Legs
            p.setPen(QPen(QColor(0, 0, 0), 1))
            leg_len = s['size'] * 2.5
            
            for k in range(4): # 4 pairs
                side_angle = 45 + k * 20
                rad = math.radians(side_angle)
                
                # Leg wiggle
                wiggle = math.sin(s['leg_phase'] + k) * 0.5 * (1 if moving else 0)
                
                # Left leg
                lx = math.cos(-rad + wiggle) * leg_len
                ly = math.sin(-rad + wiggle) * leg_len
                p.drawLine(0, 0, lx, ly)
                
                # Right leg
                rx = math.cos(rad - wiggle) * leg_len
                ry = math.sin(rad - wiggle) * leg_len
                p.drawLine(0, 0, rx, ry)
                
            p.restore()
