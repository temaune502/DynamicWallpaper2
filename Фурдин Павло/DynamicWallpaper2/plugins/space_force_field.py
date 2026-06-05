import random
import math
from PySide6.QtGui import QColor, QRadialGradient, QBrush, QLinearGradient, QPen, QPainterPath, QPolygonF
from PySide6.QtCore import Qt, QPointF
from effects import BaseEffect

class SpaceForceFieldEffect(BaseEffect):
    EFFECT_NAME = "space_force_field"
    
    def __init__(self):
        super().__init__()
        self.stars = None
        self.nebulas = None
        self.ships = []
        self.asteroids = []
        self.field_impacts = [] # Points where the field is "hit"
        self.hex_grid = None

    def _init_assets(self, w, h):
        base_radius = min(w, h) * 0.35
        # 1. Stars
        self.stars = []
        for _ in range(200):
            self.stars.append({
                'x': random.uniform(0, w),
                'y': random.uniform(0, h),
                'size': random.uniform(0.5, 2.5),
                'speed': random.uniform(0.1, 0.4),
                'brightness': random.randint(100, 255)
            })
            
        # 2. Nebulas (Background Gradients)
        self.nebulas = []
        colors = [
            QColor(40, 0, 80, 40),   # Purple
            QColor(0, 40, 80, 40),   # Blue
            QColor(80, 0, 40, 30),   # Magenta
            QColor(0, 20, 40, 50)    # Dark Teal
        ]
        for _ in range(4):
            self.nebulas.append({
                'x': random.uniform(0, w),
                'y': random.uniform(0, h),
                'r': random.uniform(w/3, w/1.5),
                'color': random.choice(colors),
                'phase_offset': random.uniform(0, math.pi * 2)
            })

        # 3. Ships (Increased spawn rate by 30%: 3 -> 4)
        for _ in range(4):
            self.ships.append(self._create_ship(w, h))

        # 4. Asteroids (Spawn outside shield, increased spawn rate by 30%: 8 -> 10)
        for _ in range(10):
            self.asteroids.append(self._create_asteroid(w, h, base_radius))

    def _create_ship(self, w, h):
        side = random.randint(0, 3)
        if side == 0: x, y = random.uniform(0, w), -50
        elif side == 1: x, y = random.uniform(0, w), h + 50
        elif side == 2: x, y = -50, random.uniform(0, h)
        else: x, y = w + 50, random.uniform(0, h)
        
        # Target a point near center
        tx, ty = w/2 + random.uniform(-100, 100), h/2 + random.uniform(-100, 100)
        angle = math.atan2(ty - y, tx - x)
        speed = random.uniform(1.5, 3.0) * 1.4 # Increased speed by 40%
        
        return {
            'x': x, 'y': y,
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
            'size': random.uniform(15, 25),
            'color': QColor(random.randint(150, 220), random.randint(150, 220), 255),
            'angle': angle * 180 / math.pi,
            'state': 'approaching'
        }

    def _create_asteroid(self, w, h, shield_radius=0):
        # Ensure spawning outside shield
        cx, cy = w/2, h/2
        while True:
            ax, ay = random.uniform(0, w), random.uniform(0, h)
            dist = math.sqrt((ax - cx)**2 + (ay - cy)**2)
            if dist > shield_radius + 60: # Added a bit more margin
                break
        
        points = []
        num_pts = random.randint(6, 10)
        radius = random.uniform(8, 30) # More size variety
        for i in range(num_pts):
            angle = (i / num_pts) * math.pi * 2
            r = radius * random.uniform(0.7, 1.3)
            points.append(QPointF(math.cos(angle) * r, math.sin(angle) * r))
        
        # Random speed based on size (smaller = faster)
        speed_factor = (30 / radius) * 0.5 * 1.4 # Increased speed by 40%
        
        return {
            'x': ax, 'y': ay,
            'vx': random.uniform(-1.0, 1.0) * speed_factor,
            'vy': random.uniform(-1.0, 1.0) * speed_factor,
            'rot': random.uniform(0, 360),
            'vrot': random.uniform(-2, 2) * 1.4, # Rotation speed also increased
            'points': QPolygonF(points),
            'color': QColor(random.randint(70, 100), 75, 70),
            'radius': radius
        }

    def draw(self, p, w, h, phase):
        if self.stars is None:
            self._init_assets(w, h)

        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(5, 5, 15))

        cx, cy = w / 2, h / 2
        base_radius = min(w, h) * 0.35

        # 1. Background Nebulas
        p.setPen(Qt.NoPen)
        for neb in self.nebulas:
            nx = neb['x'] + math.sin(phase * 0.2 + neb['phase_offset']) * 50
            ny = neb['y'] + math.cos(phase * 0.2 + neb['phase_offset']) * 50
            grad = QRadialGradient(nx, ny, neb['r'])
            grad.setColorAt(0, neb['color'])
            grad.setColorAt(1, Qt.transparent)
            p.setBrush(grad)
            p.drawRect(0, 0, w, h)

        # 2. Stars
        for s in self.stars:
            s['x'] = (s['x'] - s['speed']) % w
            twinkle = math.sin(phase * 3 + s['x'] * 0.05) * 50
            alpha = max(0, min(255, s['brightness'] + int(twinkle)))
            p.setPen(QColor(255, 255, 255, alpha))
            p.drawEllipse(QPointF(s['x'], s['y']), s['size']/2, s['size']/2)

        # 3. Space Station (Inside Field)
        self._draw_station(p, cx, cy, phase)

        # 4. Force Field
        self._draw_force_field(p, w, h, phase)

        # 5. Asteroids & Repulsion Logic
        for a in self.asteroids:
            a['x'] = (a['x'] + a['vx']) % w
            a['y'] = (a['y'] + a['vy']) % h
            a['rot'] += a['vrot']
            
            dx, dy = a['x'] - cx, a['y'] - cy
            dist = math.sqrt(dx**2 + dy**2)
            
            # Repulsion from shield boundary
            repulsion_dist = base_radius + 30
            if dist < repulsion_dist:
                nx, ny = dx / dist, dy / dist
                dot = a['vx'] * nx + a['vy'] * ny
                if dot < 0: # Moving towards center
                    # Bounce effect
                    a['vx'] -= 2.2 * dot * nx # Slight boost for repulsion
                    a['vy'] -= 2.2 * dot * ny
                    a['vx'] += random.uniform(-0.3, 0.3)
                    a['vy'] += random.uniform(-0.3, 0.3)
                    
                    impact_color = QColor(255, 255, 200)
                    if a['radius'] > 20: impact_color = QColor(255, 150, 100)
                    self.field_impacts.append({'x': a['x'], 'y': a['y'], 'life': 1.0, 'color': impact_color})
                
                # Hard limit to keep outside
                if dist < base_radius + 10:
                    a['x'] = cx + nx * (base_radius + 15)
                    a['y'] = cy + ny * (base_radius + 15)

            p.save()
            p.translate(a['x'], a['y'])
            p.rotate(a['rot'])
            p.setBrush(a['color'])
            p.setPen(QPen(a['color'].darker(150), 1))
            p.drawPolygon(a['points'])
            p.restore()

        # 6. Ships & Logic
        for s in self.ships:
            s['x'] += s['vx']
            s['y'] += s['vy']
            dist = math.sqrt((s['x'] - cx)**2 + (s['y'] - cy)**2)
            
            if s['state'] == 'approaching' and dist < base_radius + 10:
                s['state'] = 'turning'
                angle = math.atan2(s['y'] - cy, s['x'] - cx) + random.uniform(-0.5, 0.5)
                speed = math.sqrt(s['vx']**2 + s['vy']**2)
                s['vx'] = math.cos(angle) * speed
                s['vy'] = math.sin(angle) * speed
                self.field_impacts.append({'x': s['x'], 'y': s['y'], 'life': 1.0, 'color': QColor(100, 200, 255)})

            if s['x'] < -200 or s['x'] > w + 200 or s['y'] < -200 or s['y'] > h + 200:
                s.update(self._create_ship(w, h))
            
            s['angle'] = math.atan2(s['vy'], s['vx']) * 180 / math.pi
            p.save()
            p.translate(s['x'], s['y'])
            p.rotate(s['angle'])
            engine_grad = QLinearGradient(-s['size'], 0, 0, 0)
            engine_grad.setColorAt(0, Qt.transparent)
            engine_grad.setColorAt(1, QColor(100, 200, 255, 200))
            p.setBrush(engine_grad)
            p.drawRect(int(-s['size']*1.2), -2, int(s['size']), 4)
            p.setBrush(s['color'])
            p.setPen(QPen(Qt.white, 1))
            ship_poly = QPolygonF([QPointF(s['size'], 0), QPointF(-s['size']/2, -s['size']/3), QPointF(-s['size']/2, s['size']/3)])
            p.drawPolygon(ship_poly)
            p.restore()

        # 7. Update impacts
        self.field_impacts = [imp for imp in self.field_impacts if imp['life'] > 0]
        for imp in self.field_impacts:
            imp['life'] -= 0.02

    def _draw_station(self, p, cx, cy, phase):
        p.save()
        p.translate(cx, cy)
        
        # 1. Solar Panels (Rotating slowly)
        p.save()
        p.rotate(phase * 5)
        for i in range(2):
            p.save()
            p.rotate(i * 180)
            # Arm
            p.setPen(QPen(QColor(100, 100, 120), 3))
            p.drawLine(0, 0, 80, 0)
            # Panels
            p.setPen(QPen(QColor(40, 60, 120), 1))
            p.setBrush(QColor(30, 50, 100, 200))
            for j in range(3):
                p.drawRect(30 + j * 15, -15, 10, 30)
                # Detail on panel
                p.setPen(QPen(QColor(100, 150, 255, 100), 1))
                p.drawLine(30 + j * 15, -15, 40 + j * 15, 15)
            p.restore()
        p.restore()

        # 2. Main Body
        p.rotate(phase * 15) # Faster rotation for the body
        
        # Outer Ring
        p.setPen(QPen(QColor(180, 190, 200), 2))
        p.setBrush(QColor(60, 65, 80))
        p.drawEllipse(QPointF(0, 0), 35, 35)
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(0, 0), 30, 30)
        
        # Spokes
        for i in range(4):
            p.rotate(90)
            p.drawLine(15, 0, 30, 0)
            
        # Central Hub
        hub_grad = QRadialGradient(0, 0, 20)
        hub_grad.setColorAt(0, QColor(80, 85, 100))
        hub_grad.setColorAt(1, QColor(40, 45, 60))
        p.setBrush(hub_grad)
        p.drawEllipse(QPointF(0, 0), 20, 20)
        
        # Windows/Lights
        for i in range(8):
            p.rotate(45)
            if (int(phase * 2) + i) % 3 == 0:
                p.setBrush(QColor(255, 255, 150))
                p.drawRect(12, -2, 4, 2)
        
        # 3. Reactor Core (Glow)
        pulse = math.sin(phase * 4) * 0.5 + 0.5
        core_grad = QRadialGradient(0, 0, 12)
        core_grad.setColorAt(0, QColor(0, 255, 255, int(180 + pulse * 75)))
        core_grad.setColorAt(0.5, QColor(0, 150, 255, 100))
        core_grad.setColorAt(1, Qt.transparent)
        p.setBrush(core_grad)
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(0, 0), 15, 15)
        
        # Center core detail
        p.setBrush(QColor(255, 255, 255, 200))
        p.drawEllipse(QPointF(0, 0), 3, 3)
        
        p.restore()

    def _draw_force_field(self, p, w, h, phase):
        cx, cy = w / 2, h / 2
        base_radius = min(w, h) * 0.35
        
        shield_grad = QRadialGradient(cx, cy, base_radius * 1.2)
        pulse = math.sin(phase * 2) * 0.03
        shield_grad.setColorAt(0, Qt.transparent)
        shield_grad.setColorAt(0.8 + pulse, QColor(0, 100, 255, 15))
        shield_grad.setColorAt(0.95 + pulse, QColor(100, 220, 255, 80))
        shield_grad.setColorAt(1.0, Qt.transparent)
        
        p.setBrush(shield_grad)
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, cy), base_radius * 1.2, base_radius * 1.2)

        if self.hex_grid is None:
            self.hex_grid = self._generate_hex_grid(base_radius * 1.1)

        p.save()
        p.translate(cx, cy)
        for hex_poly, center_dist in self.hex_grid:
            ripple = math.sin(center_dist * 0.05 - phase * 4) * 0.5 + 0.5
            alpha = int(15 + ripple * 45)
            
            impact_bonus = 0
            for imp in self.field_impacts:
                dist_to_imp = math.sqrt((hex_poly.boundingRect().center().x() + cx - imp['x'])**2 + 
                                      (hex_poly.boundingRect().center().y() + cy - imp['y'])**2)
                if dist_to_imp < 60:
                    impact_bonus = max(impact_bonus, (1.0 - dist_to_imp/60) * imp['life'] * 150)
            
            final_alpha = min(255, alpha + int(impact_bonus))
            color = QColor(100, 200, 255, final_alpha)
            if impact_bonus > 50:
                color = QColor(200, 230, 255, final_alpha)
                
            p.setPen(QPen(color, 1))
            p.drawPolygon(hex_poly)
        p.restore()

        for imp in self.field_impacts:
            # 1. Glow flash
            flash_grad = QRadialGradient(imp['x'], imp['y'], 50 * imp['life'])
            c = imp['color']
            flash_grad.setColorAt(0, QColor(c.red(), c.green(), c.blue(), int(200 * imp['life'])))
            flash_grad.setColorAt(1, Qt.transparent)
            p.setBrush(flash_grad)
            p.drawEllipse(QPointF(imp['x'], imp['y']), 50 * imp['life'], 50 * imp['life'])
            
            # 2. Expanding Ring
            ring_radius = (1.0 - imp['life']) * 80
            alpha = int(imp['life'] * 255)
            p.setPen(QPen(QColor(c.red(), c.green(), c.blue(), alpha), 2))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPointF(imp['x'], imp['y']), ring_radius, ring_radius)

    def _generate_hex_grid(self, radius):
        hex_size = 25
        grid = []
        for q in range(-15, 16):
            for r in range(-15, 16):
                x = hex_size * (3/2 * q)
                y = hex_size * (math.sqrt(3)/2 * q + math.sqrt(3) * r)
                dist = math.sqrt(x*x + y*y)
                if dist < radius:
                    points = []
                    for i in range(6):
                        angle_rad = math.pi / 180 * (60 * i)
                        points.append(QPointF(x + hex_size * 0.9 * math.cos(angle_rad), 
                                            y + hex_size * 0.9 * math.sin(angle_rad)))
                    grid.append((QPolygonF(points), dist))
        return grid
