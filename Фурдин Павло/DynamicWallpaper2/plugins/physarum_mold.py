import random
import math
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QCursor, QImage, QPainterPath

from effects import BaseEffect

class PhysarumMoldEffect(BaseEffect):
    EFFECT_NAME = "physarum_mold"

    def __init__(self):
        super().__init__()
        self.particles = []
        self.num_particles = 300
        # Initialize particles in center
        for _ in range(self.num_particles):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(0, 100)
            self.particles.append({
                'x': 960 + math.cos(angle) * dist,
                'y': 540 + math.sin(angle) * dist,
                'angle': angle,
                'color': QColor.fromHsv(random.randint(100, 150), 200, 255) # Green slime
            })
        
        # Grid to store trails (simplified)
        # Using a QImage? No, just particle positions and decay?
        # A true physarum needs a grid for sensing. 
        # Without a grid, let's fake it with simple particle rules + mouse attraction.
        
        self.sensor_angle = math.pi / 4
        self.sensor_dist = 20

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        # Translucent black background for trail effect
        p.fillRect(0, 0, w, h, QColor(0, 0, 0, 20))
        
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        
        p.setPen(Qt.NoPen)
        
        for pt in self.particles:
            # 1. Sense / Steer to Mouse
            dx = mx - pt['x']
            dy = my - pt['y']
            dist = math.sqrt(dx*dx + dy*dy)
            angle_to_mouse = math.atan2(dy, dx)
            
            # If close, spiral
            if dist < 100:
                 target_angle = angle_to_mouse + math.pi / 2
                 speed = 3.0
            elif dist < 600:
                 # Move towards mouse with noise
                 target_angle = angle_to_mouse + random.uniform(-0.5, 0.5)
                 speed = 4.0
            else:
                 # Wander
                 target_angle = pt['angle'] + random.uniform(-0.2, 0.2)
                 speed = 2.0
            
            # Smooth turn
            diff = target_angle - pt['angle']
            while diff > math.pi: diff -= 2*math.pi
            while diff < -math.pi: diff += 2*math.pi
            
            pt['angle'] += diff * 0.1
            
            # Move
            pt['x'] += math.cos(pt['angle']) * speed
            pt['y'] += math.sin(pt['angle']) * speed
            
            # Bounce
            if pt['x'] < 0 or pt['x'] > w: 
                pt['angle'] = math.pi - pt['angle']
                pt['x'] = max(0, min(w, pt['x']))
            if pt['y'] < 0 or pt['y'] > h: 
                pt['angle'] = -pt['angle']
                pt['y'] = max(0, min(h, pt['y']))
            
            # Draw
            # Draw trail?
            p.setBrush(pt['color'])
            p.drawEllipse(QPointF(pt['x'], pt['y']), 2, 2)
            
        # Draw "Mold Network" connecting close particles
        # Only occasional connections to simulate structure
        p.setPen(QPen(QColor(100, 255, 100, 30), 1))
        
        # Spatial partitioning optimization needed for large N
        # For N=300, N^2/2 is 45k checks. Do-able but careful.
        # Just check neighbor in list?
        
        for i in range(len(self.particles)):
             p1 = self.particles[i]
             # Check next few
             for j in range(1, 5):
                 idx = (i + j) % self.num_particles
                 p2 = self.particles[idx]
                 
                 dx = p1['x'] - p2['x']
                 dy = p1['y'] - p2['y']
                 if dx*dx + dy*dy < 2500: # 50px
                     p.drawLine(QPointF(p1['x'], p1['y']), QPointF(p2['x'], p2['y']))
