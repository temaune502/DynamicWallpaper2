import math
import random
from PySide6.QtGui import QColor, QPen, QBrush, QPolygonF, QRadialGradient
from PySide6.QtCore import Qt, QPointF
from effects import BaseEffect

class MinecraftTorchEffect(BaseEffect):
    EFFECT_NAME = "mc_torch"
    
    def __init__(self):
        super().__init__()
        self.particles = []
        self.last_spark = 0
        self.noise_map = [[random.random() for _ in range(8)] for _ in range(16)] # Для текстури

        self.wall_blocks = None

    def _draw_cube(self, p, cx, cy, cz, w_b, h_b, d_b, rot_y, color, phase, is_textured=False, is_ember=False):
        scale = 18.0
        nodes = []
        for x in [-w_b/2, w_b/2]:
            for y in [0, -h_b]:
                for z in [-d_b/2, d_b/2]:
                    nx = x * math.cos(rot_y) - z * math.sin(rot_y)
                    nz = x * math.sin(rot_y) + z * math.cos(rot_y)
                    proj = 300 / (300 + nz * scale)
                    nodes.append(QPointF(cx + nx * scale * proj, cy + y * scale * proj))

        faces = [
            (0, 4, 6, 2, color.darker(150), "side"),  # Front
            (1, 5, 7, 3, color.darker(110), "side"),  # Back
            (0, 1, 5, 4, color.darker(130), "top"),   # Bottom
            (2, 3, 7, 6, color, "top"),               # Top
            (0, 1, 3, 2, color.darker(140), "side"),  # Left
            (4, 5, 7, 6, color.darker(120), "side")   # Right
        ]

        # Painter's algorithm
        face_depths = []
        for f in faces:
            avg_z = sum([( (0 if i<4 else 1) * math.sin(rot_y) + (0 if i%2==0 else 1) * math.cos(rot_y) ) for i in f[:4]]) / 4
            face_depths.append((avg_z, f))
        face_depths.sort(key=lambda x: x[0], reverse=True)

        for _, f in face_depths:
            poly = QPolygonF([nodes[i] for i in f[:4]])
            current_color = f[4]
            if is_ember:
                pulse = math.sin(phase * 10) * 40
                current_color = QColor(min(255, current_color.red() + 120 + int(pulse)), 
                                      min(255, current_color.green() + 50), 
                                      current_color.blue())

            p.setBrush(current_color)
            p.setPen(Qt.NoPen)
            p.drawPolygon(poly)
            
            if is_textured:
                self._draw_pixel_texture(p, nodes, f, is_ember)

    def _draw_pixel_texture(self, p, nodes, face, is_ember):
        indices = face[:4]
        p1, p2, p3, p4 = nodes[indices[0]], nodes[indices[1]], nodes[indices[2]], nodes[indices[3]]
        steps_u, steps_v = 4, (8 if face[5] == "side" else 4)
        for u in range(steps_u):
            for v in range(steps_v):
                fu1, fv1 = u / steps_u, v / steps_v
                fu2, fv2 = (u + 1) / steps_u, (v + 1) / steps_v
                def get_pt(fu, fv):
                    top = p1 + (p2 - p1) * fu
                    bottom = p4 + (p3 - p4) * fu
                    return top + (bottom - top) * fv
                pixel_poly = QPolygonF([get_pt(fu1, fv1), get_pt(fu2, fv1), get_pt(fu2, fv2), get_pt(fu1, fv2)])
                noise = self.noise_map[(u * 3) % 16][(v * 2) % 8]
                if is_ember:
                    t_color = QColor(255, 180, 0, int(noise * 180)) if noise > 0.4 else QColor(80, 0, 0, 120)
                else:
                    t_color = QColor(0, 0, 0, int(noise * 70)) if noise > 0.5 else QColor(255, 255, 255, int(noise * 30))
                p.setBrush(t_color)
                p.drawPolygon(pixel_poly)

    def draw(self, p, w, h, phase):
        cx, cy = w // 2, h // 2 + 150
        flicker = math.sin(phase * 15) * 5 + random.uniform(-3, 3)
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(10, 8, 8))
            if self.wall_blocks is None:
                self.wall_blocks = []
                for x in range(0, w, 50):
                    for y in range(0, h, 50):
                        if random.random() > 0.7:
                            self.wall_blocks.append((x, y, random.uniform(0.4, 0.8)))
            for bx, by, intensity in self.wall_blocks:
                dist = math.sqrt((bx - cx)**2 + (by - (cy - 150))**2)
                light = max(0, min(1, (500 - dist + flicker * 10) / 500)) * intensity
                if light > 0.05:
                    p.setBrush(QColor(50, 45, 40, int(light * 180)))
                    p.drawRect(bx, by, 48, 48)

        light_grad = QRadialGradient(cx, cy - 180, 500 + flicker * 5)
        light_grad.setColorAt(0, QColor(255, 120, 20, 100))
        light_grad.setColorAt(0.4, QColor(200, 60, 0, 40))
        light_grad.setColorAt(1, Qt.transparent)
        p.setBrush(QBrush(light_grad))
        p.setPen(Qt.NoPen)
        p.drawEllipse(cx - 500, cy - 680, 1000, 1000)

        rot_y = phase * 1.5
        self._draw_cube(p, cx, cy, 0, 2, 10, 2, rot_y, QColor(110, 80, 50), phase, is_textured=True)
        head_h = 2.5
        head_cy = cy - (10 * 18.0)
        self._draw_cube(p, cx, head_cy, 0, 2.4, head_h, 2.4, rot_y, QColor(60, 20, 10), phase, is_textured=True, is_ember=True)
        
        fire_layers = [(QColor(255, 255, 180, 240), 10, 0), (QColor(255, 180, 0, 180), 16, 1), (QColor(255, 50, 0, 120), 22, 2)]
        fire_y = head_cy - (head_h * 18.0)
        for color, size, offset in fire_layers:
            for i in range(3):
                t = phase * 15 + i * 2 + offset
                fx = cx + math.sin(t * 0.7) * 10
                fy = fire_y - 10 - i * 15 - math.cos(t) * 8
                p.setBrush(color)
                p.drawRect(int(fx - size/2), int(fy - size/2), size, size)

        if random.random() < 0.3:
            self.particles.append({'x': cx + random.uniform(-10, 10), 'y': fire_y, 'vx': random.uniform(-1.2, 1.2), 'vy': random.uniform(-3.0, -1.5), 'life': 1.0, 'type': 'smoke' if random.random() > 0.4 else 'spark', 'size': random.uniform(6, 12)})
        active_particles = []
        for pt in self.particles:
            pt['x'] += pt['vx']
            pt['y'] += pt['vy']
            if pt['type'] == 'spark': pt['vy'] += 0.08
            pt['life'] -= 0.015
            if pt['life'] > 0:
                alpha = int(255 * pt['life'])
                p.setBrush(QColor(255, 200, 50, alpha) if pt['type'] == 'spark' else QColor(50, 50, 50, int(alpha * 0.7)))
                s = pt['size'] * (0.4 + pt['life'] * 0.6)
                p.drawRect(int(pt['x'] - s/2), int(pt['y'] - s/2), int(s), int(s))
                active_particles.append(pt)
        self.particles = active_particles
