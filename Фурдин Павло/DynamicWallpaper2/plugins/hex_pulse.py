import math
from PySide6.QtGui import QColor, QPolygonF, QBrush, QPen
from PySide6.QtCore import Qt, QPointF
from effects import BaseEffect

class HexPulseEffect(BaseEffect):
    EFFECT_NAME = "hex_pulse"
    
    def __init__(self):
        super().__init__()
        self.hex_size = 40
        self.speed_mult = 1.0
        
    @classmethod
    def get_schema(cls):
        return {
            "size": {
                "type": "int",
                "min": 10,
                "max": 100,
                "default": 40,
                "label": "Hex Size"
            },
            "speed": {
                "type": "float",
                "min": 0.1,
                "max": 5.0,
                "default": 1.0,
                "label": "Pulse Speed"
            }
        }

    def configure(self, config: dict):
        if 'size' in config: self.hex_size = int(config['size'])
        if 'speed' in config: self.speed_mult = float(config['speed'])

    def draw(self, p, w, h, phase):
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(10, 10, 15))
            
        # Grid calculations
        # Hex width = sqrt(3) * size
        # Hex height = 2 * size
        # Horizontal spacing = width
        # Vertical spacing = 3/4 * height
        
        hex_w = math.sqrt(3) * self.hex_size
        hex_h = 2 * self.hex_size
        
        cols = int(w / hex_w) + 2
        rows = int(h / (hex_h * 0.75)) + 2
        
        cx, cy = w / 2, h / 2
        
        for r in range(rows):
            for c in range(cols):
                # Officet every odd row
                x_offset = (hex_w / 2) if (r % 2 == 1) else 0
                x = c * hex_w + x_offset
                y = r * (hex_h * 0.75)
                
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                
                # Pulse pattern
                # Waves rippling out from center
                val = math.sin(dist * 0.01 - phase * 3 * self.speed_mult)
                
                # Map -1..1 to brightness
                alpha = int(30 + (val + 1) * 0.5 * 100) # 30 to 130
                
                # Color based on radius too?
                hue = (int(dist * 0.2 + phase * 20 * self.speed_mult)) % 360
                color = QColor.fromHsv(hue, 200, 255, alpha)
                
                self._draw_hex(p, x, y, self.hex_size - 2, color)
                
    def _draw_hex(self, p, x, y, r, color):
        p.setBrush(color)
        p.setPen(Qt.NoPen)
        
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30 
            angle_rad = math.radians(angle_deg)
            px = x + r * math.cos(angle_rad)
            py = y + r * math.sin(angle_rad)
            points.append(QPointF(px, py))
            
        p.drawPolygon(QPolygonF(points))
