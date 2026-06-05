import math
import random
import ctypes
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QCursor

from effects import BaseEffect

# Mouse polling
user32 = ctypes.windll.user32

def is_left_clicked():
    return user32.GetAsyncKeyState(0x01) & 0x8000 != 0

def is_right_clicked():
    return user32.GetAsyncKeyState(0x02) & 0x8000 != 0

class CyberSwarmEffect(BaseEffect):
    EFFECT_NAME = "cyber_swarm"

    def __init__(self):
        super().__init__()
        self.num_particles = 80 # Optimization: Reduced from 120
        self.hue_min = 160
        self.hue_max = 240
        self.particles = []
        
        # Particle: x, y, vx, vy, size, hue
        for _ in range(self.num_particles):
            self.particles.append(self._create_particle())

    def _create_particle(self):
        return {
            'x': random.uniform(0, 1920),
            'y': random.uniform(0, 1080),
            'vx': random.uniform(-1, 1),
            'vy': random.uniform(-1, 1),
            'size': random.uniform(2, 4),
            'hue': random.randint(self.hue_min, self.hue_max) 
        }

        # Particle: x, y, vx, vy, size, hue
        for _ in range(self.num_particles):
            self.particles.append(self._create_particle())

    @classmethod
    def get_schema(cls):
        return {
            "count": {
                "type": "int",
                "min": 10,
                "max": 500,
                "default": 80,
                "label": "Particle Count"
            },
            "hue_min": {
                "type": "int",
                "min": 0,
                "max": 360,
                "default": 160,
                "label": "Hue Min"
            },
            "hue_max": {
                "type": "int",
                "min": 0,
                "max": 360,
                "default": 240,
                "label": "Hue Max"
            }
        }

    def configure(self, config: dict):
        if 'count' in config:
            self.num_particles = int(config['count'])
            # Re-init particles
            self.particles = []
            for _ in range(self.num_particles):
                self.particles.append(self._create_particle())
                
        if 'hue_min' in config: self.hue_min = int(config['hue_min'])
        if 'hue_max' in config: self.hue_max = int(config['hue_max'])

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        # 1. Background
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(5, 10, 20))
        
        # 2. Input
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        l_click = is_left_clicked()
        r_click = is_right_clicked()
        
        # 3. Optimization Setup
        neighbor_dist = 100
        neighbor_sq = neighbor_dist * neighbor_dist
        mouse_range_sq = 300 * 300
        separation_dist = 30
        
        p.setRenderHint(QPainter.Antialiasing)
        
        # Accumulators for flocking (Cohesion/Alignment)
        # We accumulate sums, then divide by count later
        N = len(self.particles)
        # [sum_vx, sum_vy, sum_x, sum_y, count]
        flock_data = [[0.0, 0.0, 0.0, 0.0, 0] for _ in range(N)]
        
        # O(N^2 / 2) Loop for pair-wise interactions
        for i in range(N):
            p1 = self.particles[i]
            
            for j in range(i + 1, N):
                p2 = self.particles[j]
                
                dx = p2['x'] - p1['x']
                dy = p2['y'] - p1['y']
                
                # Fast box check check before square (optional but good)
                if abs(dx) > neighbor_dist or abs(dy) > neighbor_dist:
                    continue
                    
                dist_sq = dx*dx + dy*dy
                if dist_sq < neighbor_sq:
                    dist = math.sqrt(dist_sq)
                    if dist < 0.1: dist = 0.1 # Avoid division by zero
                    
                    # 1. Accumulate Flocking Info for BOTH
                    # P1 sees P2
                    fd1 = flock_data[i]
                    fd1[0] += p2['vx']
                    fd1[1] += p2['vy']
                    fd1[2] += p2['x']
                    fd1[3] += p2['y']
                    fd1[4] += 1
                    
                    # P2 sees P1
                    fd2 = flock_data[j]
                    fd2[0] += p1['vx']
                    fd2[1] += p1['vy']
                    fd2[2] += p1['x']
                    fd2[3] += p1['y']
                    fd2[4] += 1
                    
                    # 2. Separation (Apply force immediately to both)
                    if dist < separation_dist:
                        force = 0.5 / dist
                        fx = dx * force
                        fy = dy * force
                        
                        # P1 moves away from P2 (minus direction of P1->P2)
                        p1['vx'] -= fx
                        p1['vy'] -= fy
                        
                        # P2 moves away from P1 (plus direction)
                        p2['vx'] += fx
                        p2['vy'] += fy

                    # 3. Draw Connection (Once per pair!)
                    alpha = int(150 * (1.0 - dist / neighbor_dist))
                    if alpha > 0:
                        p.setPen(QPen(QColor(100, 200, 255, alpha), 1))
                        p.drawLine(QPointF(p1['x'], p1['y']), QPointF(p2['x'], p2['y']))

        # Apply Flocking & Mouse & Integration
        for i in range(N):
            pt = self.particles[i]
            fd = flock_data[i]
            count = fd[4]
            
            # Apply gathered flocking forces
            if count > 0:
                avg_vx = fd[0] / count
                avg_vy = fd[1] / count
                avg_x = fd[2] / count
                avg_y = fd[3] / count
                
                # Alignment
                pt['vx'] += (avg_vx - pt['vx']) * 0.05
                pt['vy'] += (avg_vy - pt['vy']) * 0.05
                
                # Cohesion
                pt['vx'] += (avg_x - pt['x']) * 0.005
                pt['vy'] += (avg_y - pt['y']) * 0.005
            
            # Mouse Interaction
            dx = mx - pt['x']
            dy = my - pt['y']
            dist_sq = dx*dx + dy*dy
            
            if dist_sq < mouse_range_sq:
                dist = math.sqrt(dist_sq)
                if dist > 1.0: # Check dist to avoid /0
                    factor = (1.0 - dist / 300.0)
                    if l_click:
                        pt['vx'] += (dx / dist) * 1.5 * factor
                        pt['vy'] += (dy / dist) * 1.5 * factor
                    elif r_click:
                        pt['vx'] -= (dx / dist) * 4.0 * factor
                        pt['vy'] -= (dy / dist) * 4.0 * factor
                    else:
                        pt['vx'] += (dx / dist) * 0.2 * factor
                        pt['vy'] += (dy / dist) * 0.2 * factor
                        pt['vx'] += (dy / dist) * 0.5 * factor
                        pt['vy'] -= (dx / dist) * 0.5 * factor

            # Speed Limit & Integration
            speed = math.sqrt(pt['vx']**2 + pt['vy']**2)
            max_speed = 8.0 if l_click else 4.0
            if speed > max_speed:
                scale = max_speed / speed
                pt['vx'] *= scale
                pt['vy'] *= scale
                
            pt['x'] += pt['vx']
            pt['y'] += pt['vy']
            
            # Wrap
            if pt['x'] < 0: pt['x'] = w
            if pt['x'] > w: pt['x'] = 0
            if pt['y'] < 0: pt['y'] = h
            if pt['y'] > h: pt['y'] = 0
            
            # Draw Particle
            color = QColor.fromHsv(pt['hue'], 200, 255)
            pulse = math.sin(phase * 5 + i) * 1.0
            size = max(2, pt['size'] + pulse) # Ensure size doesn't go below 2
            
            if speed > 3.0:
                 p.setBrush(QColor(255, 255, 255, 100))
                 p.setPen(Qt.NoPen)
                 p.drawEllipse(QPointF(pt['x'], pt['y']), size * 2, size * 2)
            
            p.setBrush(color)
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(pt['x'], pt['y']), size, size)
            
        # Draw Mouse Interaction Lines (once, after all particles are processed)
        if l_click:
            p.setPen(QPen(QColor(255, 50, 50, 100), 1, Qt.DashLine))
            p.drawLine(0, my, w, my)
            p.drawLine(mx, 0, mx, h)
