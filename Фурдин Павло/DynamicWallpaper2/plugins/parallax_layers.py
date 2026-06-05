import random
import math
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QCursor, QBrush, QPen

from effects import BaseEffect

class ParallaxLayersEffect(BaseEffect):
    EFFECT_NAME = "parallax_layers"

    def __init__(self):
        super().__init__()
        self.layers = []
        # Create 3 layers
        for layer_idx in range(3):
            shapes = []
            count = 20 - layer_idx * 5 # Fewer shapes in front
            depth = (layer_idx + 1) * 0.5 # 0.5, 1.0, 1.5 multiplier
            
            for _ in range(count):
                shapes.append({
                    'x': random.uniform(0, 1920),
                    'y': random.uniform(0, 1080),
                    'size': random.uniform(20, 100) * (layer_idx + 1),
                    'color': QColor.fromHsv(random.randint(0, 360), 100 + layer_idx * 50, 200),
                    'type': random.choice(['circle', 'rect'])
                })
            self.layers.append({'depth': depth, 'shapes': shapes})

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        # Mouse interaction for parallax
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        
        # Calculate offset based on center
        cx, cy = w / 2, h / 2
        off_x = (mx - cx) / cx
        off_y = (my - cy) / cy
        
        # Clamp offset
        off_x = max(-1, min(1, off_x))
        off_y = max(-1, min(1, off_y))
        
        # Background
        p.fillRect(0, 0, w, h, QColor(20, 20, 25))
        
        p.setPen(Qt.NoPen)
        
        # Draw layers from back to front
        for layer in self.layers:
            depth = layer['depth']
            # Movement: deeper layers move LESS? Or MORE?
            # Standard parallax: background moves slower than foreground.
            # But here we want the "window" effect:
            # If we move mouse right, we look "left", so everything moves left.
            # Foreground moves MORE left than background.
            
            shift_x = -off_x * 50 * depth
            shift_y = -off_y * 50 * depth
            
            for s in layer['shapes']:
                p.setBrush(s['color'])
                
                # Check wrap around roughly
                draw_x = (s['x'] + shift_x) % (w + 200) - 100
                draw_y = (s['y'] + shift_y) % (h + 200) - 100
                
                if s['type'] == 'circle':
                    p.drawEllipse(QPointF(draw_x, draw_y), s['size'], s['size'])
                else:
                    p.drawRect(draw_x, draw_y, s['size'], s['size'])
