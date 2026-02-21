import math
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QPen, QLinearGradient

from effects import BaseEffect

class SynthwaveTerrainEffect(BaseEffect):
    EFFECT_NAME = "synthwave_terrain"

    def __init__(self):
        super().__init__()
        self.grid_spacing = 50
        self.horizon_y = 0.0 # Will be set in draw
        self.speed = 2.0
        self.offset_z = 0.0

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        self.horizon_y = h * 0.4
        
        # 1. Sky (Gradient)
        sky_grad = QLinearGradient(0, 0, 0, self.horizon_y)
        sky_grad.setColorAt(0, QColor(10, 0, 30))
        sky_grad.setColorAt(1, QColor(100, 0, 150))
        p.fillRect(0, 0, w, int(self.horizon_y), sky_grad)
        
        # Sun
        sun_radius = min(w, h) * 0.15
        sun_center = QPointF(w / 2, self.horizon_y - sun_radius * 0.5)
        
        sun_grad = QLinearGradient(0, sun_center.y() - sun_radius, 0, sun_center.y() + sun_radius)
        sun_grad.setColorAt(0, QColor(255, 200, 0))
        sun_grad.setColorAt(0.5, QColor(255, 0, 100))
        sun_grad.setColorAt(1, QColor(100, 0, 150))
        
        p.setBrush(sun_grad)
        p.setPen(Qt.NoPen)
        p.drawEllipse(sun_center, sun_radius, sun_radius)
        
        # 2. Ground (Grid)
        p.fillRect(0, int(self.horizon_y), w, h - int(self.horizon_y), QColor(20, 5, 30))
        
        # Perspective Grid
        # Z-movement
        self.offset_z = (phase * 1000) % self.grid_spacing
        
        p.setPen(QPen(QColor(0, 255, 255, 150), 2))
        
        cx = w / 2
        fov = 300
        camera_height = 150
        
        # Horizontal lines (moving forward)
        # z goes from near to far
        for z_idx in range(40):
            z = z_idx * self.grid_spacing - self.offset_z + 10 # +10 to avoid div by zero
            
            # Avoid Z <= 0 or very small Z causing overflow
            if z < 1.0: continue
            
            # Perspective project
            scale = fov / z
            screen_y = self.horizon_y + camera_height * scale
            
            # Check for Overflow or Out of Bounds
            if screen_y > h or screen_y < -h: 
                continue
            
            p.drawLine(0, int(screen_y), w, int(screen_y))

        # Vertical lines (converging to horizon)
        for x_idx in range(-20, 21):
            world_x = x_idx * self.grid_spacing * 2
            
            # Project two points: near and far
            z_near = 10
            z_far = 2000
            
            scale_near = fov / z_near
            x_near = cx + world_x * scale_near
            y_near = self.horizon_y + camera_height * scale_near
            
            scale_far = fov / z_far
            x_far = cx + world_x * scale_far
            y_far = self.horizon_y + camera_height * scale_far
            
            # Clip to screen bottom
            if y_near > h: 
                # Intersect with bottom edge y=h
                # simple approximation: just draw to near point (it's off screen usually)
                pass
                
            p.drawLine(QPointF(x_far, y_far), QPointF(x_near, y_near))
