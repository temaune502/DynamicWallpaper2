import math
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QPen

from effects import BaseEffect

class DNAHelixEffect(BaseEffect):
    EFFECT_NAME = "dna_helix"

    def __init__(self):
        super().__init__()
        self.points = 40
        self.spacing = 30
        self.speed_mult = 1.0

    @classmethod
    def get_schema(cls):
        return {
            "points": {
                "type": "int",
                "min": 10,
                "max": 100,
                "default": 40,
                "label": "Length (Points)"
            },
            "spacing": {
                "type": "int",
                "min": 10,
                "max": 100,
                "default": 30,
                "label": "Spacing"
            },
            "speed": {
                "type": "float",
                "min": 0.1,
                "max": 5.0,
                "default": 1.0,
                "label": "Rotation Speed"
            }
        }

    def configure(self, config: dict):
        if 'points' in config: self.points = int(config['points'])
        if 'spacing' in config: self.spacing = int(config['spacing'])
        if 'speed' in config: self.speed_mult = float(config['speed'])

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        p.fillRect(0, 0, w, h, QColor(0, 0, 20))
        
        cx = w / 2
        cy = h / 2
        
        # Rotation
        t = phase * math.pi * 2 * self.speed_mult
        
        # Draw vertical helix
        total_height = self.points * self.spacing
        start_y = cy - total_height / 2
        
        p.setPen(Qt.NoPen)
        
        for i in range(self.points):
            y = start_y + i * self.spacing
            
            # Angle for this point
            angle = i * 0.5 + t
            
            # Radius
            r = 150
            
            # Strand 1
            x1 = cx + math.cos(angle) * r
            z1 = math.sin(angle) # Depth -1 to 1
            
            # Strand 2 (opposite)
            x2 = cx + math.cos(angle + math.pi) * r
            z2 = math.sin(angle + math.pi)
            
            # Color based on depth
            # Z: -1 (far, dark) to 1 (close, bright)
            
            # Draw connector line first
            alpha_line = 50
            p.setPen(QPen(QColor(0, 255, 255, alpha_line), 2))
            p.drawLine(QPointF(x1, y), QPointF(x2, y))
            p.setPen(Qt.NoPen)
            
            # Draw balls
            # Sort by Z manually? Or just draw based on size
            
            # Ball 1
            size1 = 10 + z1 * 5
            alpha1 = 150 + z1 * 100
            
            if z1 < 0:
                 col1 = QColor(0, 0, 255, int(alpha1))
            else:
                 col1 = QColor(0, 100, 255, int(alpha1))
                 
            p.setBrush(col1)
            p.drawEllipse(QPointF(x1, y), size1, size1)
            
            # Ball 2
            size2 = 10 + z2 * 5
            alpha2 = 150 + z2 * 100
            
            if z2 < 0:
                 col2 = QColor(255, 0, 0, int(alpha2))
            else:
                 col2 = QColor(255, 100, 0, int(alpha2))
                 
            p.setBrush(col2)
            p.drawEllipse(QPointF(x2, y), size2, size2)
