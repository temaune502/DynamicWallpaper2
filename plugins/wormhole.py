import math
import random
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QCursor, QPolygonF

from effects import BaseEffect

class WormholeEffect(BaseEffect):
    EFFECT_NAME = "wormhole"

    def __init__(self):
        super().__init__()
        self.rings = []
        self.num_rings = 30
        self.ring_segments = 12
        self.tunnel_radius = 400
        self.camera_x = 0
        self.camera_y = 0
        self.speed = 20.0
        self.color_hue_min = 0.5
        self.color_hue_max = 0.9
        
        # Initialize Rings
        self._init_rings()

    def _init_rings(self):
        self.rings = []
        for i in range(self.num_rings):
            self.rings.append(self._create_ring(i * 100))

    @classmethod
    def get_schema(cls):
        return {
            "speed": {
                "type": "float", 
                "min": 0.0, 
                "max": 200.0, 
                "default": 40.0, 
                "label": "Tunnel Speed"
            },
            "tunnel_radius": {
                "type": "int",
                "min": 50,
                "max": 500,
                "default": 100,
                "label": "Tunnel Radius"
            },
            "hue_min": {
                "type": "float",
                "min": 0.0,
                "max": 1.0,
                "default": 0.0,
                "label": "Hue Min (0-1)"
            },
            "hue_max": {
                "type": "float",
                "min": 0.0,
                "max": 1.0,
                "default": 0.2,
                "label": "Hue Max (0-1)"
            }
        }

    def configure(self, config: dict):
        if 'speed' in config: self.speed = float(config['speed'])
        if 'tunnel_radius' in config: self.tunnel_radius = int(config['tunnel_radius'])
        if 'hue_min' in config: self.color_hue_min = float(config['hue_min'])
        if 'hue_max' in config: self.color_hue_max = float(config['hue_max'])
        
        # Re-color rings if needed or let them cycle naturally? 
        # Better to update existing rings or they won't match until recycled
        for r in self.rings:
            if 'hue_min' in config or 'hue_max' in config:
                r['color_hue'] = random.uniform(self.color_hue_min, self.color_hue_max)

    def _create_ring(self, z):
        return {
            'z': z,
            'x': random.uniform(-200, 200), # Curvature offset
            'y': random.uniform(-200, 200),
            'rotation': 0,
            'color_hue': random.uniform(self.color_hue_min, self.color_hue_max) # Blue/Purple/Pink
        }

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(0, 0, 10)) # Deep space
        
        cx, cy = w / 2, h / 2
        
        # Mouse Interaction (Camera Steering)
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        
        # Target camera position based on mouse relative to center
        target_cam_x = (mx - cx) * 2.0
        target_cam_y = (my - cy) * 2.0
        
        # Smooth camera movement
        self.camera_x += (target_cam_x - self.camera_x) * 0.1
        self.camera_y += (target_cam_y - self.camera_y) * 0.1
        
        # Dynamic Speed based on how far mouse is from center (warping!)
        dist_from_center = math.sqrt((mx-cx)**2 + (my-cy)**2)
        target_speed = 20.0 + (dist_from_center / 500.0) * 80.0
        self.speed += (target_speed - self.speed) * 0.1
        
        # Update Rings
        for i, r in enumerate(self.rings):
            r['z'] -= self.speed
            r['rotation'] += 0.02 # Twist
            
            # recycle
            if r['z'] < 10:
                # Find the furthest ring to attach to
                max_z = max(r['z'] for r in self.rings)
                r['z'] = max_z + 100
                # Generate new curve continuing from last? Random for now
                r['x'] = random.uniform(-300, 300)
                r['y'] = random.uniform(-300, 300)
        
        # Sort rings back-to-front for correct drawing (Painter's Algorithm)
        self.rings.sort(key=lambda r: r['z'], reverse=True)
        
        # Draw Tunnel
        # We need projected points for current ring and next ring to fill quads
        
        points_cache = [] # Cache projected points for each ring
        
        for r in self.rings:
            ring_points = []
            scale = 400.0 / max(1.0, r['z'])
            
            # Camera offset affects position relative to center
            # Parallax: Closer rings move more? No, camera moves standard
            # World pos = Ring pos
            # View pos = World pos - Camera pos
            
            rx = r['x'] - self.camera_x
            ry = r['y'] - self.camera_y
            
            brightness = min(255, max(0, int(255 * (1 - r['z'] / 3000.0))))
            color = QColor.fromHsvF(r['color_hue'], 0.8, 1.0)
            color.setAlpha(brightness)
            
            for j in range(self.ring_segments):
                angle = (j / self.ring_segments) * math.pi * 2 + r['rotation']
                x = rx + math.cos(angle) * self.tunnel_radius
                y = ry + math.sin(angle) * self.tunnel_radius
                
                # Project
                px = cx + x * scale
                py = cy + y * scale
                ring_points.append(QPointF(px, py))
            
            points_cache.append({'points': ring_points, 'color': color, 'z': r['z']})
            
        # Draw Quads connecting rings
        p.setPen(Qt.NoPen)
        
        for i in range(len(points_cache) - 1):
            r1 = points_cache[i]
            r2 = points_cache[i+1] # This is the ring closer to camera (sorted z desc)
            
            # wait, if sorted reverse=True, i=0 is FURTHEST. i+1 is CLOSER.
            # We want to draw from back to front. So this interaction is correct.
            
            pts1 = r1['points']
            pts2 = r2['points']
            col = r1['color']
            
            # Interpolate color towards r2?
            
            for j in range(self.ring_segments):
                next_j = (j + 1) % self.ring_segments
                
                # Quad vertices
                # r1 (far) -> r2 (near)
                p1 = pts1[j]      # Far Left
                p2 = pts1[next_j] # Far Right
                p3 = pts2[next_j] # Near Right
                p4 = pts2[j]      # Near Left
                
                # Culling: Only draw if z is sufficient?
                # or opacity handles it.
                
                # Wireframe or Fill?
                # Fill looks better for "solid" tunnel
                # Use semi-transparent fill
                
                fill_col = QColor(col)
                fill_col.setAlpha(min(50, fill_col.alpha()))
                
                p.setBrush(fill_col)
                p.setPen(QPen(col, 2))
                
                poly = QPolygonF([p1, p2, p3, p4])
                p.drawPolygon(poly)

        # Draw "Speed Lines" / Particles passing by
        # ... (Optional, let's keep it clean for now)
