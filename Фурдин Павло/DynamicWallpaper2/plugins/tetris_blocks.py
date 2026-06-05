import random
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QBrush, QPen

from effects import BaseEffect

class TetrisBlocksEffect(BaseEffect):
    EFFECT_NAME = "tetris_blocks"

    SHAPES = [
        [[1, 1, 1, 1]], # I
        [[1, 1], [1, 1]], # O
        [[0, 1, 0], [1, 1, 1]], # T
        [[1, 0, 0], [1, 1, 1]], # L
        [[0, 0, 1], [1, 1, 1]], # J
        [[0, 1, 1], [1, 1, 0]], # S
        [[1, 1, 0], [0, 1, 1]]  # Z
    ]
    
    COLORS = [
        QColor(0, 255, 255), # Cyan (I)
        QColor(255, 255, 0), # Yellow (O)
        QColor(128, 0, 128), # Purple (T)
        QColor(255, 165, 0), # Orange (L)
        QColor(0, 0, 255),   # Blue (J)
        QColor(0, 255, 0),   # Green (S)
        QColor(255, 0, 0)    # Red (Z)
    ]

    def __init__(self):
        super().__init__()
        self.block_size = 30
        self.spawn_rate = 20
        self.blocks = []
        # Columns
        self.cols = 0 
        self.timer = 0
        
    @classmethod
    def get_schema(cls):
        return {
            "block_size": {
                "type": "int",
                "min": 10,
                "max": 100,
                "default": 30,
                "label": "Block Size"
            },
            "spawn_rate": {
                "type": "int",
                "min": 1,
                "max": 60,
                "default": 20,
                "label": "Spawn Rate (Frames)"
            }
        }

    def configure(self, config: dict):
        if 'block_size' in config: self.block_size = int(config['block_size'])
        if 'spawn_rate' in config: self.spawn_rate = int(config['spawn_rate'])
        
    def _spawn_block(self, w):
        shape_idx = random.randint(0, len(self.SHAPES) - 1)
        shape = self.SHAPES[shape_idx]
        color = self.COLORS[shape_idx]
        
        # Random column
        col = random.randint(0, self.cols -  len(shape[0]))
        
        self.blocks.append({
            'shape': shape,
            'color': color,
            'x': col * self.block_size,
            'y': -100,
            'speed': random.uniform(2, 5)
        })

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        p.fillRect(0, 0, w, h, QColor(20, 20, 20))
        
        self.cols = w // self.block_size
        
        # Spawn
        self.timer += 1
        self.timer += 1
        if self.timer > self.spawn_rate: # Spawn rate
            self._spawn_block(w)
            self.timer = 0
            
        # Grid lines (faint)
        p.setPen(QPen(QColor(255, 255, 255, 20), 1))
        for c in range(self.cols + 1):
            p.drawLine(c * self.block_size, 0, c * self.block_size, h)
            
        p.setPen(Qt.NoPen)
        
        # Update and Draw
        for b in self.blocks[:]:
            b['y'] += b['speed']
            
            p.setBrush(b['color'])
            
            # Draw individual cells of the shape
            for r_idx, row in enumerate(b['shape']):
                for c_idx, cell in enumerate(row):
                    if cell:
                        bx = b['x'] + c_idx * self.block_size
                        by = b['y'] + r_idx * self.block_size
                        
                        # Simple 3D effect (bevel)
                        rect = QRectF(bx, by, self.block_size, self.block_size)
                        p.drawRect(rect)
                        
                        # Highlight
                        p.setBrush(QColor(255, 255, 255, 100))
                        p.drawRect(bx, by, self.block_size, 5)
                        p.drawRect(bx, by, 5, self.block_size)
                        p.setBrush(b['color']) # Reset
            
            if b['y'] > h:
                self.blocks.remove(b)
