from collections import deque
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QCursor, QPen

from effects import BaseEffect

class NeonCursorEffect(BaseEffect):
    EFFECT_NAME = "neon_cursor"

    def __init__(self):
        super().__init__()
        self.trail = deque(maxlen=50)

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        p.fillRect(0, 0, w, h, QColor(0, 0, 0))
        
        mouse_pos = QCursor.pos()
        mx, my = mouse_pos.x(), mouse_pos.y()
        
        # Add current position
        self.trail.append((mx, my))
        
        if len(self.trail) < 2:
            return
            
        p.setRenderHint(QPainter.Antialiasing)
        
        # Draw trail
        prev_x, prev_y = self.trail[0]
        
        for i in range(1, len(self.trail)):
            curr_x, curr_y = self.trail[i]
            
            # Progress 0..1
            prog = i / len(self.trail)
            
            # Width and Color
            width = prog * 20
            
            # Rainbow cycle
            hue = (phase + prog) % 1.0
            color = QColor.fromHsvF(hue, 1.0, 1.0, prog) # Fade out tail (alpha = prog)
            
            pen = QPen(color, width, Qt.SolidLine, Qt.RoundCap)
            p.setPen(pen)
            
            p.drawLine(QPointF(prev_x, prev_y), QPointF(curr_x, curr_y))
            
            prev_x, prev_y = curr_x, curr_y
