import math
import random
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QFont

from effects import BaseEffect

class BinaryVortexEffect(BaseEffect):
    EFFECT_NAME = "binary_vortex"

    def __init__(self):
        super().__init__()
        self.num_bits = 150
        self.hue_base = 120 # Green
        self.bits = []
        # Pre-populate
        for _ in range(self.num_bits):
            self._add_bit(start_far=True)

    @classmethod
    def get_schema(cls):
        return {
            "count": {
                "type": "int",
                "min": 50,
                "max": 1000,
                "default": 150,
                "label": "Bit Count"
            },
            "hue": {
                "type": "int",
                "min": 0,
                "max": 360,
                "default": 120,
                "label": "Color Hue"
            }
        }

    def configure(self, config: dict):
        if 'count' in config:
            self.num_bits = int(config['count'])
            # Adjust list size
            self.bits = []
            for _ in range(self.num_bits):
                self._add_bit(start_far=True)
                
        if 'hue' in config:
            self.hue_base = int(config['hue'])

    def _add_bit(self, start_far=False):
        angle = random.uniform(0, 360)
        dist = random.uniform(0.5, 1.5) if start_far else 1.5
        val = str(random.randint(0, 1))
        
        self.bits.append({
            'angle': angle,
            'dist': dist,
            'val': val,
            'speed': random.uniform(0.5, 2.0),
            'z': 0 # depth
        })

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        cx, cy = w / 2, h / 2
        max_r = min(w, h) * 0.8
        
        p.fillRect(0, 0, w, h, QColor(0, 0, 0))
        
        font = QFont("Courier New")
        
        new_bits = []
        for bit in self.bits:
            # Vortex motion: spirals INwards
            bit['dist'] -= 0.005
            bit['angle'] += (2.0 / (bit['dist'] + 0.1)) # Faster near center
            
            if bit['dist'] <= 0.05:
                # Re-spawn at edge if needed
                if len(new_bits) < self.num_bits:
                     self._add_bit()
                continue
            
            new_bits.append(bit)
            
            # Draw
            scale = bit['dist']
            screen_x = cx + math.cos(math.radians(bit['angle'])) * (max_r * scale)
            screen_y = cy + math.sin(math.radians(bit['angle'])) * (max_r * scale)
            
            # Size and Opacity based on distance (or inverse distance for vortex feel?)
            # Let's make them fade in as they approach center, then fade out instantly?
            # Standard vortex: big on outside, small inside? No, perspective: small inside (far), big outside (close)?
            # Let's do: "Singularity" style. Center is far away.
            # So dist=0 is Z=infinity (far), dist=1 is Z=0 (close)
            
            # Simple 2D spiral for now
            font_size = max(6, int(20 * bit['dist']))
            alpha = min(255, int(bit['dist'] * 255))
            
            # Matrix color
            # Hue from config, S=255, V=alpha
            color = QColor.fromHsv(self.hue_base, 255, 200)
            color.setAlpha(alpha)
            
            if font_size > 14:
                 color = QColor.fromHsv(self.hue_base, 200, 255) # Brighter
                 color.setAlpha(alpha)
            
            font.setPixelSize(font_size)
            p.setFont(font)
            p.setPen(color)
            p.drawText(int(screen_x), int(screen_y), bit['val'])
            
        self.bits = new_bits
