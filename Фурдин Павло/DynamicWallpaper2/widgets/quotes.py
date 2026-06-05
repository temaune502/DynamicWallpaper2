from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtCore import Qt, QRect
import math
import random
import time
from widgets import BaseWidget

class QuotesWidget(BaseWidget):
    WIDGET_NAME = "quotes"
    
    def __init__(self, config=None):
        super().__init__(config)
        self.quotes = self.config.get('quotes', [
            "Code is like humor. When you have to explain it, it’s bad.",
            "Fix the cause, not the symptom.",
            "Simplicity is the soul of efficiency.",
            "Make it work, make it right, make it fast.",
            "Knowledge is power."
        ])
        self.current_quote = random.choice(self.quotes)
        self.interval = self.config.get('interval', 15) # seconds
        self.last_switch = time.time()
        self.opacity = 1.0
        self.target_opacity = 1.0
        
    def draw(self, p: QPainter, w: int, h: int, phase: float = 0.0):
        now = time.time()
        
        # Switch quote logic
        if now - self.last_switch > self.interval:
            self.target_opacity = 0.0
            if self.opacity <= 0.05:
                self.current_quote = random.choice(self.quotes)
                self.last_switch = now
                self.target_opacity = 1.0
        
        # Smooth opacity transition
        if self.opacity < self.target_opacity:
            self.opacity += 0.02
        elif self.opacity > self.target_opacity:
            self.opacity -= 0.02
            
        # Draw setup
        font = QFont("Segoe UI Light", self.config.get('font_size', 14), QFont.Normal, True)
        p.setFont(font)
        
        # Wrapping text
        max_w = 300
        metrics = p.fontMetrics()
        rect = metrics.boundingRect(QRect(0, 0, max_w, 1000), Qt.TextWordWrap, self.current_quote)
        
        start_x, start_y = self.get_pos(w, h, rect.width(), rect.height())
        
        # Draw text with shadow
        color = QColor(255, 255, 255, int(200 * self.opacity))
        shadow = QColor(0, 0, 0, int(100 * self.opacity))
        
        p.setPen(shadow)
        p.drawText(QRect(start_x + 1, start_y + 1, max_w, rect.height()), Qt.TextWordWrap, self.current_quote)
        
        p.setPen(color)
        p.drawText(QRect(start_x, start_y, max_w, rect.height()), Qt.TextWordWrap, self.current_quote)
        
        # Draw a small decorative line
        line_glow = 0.5 + 0.5 * math.sin(phase * 2 * math.pi)
        p.setPen(QPen(QColor(0, 255, 255, int(150 * self.opacity * line_glow)), 1))
        p.drawLine(start_x, start_y - 5, start_x + 30, start_y - 5)
