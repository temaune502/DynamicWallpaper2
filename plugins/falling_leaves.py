import random
import math
from PySide6.QtGui import QColor, QBrush, QPen, QPolygonF
from PySide6.QtCore import Qt, QPointF
from effects import BaseEffect

class FallingLeavesEffect(BaseEffect):
    EFFECT_NAME = "falling_leaves"
    
    def __init__(self):
        super().__init__()
        self.leaves = []
        
    def draw(self, p, w, h, phase):
        # Soft autumn background
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(40, 30, 30))
            
        if not self.leaves:
            for _ in range(50):
                self.leaves.append(self._create_leaf(w, h))

        for leaf in self.leaves:
            # Move
            leaf['y'] += leaf['speed']
            leaf['x'] += math.sin(phase * 2 + leaf['sway_offset']) * 1.5
            leaf['rotation'] += leaf['rot_speed']
            
            # Reset
            if leaf['y'] > h + 50:
                self.leaves.remove(leaf)
                self.leaves.append(self._create_leaf(w, h, top=True))
                continue
                
            # Draw
            p.save()
            p.translate(leaf['x'], leaf['y'])
            p.rotate(leaf['rotation'])
            
            p.setPen(Qt.NoPen)
            p.setBrush(leaf['color'])
            
            # Simple leaf shape
            s = leaf['size']
            path = QPolygonF([
                QPointF(0, -s),
                QPointF(s * 0.5, 0),
                QPointF(0, s),
                QPointF(-s * 0.5, 0)
            ])
            p.drawPolygon(path)
            
            p.restore()

    def _create_leaf(self, w, h, top=False):
        # Autumn palette
        colors = [
            QColor(200, 100, 50),   # Rust
            QColor(220, 160, 60),   # Gold
            QColor(160, 60, 40),    # Red-brown
            QColor(120, 140, 60)    # Olive
        ]
        return {
            'x': random.uniform(0, w),
            'y': -50 if top else random.uniform(0, h),
            'size': random.uniform(10, 20),
            'speed': random.uniform(1, 3),
            'sway_offset': random.uniform(0, math.pi * 2),
            'rotation': random.uniform(0, 360),
            'rot_speed': random.uniform(-2, 2),
            'color': random.choice(colors)
        }
