import random
import math
from PySide6.QtGui import QColor, QFont, QPen
from PySide6.QtCore import Qt
from effects import BaseEffect

class DigitalRainEffect(BaseEffect):
    EFFECT_NAME = "digital_rain"
    
    def __init__(self):
        super().__init__()
        self.columns = None
        self.font = QFont("Monospace", 12, QFont.Bold)
        self.chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$+-*/=%\"'#&_(),.;:?!"
        self.glyphs = "アカサタナハマヤラワガザダバパイキシチニヒミリギジヂビピウクスツヌフムユルグズヅブプエケセテネヘメレゲゼデベペオコソトノホモヨロヲゴゾドボポ"

    def draw(self, p, w, h, phase):
        if self.columns is None:
            char_w = 15
            num_cols = int(w / char_w) + 1
            self.columns = []
            for i in range(num_cols):
                self.columns.append({
                    'x': i * char_w,
                    'y': random.uniform(-h, 0),
                    'speed': random.uniform(2, 6),
                    'chars': [],
                    'length': random.randint(10, 25)
                })

        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(0, 5, 0))

        p.setFont(self.font)
        
        for col in self.columns:
            col['y'] += col['speed']
            if col['y'] - (col['length'] * 15) > h:
                col['y'] = random.uniform(-200, 0)
                col['speed'] = random.uniform(2, 6)
                col['length'] = random.randint(10, 25)

            # Draw the tail
            for i in range(col['length']):
                char_y = col['y'] - (i * 15)
                if char_y < -20 or char_y > h + 20:
                    continue

                # Fade out color
                alpha = int(255 * (1 - i / col['length']))
                if i == 0:
                    color = QColor(200, 255, 200, alpha) # Bright lead char
                else:
                    color = QColor(0, 255, 70, alpha)

                # Randomly change characters
                if random.random() < 0.05:
                    char = random.choice(self.glyphs)
                else:
                    char = random.choice(self.chars) if random.random() < 0.5 else random.choice(self.glyphs)

                p.setPen(color)
                p.drawText(int(col['x']), int(char_y), char)

        # Subtle scanlines
        p.setPen(QPen(QColor(0, 20, 0, 40), 1))
        for y in range(0, h, 3):
            p.drawLine(0, y, w, y)
