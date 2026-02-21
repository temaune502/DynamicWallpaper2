import random
import math
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QCursor, QLinearGradient, QPolygonF

from effects import BaseEffect

class SynthwaveDriveEffect(BaseEffect):
    EFFECT_NAME = "synthwave_drive"

    def __init__(self):
        super().__init__()
        self.sun_stripe_phase = 0
        self.grid_phase = 0
        self.mountain_offset = 0
        self.mountain_offset = 0
        
        self.speed = 2.0
        self.color_sky_top = (10, 0, 30)
        self.color_sky_bottom = (40, 0, 60)
        self.color_grid = (255, 0, 255)

        self._init_terrain()

    def _init_terrain(self):
        # Generate Mountains (Static y-values, we'll scroll x)
        self.mountains_far = self._generate_mountains(100, 50)
        self.mountains_mid = self._generate_mountains(80, 100)

    @classmethod
    def get_schema(cls):
        return {
            "speed": {
                "type": "float",
                "min": 1.0,
                "max": 50.0,
                "default": 10.0,
                "label": "Speed"
            },
            "color_grid": {
                "type": "color",
                "default": (255, 0, 255),
                "label": "Grid Color"
            },
            "color_sky_top": {
                "type": "color",
                "default": (10, 0, 30),
                "label": "Sky Top"
            },
            "color_sky_bottom": {
                "type": "color",
                "default": (60, 0, 60),
                "label": "Sky Bottom"
            }
        }

    def configure(self, config: dict):
        if 'speed' in config: self.speed = float(config['speed'])
        if 'color_grid' in config: self.color_grid = tuple(config['color_grid'])
        if 'color_sky_top' in config: self.color_sky_top = tuple(config['color_sky_top'])
        if 'color_sky_bottom' in config: self.color_sky_bottom = tuple(config['color_sky_bottom'])

    def _generate_mountains(self, spacing, variance):
        points = []
        y = 0
        # Generate enough to scroll indefinitely? No, just loop.
        # We assume screen width max 2000. 4000 pixels wide pattern to loop.
        current_x = 0
        while current_x < 4000:
            points.append(QPointF(current_x, y))
            current_x += spacing
            y = max(0, min(150, y + random.uniform(-variance, variance)))
            # Return to base roughly?
            if y > 100: y -= 20
        # Close shape
        points.append(QPointF(current_x, 200))
        points.append(QPointF(0, 200))
        return points

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        # 1. Sky Gradient
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor(*self.color_sky_top)) # Deep purple top
        grad.setColorAt(0.4, QColor(*self.color_sky_bottom))
        grad.setColorAt(0.5, QColor(180, 40, 80)) # Horizon Red
        grad.setColorAt(0.51, QColor(10, 0, 20)) # Grid background dark
        grad.setColorAt(1.0, QColor(30, 0, 60)) # Grid bottom
        p.fillRect(0, 0, w, h, QBrush(grad))
        
        horizon_y = h / 2
        cx = w / 2
        
        # Mouse Interaction (Parallax)
        mouse_pos = QCursor.pos()
        mx = mouse_pos.x()
        
        # Shift -1 to 1 based on mouse x relative to center
        parallax_shift = (mx - cx) / float(w) 
        
        # 2. Retro Sun
        sun_radius = 150
        sun_x = cx - parallax_shift * 20 # Moves very little
        sun_y = horizon_y - 50
        
        # Draw Sun
        p.setPen(Qt.NoPen)
        # Gradient sun
        sun_grad = QLinearGradient(0, sun_y - sun_radius, 0, sun_y + sun_radius)
        sun_grad.setColorAt(0, QColor(255, 255, 0))
        sun_grad.setColorAt(1, QColor(255, 0, 128))
        p.setBrush(QBrush(sun_grad))
        p.drawEllipse(QPointF(sun_x, sun_y), sun_radius, sun_radius)
        
        # Sun Stripes (Scanlines)
        p.setBrush(QColor(10, 0, 30)) # Sky color to mask
        stripe_height = 4
        total_h = sun_radius * 2
        
        self.sun_stripe_phase += 0.5
        if self.sun_stripe_phase >= 20: self.sun_stripe_phase = 0
        
        # Only draw stripes on bottom half of sun usually
        for i in range(10):
            y_off = sun_radius * 0.2 + i * 15 + (self.sun_stripe_phase % 15)
            if y_off < sun_radius:
                # Calc width at this y
                # x^2 + y^2 = r^2 -> x = sqrt(r^2 - y^2)
                # But we just draw rect across
                rect_y = sun_y + y_off
                p.drawRect(sun_x - sun_radius, rect_y, sun_radius * 2, stripe_height * (i/5.0 + 0.5))
        
        # 3. Mountains (Parallax)
        self.mountain_offset += self.speed
        
        # Far layer
        p.setBrush(QColor(60, 20, 80))
        p.save()
        # Scroll + Parallax
        scroll_x = (self.mountain_offset * 0.5) % 2000
        shift_x = -parallax_shift * 50
        p.translate(shift_x - scroll_x, horizon_y - 50)
        # Draw twice to loop
        self._draw_poly(p, self.mountains_far)
        p.translate(2000, 0) # Wrap
        self._draw_poly(p, self.mountains_far) # Wait this is buggy if we construct QPolygonF once.
        # Just drawing points manually?
        # Let's fix _draw_poly to take offset
        p.restore()
        
        # Mid layer
        p.setBrush(QColor(30, 0, 40))
        p.save()
        scroll_x = (self.mountain_offset * 1.0) % 2000
        shift_x = -parallax_shift * 150
        p.translate(shift_x - scroll_x, horizon_y)
        self._draw_poly(p, self.mountains_mid)
        p.translate(2000, 0)
        self._draw_poly(p, self.mountains_mid)
        p.restore()
        
        # 4. Perspective Grid
        p.setClipRect(0, int(horizon_y), w, h - int(horizon_y))
        
        grid_color = QColor(*self.color_grid) # Neon Pink
        grid_color.setAlpha(100)
        p.setPen(QPen(grid_color, 2))
        
        # Infinite Vertical Lines
        # Perspective: converge to (cx, horizon_y)
        # We need to scroll them laterally based on parallax to simulate turning?
        # Or just keep them static and move horizontal lines?
        # Let's shift vanish point X based on mouse
        vanish_x = cx - parallax_shift * 500
        
        spacing = 100
        num_lines = int(w / spacing) * 4 # Extra for wide fov
        start_x = -w
        
        for i in range(num_lines):
            base_x = start_x + i * spacing
            # Scroll base x slightly for turning effect?
            base_x = (base_x + parallax_shift * 500) % (w * 2) - w/2
            
            p.drawLine(QPointF(vanish_x, horizon_y), QPointF(base_x, h))

        # Horizontal Lines (Moving forward)
        self.grid_phase += self.speed
        if self.grid_phase > 100: self.grid_phase = 0
        
        # Logarithmic or 1/z spacing for perspective depth
        # z goes from 1 to 1000
        # y = horizon + h / z
        
        for i in range(20):
             z = 20 - i + (self.grid_phase / 100.0)
             if z < 1: continue
             
             # Project z to y
             # y = horizon + (h/2) * (1/z)
             perspective_y = horizon_y + (h) / z * 1.5
             
             if perspective_y > h: continue
             
             # Alpha fade near horizon
             alpha = int(255 * (1 - (20-z)/20.0))
             # Actually fade near horizon (high z)
             alpha = 255 if z < 10 else int(255 * (20-z)/10.0)
             
             col = QColor(grid_color)
             col.setAlpha(max(0, min(255, alpha)))
             p.setPen(QPen(col, 2))
             
             p.drawLine(0, perspective_y, w, perspective_y)
             
        p.setClipping(False)

    def _draw_poly(self, p, points):
        # Scale polygon to be larger?
        poly = QPolygonF(points)
        p.drawPolygon(poly)
