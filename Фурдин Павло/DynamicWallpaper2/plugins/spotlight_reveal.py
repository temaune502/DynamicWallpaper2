import random
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QCursor, QRadialGradient, QBrush, QFont

from effects import BaseEffect

class SpotlightRevealEffect(BaseEffect):
    EFFECT_NAME = "spotlight_reveal"

    def __init__(self):
        super().__init__()
        self.words = ["PYTHON", "TEMAUNE","CODE", "MAGIC", "SYSTEM", "KERNEL", "DATA", "NET", "CYBER"]
        self.bg_items = []
        for _ in range(200):
            self.bg_items.append({
                'x': random.uniform(0, 1920),
                'y': random.uniform(0, 1080),
                'text': random.choice(self.words),
                'size': random.randint(10, 30),
                'color': QColor.fromHsv(random.randint(0, 360), 200, 255)
            })

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        # 1. Fill black (The darkness)
        p.fillRect(0, 0, w, h, QColor(0, 0, 0))
        
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        
        # 2. Define Spotlight Gradient
        radius = 300
        grad = QRadialGradient(mx, my, radius)
        grad.setColorAt(0, QColor(255, 255, 255, 255)) # Center opaque
        grad.setColorAt(1, QColor(0, 0, 0, 0))       # Edge transparent
        
        # We want to draw items ONLY where the spotlight is.
        # But standard drawing + clipping is easier.
        
        # Let's clip to the spotlight circle? 
        # Or easier: Draw everything faintly, and draw bright where mouse is.
        
        # Optimization: Only draw items close to mouse
        p.setPen(Qt.NoPen)
        
        font = QFont("Courier New", 10, QFont.Bold)
        p.setFont(font)
        
        for item in self.bg_items:
            dx = item['x'] - mx
            dy = item['y'] - my
            dist = dx*dx + dy*dy
            
            if dist < radius*radius:
                # Calculate alpha based on distance
                alpha = 255 * (1 - dist / (radius*radius))
                col = QColor(item['color'])
                col.setAlpha(int(alpha))
                
                p.setPen(col)
                font.setPointSize(item['size'])
                p.setFont(font)
                p.drawText(QPointF(item['x'], item['y']), item['text'])
