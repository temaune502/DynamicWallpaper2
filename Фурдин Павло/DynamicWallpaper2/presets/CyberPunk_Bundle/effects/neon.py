from src.effects.base import BaseEffect, QColor, QRadialGradient, QPointF

class NeonPulse(BaseEffect):
    EFFECT_NAME = "neon_pulse"
    
    def __init__(self):
        super().__init__()
        self.speed = 1.0
        self.color = QColor(0, 255, 255)
        
    def configure(self, config):
        self.speed = config.get("speed", 1.0)
        c = config.get("color", [0, 255, 255])
        self.color = QColor(c[0], c[1], c[2])
        
    def draw(self, p, w, h, phase):
        # Draw a pulsing neon grid or circle
        cx, cy = w / 2, h / 2
        radius = min(w, h) * 0.4
        
        pulse = (phase * self.speed * 10) % 2.0
        if pulse > 1.0: pulse = 2.0 - pulse
        
        # Background
        p.fillRect(0, 0, w, h, QColor(10, 10, 20))
        
        # Gradient Circle
        grad = QRadialGradient(cx, cy, radius * (0.8 + pulse * 0.2))
        grad.setColorAt(0, self.color)
        grad.setColorAt(0.5, QColor(0, 0, 0, 0))
        grad.setColorAt(1, QColor(0, 0, 0, 0))
        
        p.fillRect(0, 0, w, h, grad)
        
        # Grid lines
        p.setPen(QColor(self.color.red(), self.color.green(), self.color.blue(), 50))
        step = 50
        offset = phase * w * self.speed
        
        for x in range(0, w, step):
            p.drawLine(x, 0, x, h)
        for y in range(0, h, step):
            p.drawLine(0, y, w, y)
