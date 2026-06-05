import random
from PySide6.QtGui import QColor, QLinearGradient, QBrush
from PySide6.QtCore import Qt
from effects import BaseEffect

class CyberCityEffect(BaseEffect):
    EFFECT_NAME = "cyber_city"
    
    def __init__(self):
        super().__init__()
        self.building_count = 20
        self.buildings = None

    @classmethod
    def get_schema(cls):
        return {
            "count": {
                "type": "int",
                "min": 5,
                "max": 50,
                "default": 20,
                "label": "Building Count"
            }
        }

    def configure(self, config: dict):
        if 'count' in config:
            self.building_count = int(config['count'])
            self.buildings = [] # Force re-init

    def _init_city(self, h):
        self.buildings = []
        for i in range(self.building_count):
            bw = random.randint(60, 150)
            bh = random.randint(200, int(h // 1.5))
            self.buildings.append({'x': i * 100 - 100, 'w': bw, 'h': bh, 'speed': random.uniform(0.5, 1.5)})

    def draw(self, p, w, h, phase):
        if self.buildings is None:
            self._init_city(h) # type: ignore

        # Audio Reactivity
        bass = 0.0
        mid = 0.0
        treble = 0.0
        if self.audio_data:
            bass = self.audio_data.get('bass', 0.0)
            mid = self.audio_data.get('mid', 0.0)
            treble = self.audio_data.get('treble', 0.0)

        # Cyber sunset background
        if self.show_background:
            bg = QLinearGradient(0, 0, 0, h)
            # Modulate sky color with mid/treble
            r_top = min(255, 20 + int(mid * 100))
            b_bot = min(255, 100 + int(treble * 155))
            bg.setColorAt(0.0, QColor(r_top, 0, 40))
            bg.setColorAt(0.6, QColor(80, 0, 80))
            bg.setColorAt(1.0, QColor(255, 50, b_bot))
            p.fillRect(0, 0, w, h, QBrush(bg))

        # Retro sun
        sun_y = h // 2
        # Pulse sun radius with bass
        sun_r = 150 + int(bass * 50)
        
        for i in range(10):
            if (phase * 20 + i) % 10 > 2:
                p.setBrush(QColor(255, 200, 0, 200 - i * 15))
                p.setPen(Qt.NoPen)
                # Centered sun rect
                p.drawRect(w//2 - sun_r, sun_y + i * 20, sun_r * 2, 15)

        # Buildings
        for b in self.buildings: # type: ignore
            b['x'] = (b['x'] - b['speed'] - bass * 5.0) # Speed boost
            if b['x'] + b['w'] < 0: 
                b['x'] = w
                b['h'] = random.randint(200, int(h // 1.5))

            
            # Building silhouette
            p.setBrush(QColor(10, 10, 25, 240))
            p.drawRect(int(b['x']), h - b['h'], b['w'], b['h'])
            
            # Windows
            # Pulse window transparency with treble
            alpha = 100 + int(treble * 155)
            p.setBrush(QColor(0, 255, 255, alpha))
            
            # Draw windows (simplified loop)
            wx_start = int(b['x']) + 10
            wx_end = int(b['x'] + b['w']) - 10
            wy_start = h - b['h'] + 10
            
            for wx in range(wx_start, wx_end, 20):
                for wy in range(wy_start, h - 10, 30):
                    # Use deterministic random based on position so windows don't flicker
                    # unless we want them to flicker with beat? 
                    # Let's make them flicker if bass is high
                    seed = (wx * wy) % 100
                    threshold = 0.3
                    if bass > 0.5: threshold = 0.1 # More windows light up on drop
                    
                    if (seed / 100.0) > threshold:
                        p.drawRect(wx, wy, 10, 15)
