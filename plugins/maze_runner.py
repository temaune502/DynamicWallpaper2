import random
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QBrush, QPen

from effects import BaseEffect

class MazeRunnerEffect(BaseEffect):
    EFFECT_NAME = "maze_runner"

    def __init__(self):
        super().__init__()
        self.cols = 40
        self.rows = 24
        self.cell_size = 40
        self.maze = [] # 2D array: 0=wall, 1=path, 2=visited
        self.stack = []
        self.current = (0, 0)
        self.generated = False
        self.runner = None
        self.runner_path = []
        
        self.reset_maze()

    def reset_maze(self):
        # Prim's or Recursive Backtracker
        # Let's do Recursive Backtracker (DFS)
        self.maze = [[1 for _ in range(self.cols)] for _ in range(self.rows)] 
        # Actually standard maze needs grid cells and walls between.
        # Simplified: Grid of cells, each has walls [top, right, bottom, left]
        
        self.grid = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                row.append({'visited': False, 'walls': [True, True, True, True]})
            self.grid.append(row)
            
        self.current = (0, 0)
        self.grid[0][0]['visited'] = True
        self.stack = [(0, 0)]
        self.generated = False
        self.runner = None

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        p.fillRect(0, 0, w, h, QColor(20, 20, 20))
        
        # Calculate offset to center
        grid_w = self.cols * self.cell_size
        grid_h = self.rows * self.cell_size
        off_x = (w - grid_w) / 2
        off_y = (h - grid_h) / 2
        
        p.translate(off_x, off_y)
        
        # Generation Step (Multiple per frame for speed)
        if not self.generated:
            for _ in range(5):
                if self.stack:
                    cx, cy = self.current
                    neighbors = []
                    
                    # Check neighbors
                    dirs = [(0, -1, 0, 2), (1, 0, 1, 3), (0, 1, 2, 0), (-1, 0, 3, 1)] # dx, dy, wall_idx, opp_wall_idx
                    
                    for dx, dy, wall, opp_wall in dirs:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < self.cols and 0 <= ny < self.rows and not self.grid[ny][nx]['visited']:
                            neighbors.append((nx, ny, wall, opp_wall))
                            
                    if neighbors:
                        nx, ny, wall, opp_wall = random.choice(neighbors)
                        
                        # Remove walls
                        self.grid[cy][cx]['walls'][wall] = False
                        self.grid[ny][nx]['walls'][opp_wall] = False
                        
                        self.current = (nx, ny)
                        self.grid[ny][nx]['visited'] = True
                        self.stack.append((nx, ny))
                    else:
                        self.current = self.stack.pop()
                else:
                    self.generated = True
                    self.spawn_runner()
                    break
        
        # Runner Step
        if self.generated and self.runner:
            # Simple right-hand rule or just DFS solver
            # Let's use simple DFS to endpoint
            if self.runner != (self.cols-1, self.rows-1):
                # Move logic...
                # (For visual effect, we just made it static for now, implementing solver is complex in draw loop)
                pass

        # Draw Maze
        p.setPen(QPen(QColor(0, 255, 255), 2))
        
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                x = c * self.cell_size
                y = r * self.cell_size
                
                if cell['walls'][0]: p.drawLine(x, y, x + self.cell_size, y) # Top
                if cell['walls'][1]: p.drawLine(x + self.cell_size, y, x + self.cell_size, y + self.cell_size) # Right
                if cell['walls'][2]: p.drawLine(x + self.cell_size, y + self.cell_size, x, y + self.cell_size) # Bottom
                if cell['walls'][3]: p.drawLine(x, y + self.cell_size, x, y) # Left
                
                # Highlight current generation head
                if not self.generated and (c, r) == self.current:
                    p.fillRect(x+5, y+5, self.cell_size-10, self.cell_size-10, QColor(255, 0, 0))

    def spawn_runner(self):
        self.runner = (0, 0)
