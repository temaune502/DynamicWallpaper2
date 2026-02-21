import math
import random
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QPen

from effects import BaseEffect

class LaserNetEffect(BaseEffect):
    EFFECT_NAME = "laser_net"

    def __init__(self):
        super().__init__()
        self.nodes = []
        # Create grid of nodes
        for _ in range(40):
            self.nodes.append({
                'x': random.uniform(0, 1),
                'y': random.uniform(0, 1),
                'vx': random.uniform(-0.002, 0.002),
                'vy': random.uniform(-0.002, 0.002)
            })

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        # Dark Cyber background
        p.fillRect(0, 0, w, h, QColor(10, 5, 20))
        
        # Update nodes
        for node in self.nodes:
            node['x'] += node['vx']
            node['y'] += node['vy']
            
            # Bounce
            if node['x'] < 0 or node['x'] > 1: node['vx'] *= -1
            if node['y'] < 0 or node['y'] > 1: node['vy'] *= -1
            
        # Draw connections
        pen = QPen()
        max_dist = 0.2 # Max distance to connect (normalized)
        max_dist_sq = max_dist * max_dist
        
        # Pre-calc screen coords
        screen_nodes = [(n['x'] * w, n['y'] * h) for n in self.nodes]
        
        # Optimize: O(N^2) but N is small (40)
        for i in range(len(self.nodes)):
            x1, y1 = screen_nodes[i]
            
            # Draw node (glowing dot)
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 0, 100, 200)) # Pink/Red node
            p.drawEllipse(QPointF(x1, y1), 3, 3)
            
            for j in range(i + 1, len(self.nodes)):
                x2, y2 = screen_nodes[j]
                
                dx = self.nodes[i]['x'] - self.nodes[j]['x']
                dy = self.nodes[i]['y'] - self.nodes[j]['y']
                dist_sq = dx*dx + dy*dy
                
                if dist_sq < max_dist_sq:
                    # Alpha depends on distance
                    alpha = int((1.0 - (dist_sq / max_dist_sq)) * 200)
                    
                    # Laser color: shifting hue based on phase
                    # Simple color pulse
                    hue = (phase * 360 + (i * 10)) % 360
                    # For performance, just use fixed colors or simple lerp
                    # Let's use Cyan to Pink gradient
                    
                    pen_color = QColor(0, 200, 255, alpha)
                    pen.setColor(pen_color)
                    pen.setWidth(1)
                    p.setPen(pen)
                    p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
