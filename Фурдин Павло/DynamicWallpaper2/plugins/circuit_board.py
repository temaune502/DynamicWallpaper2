import random
import math
from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtCore import Qt, QPointF
from effects import BaseEffect

class CircuitBoardEffect(BaseEffect):
    EFFECT_NAME = "circuit_board"
    
    def __init__(self):
        super().__init__()
        self.traces = None
        self.max_traces = 40
        self.bg_dots = None

    def draw(self, p, w, h, phase):
        if self.traces is None:
            self.traces = []
            self.bg_dots = []
            # Create background grid dots
            for x in range(0, w + 40, 40):
                for y in range(0, h + 40, 40):
                    self.bg_dots.append((x, y))
            
            # Initial traces
            for _ in range(self.max_traces // 2):
                self.traces.append(self._create_trace(w, h))

        # 1. Background
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(10, 15, 10))
            # Grid dots
            p.setPen(QPen(QColor(0, 100, 0, 50), 2))
            for dx, dy in self.bg_dots:
                p.drawPoint(dx, dy)

        # 2. Update and Draw Traces
        p.setBrush(Qt.NoBrush)
        active_traces = []
        
        # Add new traces occasionally
        if len(self.traces) < self.max_traces and random.random() < 0.1:
            self.traces.append(self._create_trace(w, h))

        for t in self.traces:
            # Advance trace
            if not t['finished']:
                t['age'] += 1
                last_pt = t['path'][-1]
                new_x = last_pt.x() + t['vx'] * t['speed']
                new_y = last_pt.y() + t['vy'] * t['speed']
                
                # Boundary check or random turn
                if (new_x < 0 or new_x > w or new_y < 0 or new_y > h or 
                    t['age'] > t['max_age'] or random.random() < 0.02):
                    
                    if t['age'] > 10 and random.random() < 0.7:
                        # Try to turn 90 degrees
                        old_vx, old_vy = t['vx'], t['vy']
                        if random.random() < 0.5:
                            t['vx'], t['vy'] = -old_vy, old_vx
                        else:
                            t['vx'], t['vy'] = old_vy, -old_vx
                        t['age'] = 0 # reset age for the new segment
                        t['max_age'] = random.randint(10, 40)
                    else:
                        t['finished'] = True
                
                if not t['finished']:
                    t['path'].append(QPointF(new_x, new_y))

            # Draw the trace
            alpha = int(200 * (1.0 - t['life'] / 100))
            if alpha > 0:
                color = QColor(0, 255, 120, alpha)
                p.setPen(QPen(color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                p.drawPolyline(t['path'])
                
                # Draw "head" glow
                if not t['finished']:
                    head = t['path'][-1]
                    p.setPen(QPen(QColor(255, 255, 255, alpha), 3))
                    p.drawPoint(head)

                # Draw nodes at start/end
                p.setPen(QPen(color, 1))
                p.setBrush(QColor(0, 50, 20, alpha))
                start = t['path'][0]
                p.drawEllipse(start, 4, 4)
                
                if t['finished']:
                    end = t['path'][-1]
                    p.setBrush(QColor(0, 255, 120, alpha))
                    p.drawEllipse(end, 3, 3)
                    t['life'] += 1 # start fading out
            
            if t['life'] < 100:
                active_traces.append(t)
        
        self.traces = active_traces

    def _create_trace(self, w, h):
        # Align to grid
        x = random.randrange(0, w, 40)
        y = random.randrange(0, h, 40)
        
        # Directions: Up, Down, Left, Right
        dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        vx, vy = random.choice(dirs)
        
        return {
            'path': [QPointF(x, y)],
            'vx': vx,
            'vy': vy,
            'speed': 3.0,
            'age': 0,
            'max_age': random.randint(15, 50),
            'finished': False,
            'life': 0 # for fading after finish
        }
