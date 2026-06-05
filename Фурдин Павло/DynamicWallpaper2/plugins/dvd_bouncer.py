import random
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QFont, QFontMetrics

from effects import BaseEffect

class DvdBouncerEffect(BaseEffect):
    EFFECT_NAME = "dvd_bouncer"

    def __init__(self):
        super().__init__()
        self.x = 100
        self.y = 100
        self.speed = 3.0
        self.vx = self.speed
        self.vy = self.speed
        self.width = 200
        self.height = 100
        self.color = QColor(255, 0, 0)
        self.text = "DVD"

    @classmethod
    def get_schema(cls):
        return {
            "speed": {
                "type": "float",
                "min": 1.0,
                "max": 20.0,
                "default": 3.0,
                "label": "Speed"
            }
        }

    def configure(self, config: dict):
        if 'speed' in config:
            self.speed = float(config['speed'])
            self.vx = self.speed if self.vx > 0 else -self.speed
            self.vy = self.speed if self.vy > 0 else -self.speed

    def _change_color(self):
        self.color = QColor.fromHsv(random.randint(0, 360), 255, 255)

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        p.fillRect(0, 0, w, h, QColor(0, 0, 0))
        
        # Physics
        self.x += self.vx
        self.y += self.vy
        
        hit = False
        if self.x <= 0:
            self.x = 0
            self.vx = abs(self.vx)
            hit = True
        elif self.x + self.width >= w:
            self.x = w - self.width
            self.vx = -abs(self.vx)
            hit = True
            
        if self.y <= 0:
            self.y = 0
            self.vy = abs(self.vy)
            hit = True
        elif self.y + self.height >= h:
            self.y = h - self.height
            self.vy = -abs(self.vy)
            hit = True
            
        if hit:
            self._change_color()
            
        # Draw Logo
        p.setPen(Qt.NoPen)
        p.setBrush(self.color)
        
        # Simple DVD shape approximation (Recall: Oval + Text)
        rect = QRectF(self.x, self.y, self.width, self.height)
        p.drawEllipse(rect)
        
        p.setPen(QColor(0, 0, 0))
        font = QFont("Arial", 40, QFont.Bold)
        p.setFont(font)
        p.drawText(rect, Qt.AlignCenter, "DVD")
        
        # Draw "Video" below
        font_small = QFont("Arial", 15, QFont.Bold)
        p.setFont(font_small)
        p.drawText(QRectF(self.x, self.y + self.height - 30, self.width, 30), Qt.AlignCenter, "VIDEO")
