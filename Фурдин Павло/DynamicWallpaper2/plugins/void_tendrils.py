import math
import random
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QCursor, QRadialGradient

from effects import BaseEffect

class VoidTendrilsEffect(BaseEffect):
    EFFECT_NAME = "void_tendrils"

    def __init__(self):
        super().__init__()
        self.tendrils = []
        self.num_tendrils = 15
        self.color_base = (20, 0, 40)
        self.color_tip = (255, 0, 0)
        
        # Create a pool of tendrils
        self._init_tendrils()

        # Create a pool of tendrils
        self._init_tendrils()

    @classmethod
    def get_schema(cls):
        return {
            "count": {
                "type": "int",
                "min": 1,
                "max": 50,
                "default": 15,
                "label": "Tendril Count"
            },
            "color_base": {
                "type": "color",
                "default": (20, 0, 40),
                "label": "Base Color"
            },
            "color_tip": {
                "type": "color",
                "default": (255, 0, 0),
                "label": "Tip Color"
            }
        }

    def configure(self, config: dict):
        if 'count' in config: self.num_tendrils = int(config['count'])
        if 'color_base' in config: self.color_base = tuple(config['color_base'])
        if 'color_tip' in config: self.color_tip = tuple(config['color_tip'])
        
        if 'count' in config:
            self._init_tendrils()
            
    def _init_tendrils(self):
        self.tendrils = []
        for _ in range(self.num_tendrils): 
            self.tendrils.append(self._create_tendril_state())

    def _create_tendril_state(self):
        # Pick a random edge position
        start_x, start_y = self._random_edge_pos()
        
        # IK Chain
        segments = []
        num_segments = 25
        seg_len = 20
        for _ in range(num_segments):
            segments.append({'x': start_x, 'y': start_y})
            
        return {
            'anchor_x': start_x,
            'anchor_y': start_y,
            'segments': segments,
            'seg_len': seg_len,
            'num': num_segments,
            'target_x': start_x,
            'target_y': start_y,
            'reach_speed': random.uniform(0.05, 0.15),
            'state': 'EMERGING', # EMERGING, ACTIVE, RETRACTING, HIDDEN
            'timer': 0,
            'opacity': 0.0,
            'width_scale': 1.0
        }

    def _random_edge_pos(self):
        # 1920x1080 bounds roughly
        side = random.randint(0, 3)
        if side == 0: # Top
            return random.uniform(0, 1920), -50
        elif side == 1: # Bottom
            return random.uniform(0, 1920), 1130
        elif side == 2: # Left
            return -50, random.uniform(0, 1080)
        else: # Right
            return 1970, random.uniform(0, 1080)

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(0, 0, 0)) 
        
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        
        # Vignette
        if self.show_background:
            grad = QRadialGradient(w/2, h/2, w)
            grad.setColorAt(0, QColor(0, 0, 0, 0))
            grad.setColorAt(0.8, QColor(0, 0, 0, 255))
        
        for t in self.tendrils:
            # --- State Machine ---
            t['timer'] += 1
            
            if t['state'] == 'EMERGING':
                t['opacity'] = min(1.0, t['opacity'] + 0.02)
                if t['opacity'] >= 1.0 and t['timer'] > 60:
                    t['state'] = 'ACTIVE'
                    t['timer'] = 0
                    
            elif t['state'] == 'ACTIVE':
                # Stay for random time then leave, OR random chance
                if t['timer'] > random.randint(200, 600):
                    t['state'] = 'RETRACTING'
                    
            elif t['state'] == 'RETRACTING':
                t['opacity'] = max(0.0, t['opacity'] - 0.02)
                # Pull anchor away? or just fade
                if t['opacity'] <= 0:
                    t['state'] = 'HIDDEN'
                    t['timer'] = 0
            
            elif t['state'] == 'HIDDEN':
                if t['timer'] > random.randint(50, 200):
                    # Respawn
                    nx, ny = self._random_edge_pos()
                    t['anchor_x'] = nx
                    t['anchor_y'] = ny
                    # Reset segments
                    for s in t['segments']:
                        s['x'] = nx
                        s['y'] = ny
                    t['target_x'] = nx
                    t['target_y'] = ny
                    t['state'] = 'EMERGING'
                    t['timer'] = 0
                    
            if t['state'] == 'HIDDEN':
                continue
                
            # --- IK Logic ---
            
            # Update Target
            dx = mx - t['target_x']
            dy = my - t['target_y']
            
            noise_x = math.sin(phase * 3 + t['anchor_y']) * 30
            noise_y = math.cos(phase * 3 + t['anchor_x']) * 30
            
            # If emerging, maybe don't reach full way?
            factor = 1.0
            if t['state'] == 'RETRACTING': factor = 0.1
            
            t['target_x'] += (dx * t['reach_speed'] + noise_x * 0.1) * factor
            t['target_y'] += (dy * t['reach_speed'] + noise_y * 0.1) * factor
            
            # FABRIK
            head = t['segments'][-1]
            head['x'] = t['target_x']
            head['y'] = t['target_y']
            
            # Drag backwards
            for i in range(t['num'] - 2, -1, -1):
                curr = t['segments'][i]
                next_seg = t['segments'][i+1]
                dx = curr['x'] - next_seg['x']
                dy = curr['y'] - next_seg['y']
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    scale = t['seg_len'] / dist
                    curr['x'] = next_seg['x'] + dx * scale
                    curr['y'] = next_seg['y'] + dy * scale
                    
            # Constrain root
            root = t['segments'][0]
            root['x'] = t['anchor_x']
            root['y'] = t['anchor_y']
            
            # Drag forwards
            for i in range(1, t['num']):
                curr = t['segments'][i]
                prev = t['segments'][i-1]
                dx = curr['x'] - prev['x']
                dy = curr['y'] - prev['y']
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    scale = t['seg_len'] / dist
                    curr['x'] = prev['x'] + dx * scale
                    curr['y'] = prev['y'] + dy * scale
            
            # Draw
            path_points = [QPointF(s['x'], s['y']) for s in t['segments']]
            
            
            base_alpha = int(255 * t['opacity'])
            color = QColor(*self.color_base)
            color.setAlpha(base_alpha)
            
            # Tapered line
            for i in range(len(path_points) - 1):
                width = (t['num'] - i) * 1.5 * t['opacity']
                p.setPen(QPen(color, width, Qt.SolidLine, Qt.RoundCap))
                p.drawLine(path_points[i], path_points[i+1])
                
            # Tip
            tip = path_points[-1]
            p.setPen(Qt.NoPen)
            tip_col = QColor(*self.color_tip)
            tip_col.setAlpha(int(200 * t['opacity']))
            p.setBrush(tip_col)
            p.drawEllipse(tip, 3, 3)
            
            p.drawEllipse(tip, 3, 3)
            
        if self.show_background:
            p.setBrush(QBrush(grad))
            p.setPen(Qt.NoPen)
            p.drawRect(0, 0, w, h)
