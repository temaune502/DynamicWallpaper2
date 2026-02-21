import math
import random
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QLinearGradient, QBrush, QPen, QPolygonF

from effects import BaseEffect

class AuroraBorealisEffect(BaseEffect):
    EFFECT_NAME = "aurora_borealis"

    def __init__(self):
        super().__init__()
        self.points = 100
        # Multiple layers of waves
        self.base_hue_min = 120
        self.base_hue_max = 180
        self.speed_factor = 1.0
        
        # Init layers
        self._init_layers()

        self._init_layers()

    @classmethod
    def get_schema(cls):
        return {
            "speed": {
                "type": "float",
                "min": 0.0,
                "max": 5.0,
                "default": 1.0,
                "label": "Speed"
            },
            "hue_min": {
                "type": "float",
                "min": 0.0,
                "max": 1.0,
                "default": 0.3,
                "label": "Hue Min"
            },
            "hue_max": {
                "type": "float",
                "min": 0.0,
                "max": 1.0,
                "default": 0.5,
                "label": "Hue Max"
            }
        }
        
    def configure(self, config: dict):
        if 'speed' in config: self.speed_factor = float(config['speed'])
        if 'hue_min' in config: self.base_hue_min = int(config['hue_min'])
        if 'hue_max' in config: self.base_hue_max = int(config['hue_max'])
        
        # Re-init layers
        self._init_layers()

    def _init_layers(self):
        self.layers = []
        for i in range(3):
            self.layers.append({
                'speed': random.uniform(0.005, 0.02) * (i + 1) * self.speed_factor,
                'amplitude': random.uniform(50, 150),
                'wavelength': random.uniform(0.01, 0.03),
                'y_offset': random.uniform(200, 400),
                'color_base': QColor.fromHsv(random.randint(self.base_hue_min, self.base_hue_max), 200, 255) 
            })

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        # Dark night sky background
        if self.show_background:
            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0, QColor(0, 5, 20))
            grad.setColorAt(1, QColor(10, 20, 40))
            p.fillRect(0, 0, w, h, grad)
        
        # Stars (static for now, could be dynamic)
        if not hasattr(self, 'stars'):
            self.stars = []
            for _ in range(200):
                self.stars.append(QPointF(random.uniform(0, w), random.uniform(0, h)))
                
        p.setPen(QColor(255, 255, 255, 150))
        p.setBrush(QColor(255, 255, 255, 150))
        for star in self.stars:
            p.drawEllipse(star, 1, 1)
            
        # Draw Aurora Layers
        # Use CompositionMode_Plus for additive blending (glowing effect)
        p.setCompositionMode(QPainter.CompositionMode_Screen) # Screen or Plus
        p.setPen(Qt.NoPen)
        
        step = w / self.points
        
        for layer in self.layers:
            # Shift phase per layer
            t = phase * 50 * layer['speed']
            
            # Construct polygon for the wave curtain
            poly_points = [QPointF(0, h), QPointF(0, h/2)] # Start bottom-left, then mid-left
            
            # Top edge of the curtain
            path_top = []
            for i in range(self.points + 1):
                x = i * step
                
                # Complex wave function: sum of sines
                noise = math.sin(x * layer['wavelength'] + t) + \
                        0.5 * math.sin(x * layer['wavelength'] * 2.5 - t) + \
                        0.25 * math.sin(x * layer['wavelength'] * 5.0 + t*2)
                        
                y = layer['y_offset'] + noise * layer['amplitude']
                
                # Y also varies over time globally
                y += math.sin(t * 0.5) * 50
                
                path_top.append(QPointF(x, y))
            
            # Close polygon down to bottom right
            poly_points = [QPointF(0, h)] + path_top + [QPointF(w, h)]
            
            # Gradient brush for the curtain (fade transparency upwards)
            # We want the color to be intense at the wave line and fade down? 
            # Actually auroras shoot UP or hang down. Let's make them hang down from the sky or rise?
            # Usually they are ribbons. Let's make vertical gradient for the ribbon.
            
            # Approximation: Just fill the area below the curve with a gradient that fades out
            # But "curtains" usually have vertical striations. 
            
            # Simpler approach: Vertical gradient fill of the wave shape
            # Top of wave = bright color
            # Bottom of screen = transparent or dark
            
            poly = QPolygonF(poly_points)
            
            # Dynamic color
            hue_shift = math.sin(t * 0.1) * 20
            color = QColor(layer['color_base'])
            h_val = color.hsvHue() + hue_shift
            color.setHsv(int(h_val % 360), 200, 255, 100) # Alpha 100
            
            color_transparent = QColor(color)
            color_transparent.setAlpha(0)
            
            # Gradient spanning the whole height
            wave_grad = QLinearGradient(0, layer['y_offset'] - 100, 0, h)
            wave_grad.setColorAt(0, color_transparent)
            wave_grad.setColorAt(0.2, color) # Brightest part near top
            wave_grad.setColorAt(1, color_transparent)
            
            p.setBrush(QBrush(wave_grad))
            p.drawPolygon(poly)
            
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)
