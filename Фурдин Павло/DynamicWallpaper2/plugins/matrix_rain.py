import random
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QFont, QFontMetrics

from effects import BaseEffect

class MatrixRainEffect(BaseEffect):
    EFFECT_NAME = "matrix_rain"

    def __init__(self):
        super().__init__()
        self.font_size = 20 # Optimized: Increased from 14
        self.cols = 0
        self.drops = []
        self.chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*"
        self.font = QFont("Courier New", self.font_size, QFont.Bold)
        self.speed_min = 5.0
        self.font = QFont("Courier New", self.font_size, QFont.Bold)
        self.speed_min = 5.0
        self.speed_max = 15.0

    @classmethod
    def get_schema(cls):
        return {
            "font_size": {
                "type": "int",
                "min": 8,
                "max": 100,
                "default": 20,
                "label": "Font Size"
            },
            "speed_min": {
                "type": "float",
                "min": 1.0,
                "max": 50.0,
                "default": 5.0,
                "label": "Min Speed"
            },
            "speed_max": {
                "type": "float",
                "min": 1.0,
                "max": 50.0,
                "default": 15.0,
                "label": "Max Speed"
            }
        }

    def configure(self, config: dict):
        if 'font_size' in config:
            self.font_size = int(config['font_size'])
            self.font = QFont("Courier New", self.font_size, QFont.Bold)
            self.drops = [] # Reset drops to re-calculate columns

        if 'speed_min' in config: self.speed_min = float(config['speed_min'])
        if 'speed_max' in config: self.speed_max = float(config['speed_max'])

    def _init_drops(self, w):
        self.cols = w // self.font_size
        self.drops = []
        for c in range(self.cols):
            self.drops.append({
                'y': random.uniform(-1000, 0),
                'speed': random.uniform(self.speed_min, self.speed_max),
                'chars': [random.choice(self.chars) for _ in range(15)], 
                'val': random.random() 
            })

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        # Semi-transparent black for trail fading effect
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(0, 0, 0, 50))
        
        if not self.drops:
            self._init_drops(w)
            
        p.setFont(self.font)
        
        for i, drop in enumerate(self.drops):
            x = i * self.font_size
            
            # Audio Reactivity
            audio_speed_boost = 0.0
            glitch_boost = 0.0
            mid_boost = 0.0
            
            if self.audio_data:
                audio_speed_boost = self.audio_data.get('bass', 0.0) * 20.0
                mid_boost = self.audio_data.get('mid', 0.0)
                glitch_boost = self.audio_data.get('treble', 0.0) * 0.2

            # Update position
            drop['y'] += drop['speed'] + audio_speed_boost
            
            # Reset if off screen
            if drop['y'] - 20 * self.font_size > h:
                drop['y'] = random.uniform(-100, 0)
                drop['speed'] = random.uniform(self.speed_min, self.speed_max)
                # Randomize chars again
                drop['chars'] = [random.choice(self.chars) for _ in range(15)]
            
            # Random character change (glitch effect)
            if random.random() < (0.05 + glitch_boost):
                 drop['chars'][0] = random.choice(self.chars)

            # Draw the trail
            for j, char in enumerate(drop['chars']):
                char_y = drop['y'] - j * self.font_size
                
                if char_y < 0 or char_y > h: continue
                
                # Head is white/bright green
                if j == 0:
                    val = 200 + int(mid_boost * 55)
                    p.setPen(QColor(val, 255, val))
                elif j < 5:
                    val = int(mid_boost * 100)
                    p.setPen(QColor(val, 255, val)) # Bright green + pulse
                else:
                    # Fade out tail
                    alpha = 255 - (j * 12)
                    if alpha < 0: alpha = 0
                    p.setPen(QColor(0, 150, 0, alpha))
                    
                p.drawText(QPointF(x, char_y), char)
