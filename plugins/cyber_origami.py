import math
import random
from PySide6.QtGui import QColor, QBrush, QPen, QPolygonF, QLinearGradient, QPainter
from PySide6.QtCore import Qt, QPointF
from effects import BaseEffect

class CyberOrigamiEffect(BaseEffect):
    EFFECT_NAME = "cyber_origami"

    def __init__(self):
        super().__init__()
        self.shapes = None
        self.bg_particles = None

    def _init_assets(self, w, h):
        self.shapes = []
        # Create a set of interconnected triangular "folding" planes
        num_shapes = 12
        for i in range(num_shapes):
            self.shapes.append({
                'center_x': random.uniform(w*0.2, w*0.8),
                'center_y': random.uniform(h*0.2, h*0.8),
                'size': random.uniform(100, 250),
                'rotation_speed': random.uniform(0.2, 0.5),
                'fold_speed': random.uniform(0.5, 1.2),
                'phase_offset': random.uniform(0, math.pi * 2),
                'color': QColor(random.randint(10, 30), random.randint(150, 255), random.randint(200, 255), 40),
                'points_count': random.randint(3, 5)
            })
        
        # Background digital dust
        self.bg_particles = []
        for _ in range(100):
            self.bg_particles.append({
                'x': random.uniform(0, w),
                'y': random.uniform(0, h),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-0.5, 0.5),
                'size': random.uniform(1, 3)
            })

    def draw(self, p, w, h, phase):
        if self.shapes is None:
            self._init_assets(w, h)

        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(5, 8, 15))

        # 1. Background Particles
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(100, 200, 255, 30))
        for part in self.bg_particles:
            part['x'] = (part['x'] + part['vx']) % w
            part['y'] = (part['y'] + part['vy']) % h
            p.drawRect(int(part['x']), int(part['y']), int(part['size']), int(part['size']))

        # 2. Cyber Origami Shapes
        p.setRenderHint(QPainter.Antialiasing)
        
        for s in self.shapes:
            p.save()
            p.translate(s['center_x'], s['center_y'])
            
            # Complex transformation
            rot = phase * s['rotation_speed'] + s['phase_offset']
            fold = math.sin(phase * s['fold_speed'] + s['phase_offset'])
            
            p.rotate(math.degrees(rot))
            
            # Create a "3D-like" folding effect by calculating vertices
            pts = []
            for i in range(s['points_count']):
                angle = (i / s['points_count']) * math.pi * 2
                # Morph the radius based on folding phase
                r = s['size'] * (0.8 + 0.4 * math.cos(fold + i))
                px = math.cos(angle) * r
                py = math.sin(angle) * r * math.sin(fold) # Squashing for 3D look
                pts.append(QPointF(px, py))

            # Draw multiple layers for glass/crystal effect
            for layer in range(3):
                p.save()
                scale = 1.0 - (layer * 0.15)
                p.scale(scale, scale)
                p.rotate(layer * 10 * fold)
                
                # Gradient for each facet
                grad = QLinearGradient(pts[0], pts[1] if len(pts) > 1 else pts[0])
                c = s['color']
                alpha = 40 + layer * 30
                grad.setColorAt(0, QColor(c.red(), c.green(), c.blue(), alpha))
                grad.setColorAt(1, QColor(255, 255, 255, alpha // 2))
                
                p.setBrush(grad)
                p.setPen(QPen(QColor(c.red(), c.green(), c.blue(), 150), 1))
                p.drawPolygon(QPolygonF(pts))
                
                # Draw "wireframe" connections to center
                p.setPen(QPen(QColor(100, 255, 255, 40), 0.5))
                for pt in pts:
                    p.drawLine(QPointF(0, 0), pt)
                
                p.restore()

            # Central glow
            glow = QColor(s['color'].red(), s['color'].green(), s['color'].blue(), 20)
            p.setBrush(glow)
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(0, 0), s['size'] * 0.4, s['size'] * 0.4)
            
            p.restore()

        # 3. Connection lines between shapes (rarely)
        p.setPen(QPen(QColor(100, 200, 255, 20), 1))
        for i in range(len(self.shapes)):
            for j in range(i + 1, len(self.shapes)):
                s1, s2 = self.shapes[i], self.shapes[j]
                dist_sq = (s1['center_x'] - s2['center_x'])**2 + (s1['center_y'] - s2['center_y'])**2
                if dist_sq < (300**2):
                    p.drawLine(QPointF(s1['center_x'], s1['center_y']), 
                               QPointF(s2['center_x'], s2['center_y']))
