import random
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QBrush

from effects import BaseEffect

class ConwayLifeEffect(BaseEffect):
    EFFECT_NAME = "conway_life"

    def __init__(self):
        super().__init__()
        self.cell_size = 10
        self.cols = 0
        self.rows = 0
        self.grid = []
        self.init_done = False
        self.tick_timer = 0
        
    def _init_grid(self, w, h):
        self.cols = w // self.cell_size
        self.rows = h // self.cell_size
        self.grid = [[random.choice([0, 1]) if random.random() < 0.2 else 0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.init_done = True

    def _step(self):
        new_grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        
        for r in range(self.rows):
            for c in range(self.cols):
                # Count neighbors
                neighbors = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if i == 0 and j == 0: continue
                        nr, nc = r + i, c + j
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if self.grid[nr][nc]: neighbors += 1
                
                cell = self.grid[r][c]
                if cell == 1:
                    if neighbors < 2 or neighbors > 3:
                        new_grid[r][c] = 0 # Die
                    else:
                        new_grid[r][c] = 1 # Live
                else:
                    if neighbors == 3:
                        new_grid[r][c] = 1 # Born
                        
        self.grid = new_grid
        
        # Random respawn if empty
        if random.random() < 0.05:
            rx, ry = random.randint(0, self.cols-1), random.randint(0, self.rows-1)
            # Glider spawn maybe?
            self.grid[ry][rx] = 1

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        if not self.init_done:
            self._init_grid(w, h)
            
        p.fillRect(0, 0, w, h, QColor(0, 0, 0))
        
        self.tick_timer += 1
        if self.tick_timer > 5: # Limit speed
            self._step()
            self.tick_timer = 0
            
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 255, 0))
        
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c]:
                    # Fade color based on position?
                    hue = (c / self.cols + phase) % 1.0
                    col = QColor.fromHsvF(hue, 0.8, 1.0, 1.0)
                    p.setBrush(col)
                    
                    p.drawRect(c * self.cell_size, r * self.cell_size, self.cell_size - 1, self.cell_size - 1)
