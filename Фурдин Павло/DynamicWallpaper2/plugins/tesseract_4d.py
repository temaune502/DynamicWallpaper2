import math
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QPen

from effects import BaseEffect

class Tesseract4DEffect(BaseEffect):
    EFFECT_NAME = "tesseract_4d"

    def __init__(self):
        super().__init__()
        self.speed = 1.0
        self.color_nodes = (255, 255, 255)
        self.color_edges = (0, 255, 255)
        self.edge_alpha = 150
        
        self._init_tesseract()

    def _init_tesseract(self):
        # 4D Hypercube Vertices (+-1, +-1, +-1, +-1)
        self.vertices = []
        for x in [-1, 1]:
            for y in [-1, 1]:
                for z in [-1, 1]:
                    for w in [-1, 1]:
                        self.vertices.append([x, y, z, w])

        # Edges (connect vertices that differ by 1 coord)
        self.edges = []
        for i in range(len(self.vertices)):
            for j in range(i + 1, len(self.vertices)):
                v1 = self.vertices[i]
                v2 = self.vertices[j]
                diff = 0
                for k in range(4):
                    if v1[k] != v2[k]: diff += 1
                if diff == 1:
                    self.edges.append((i, j))
        
        self.nodes = []

    @classmethod
    def get_schema(cls):
        return {
            "speed": {
                "type": "float",
                "min": 0.0,
                "max": 5.0,
                "default": 1.0,
                "label": "Rotation Speed"
            },
            "color_nodes": {
                "type": "color",
                "default": (0, 255, 255),
                "label": "Node Color"
            },
            "color_edges": {
                "type": "color",
                "default": (255, 255, 255),
                "label": "Edge Color"
            },
            "edge_alpha": {
                "type": "int",
                "min": 0,
                "max": 255,
                "default": 150,
                "label": "Edge Alpha"
            }
        }

    def configure(self, config: dict):
        if 'speed' in config: self.speed = float(config['speed'])
        if 'color_nodes' in config: self.color_nodes = tuple(config['color_nodes'])
        if 'color_edges' in config: self.color_edges = tuple(config['color_edges'])
        if 'edge_alpha' in config: self.edge_alpha = int(config['edge_alpha'])

    def _rotate_xw(self, point, theta):
        x, y, z, w = point
        nx = x * math.cos(theta) - w * math.sin(theta)
        nw = x * math.sin(theta) + w * math.cos(theta)
        return [nx, y, z, nw]

    def _rotate_yw(self, point, theta):
        x, y, z, w = point
        ny = y * math.cos(theta) - w * math.sin(theta)
        nw = y * math.sin(theta) + w * math.cos(theta)
        return [x, ny, z, nw]
        
    def _rotate_zw(self, point, theta):
        x, y, z, w = point
        nz = z * math.cos(theta) - w * math.sin(theta)
        nw = z * math.sin(theta) + w * math.cos(theta)
        return [x, y, nz, nw]

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(10, 10, 15))
        
        cx, cy = w / 2, h / 2
        scale = 150
        
        # Rotations
        angle = phase * 2 * self.speed
        
        projected_points_2d = []
        
        for v in self.vertices:
            # Copy vertex
            pt = list(v)
            
            # Rotate in 4D
            pt = self._rotate_xw(pt, angle)
            pt = self._rotate_yw(pt, angle * 0.5)
            # pt = self._rotate_zw(pt, angle * 0.2)
            
            # Project 4D to 3D
            # p_3d = p_4d / (w + distance)
            w_factor = 2 - pt[3] # Camera distance
            x_3d = pt[0] / w_factor
            y_3d = pt[1] / w_factor
            z_3d = pt[2] / w_factor
            
            # Rotate in 3D (Standard)
            # ... can add 3D rotation here if needed
            
            # Project 3D to 2D
            z_factor = 2 - z_3d
            x_2d = x_3d / z_factor * scale * 3 # Zoom
            y_2d = y_3d / z_factor * scale * 3
            
            projected_points_2d.append(QPointF(cx + x_2d, cy + y_2d))
            
            
        # Draw Edges
        edge_col = QColor(*self.color_edges)
        edge_col.setAlpha(self.edge_alpha)
        p.setPen(QPen(edge_col, 2))
        
        for i, j in self.edges:
            p1 = projected_points_2d[i]
            p2 = projected_points_2d[j]
            p.drawLine(p1, p2)
            
        # Draw Nodes
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(*self.color_nodes))
        for pt in projected_points_2d:
            p.drawEllipse(pt, 4, 4)
