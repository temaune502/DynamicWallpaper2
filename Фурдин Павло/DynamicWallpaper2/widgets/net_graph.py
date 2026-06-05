from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPolygonF
import psutil
import time
from widgets import BaseWidget

class NetGraphWidget(BaseWidget):
    WIDGET_NAME = "net_graph"
    
    def __init__(self, config=None):
        super().__init__(config)
        self.history_len = 60
        self.upload_history = [0] * self.history_len
        self.download_history = [0] * self.history_len
        
        self.last_io = psutil.net_io_counters()
        self.last_time = time.time()
        
        self.max_val = 1024 * 10 # Initial scaling (10 KB/s)

    def draw(self, p: QPainter, w: int, h: int, phase: float = 0.0):
        # Update Data
        now = time.time()
        dt = now - self.last_time
        if dt > 1.0:
            current_io = psutil.net_io_counters()
            
            sent = current_io.bytes_sent - self.last_io.bytes_sent
            recv = current_io.bytes_recv - self.last_io.bytes_recv
            
            # Convert to B/s
            speed_up = sent / dt
            speed_down = recv / dt
            
            self.upload_history.append(speed_up)
            self.download_history.append(speed_down)
            
            if len(self.upload_history) > self.history_len:
                self.upload_history.pop(0)
                self.download_history.pop(0)
                
            self.last_io = current_io
            self.last_time = now
            
            # Dynamic Scaling
            curr_max = max(max(self.upload_history), max(self.download_history))
            if curr_max > self.max_val:
                self.max_val = curr_max
            elif curr_max < self.max_val * 0.8 and self.max_val > 10240:
                self.max_val *= 0.95

        # Draw
        total_w = 250
        total_h = 100
        x, y = self.get_pos(w, h, total_w, total_h)
        
        # BG
        p.setBrush(QColor(10, 10, 20, 200)) # Dark Grid
        p.setPen(QPen(QColor(0, 255, 255, 50), 1))
        p.drawRect(x, y, total_w, total_h)
        
        # Grid lines
        p.setPen(QPen(QColor(0, 255, 255, 20), 1))
        p.drawLine(x, y + total_h//2, x + total_w, y + total_h//2)
        for i in range(1, 4):
             xg = x + i * (total_w // 4)
             p.drawLine(xg, y, xg, y + total_h)
             
        # Plot Charts
        # Download (Cyan)
        self._draw_chart(p, x, y, total_w, total_h, self.download_history, QColor(0, 255, 255), True)
        
        # Upload (Magenta)
        self._draw_chart(p, x, y, total_w, total_h, self.upload_history, QColor(255, 0, 255), False)
        
        # Text Stats
        curr_down = self.download_history[-1]
        curr_up = self.upload_history[-1]
        
        p.setFont(QFont("Consolas", 9, QFont.Bold))
        
        # Down
        p.setPen(QColor(0, 255, 255))
        p.drawText(x + 5, y + 15, f"DL: {self._fmt_speed(curr_down)}")
        
        # Up
        p.setPen(QColor(255, 0, 255))
        p.drawText(x + 5, y + 30, f"UL: {self._fmt_speed(curr_up)}")

    def _draw_chart(self, p, x, y, w, h, data, color, fill=False):
        if not data: return
        
        points = []
        step_x = w / (len(data) - 1)
        
        for i, val in enumerate(data):
            px = x + i * step_x
            # Normalize height
            norm = val / max(1, self.max_val)
            norm = min(1.0, norm)
            py = y + h - (norm * (h - 20)) # Keep padding top
            points.append(QPointF(px, py))
            
        if fill:
            poly_points = points.copy()
            poly_points.append(QPointF(x + w, y + h))
            poly_points.append(QPointF(x, y + h))
            
            c_fill = QColor(color)
            c_fill.setAlpha(50)
            p.setBrush(c_fill)
            p.setPen(Qt.NoPen)
            p.drawPolygon(QPolygonF(poly_points))
            
        p.setPen(QPen(color, 2))
        p.setBrush(Qt.NoBrush)
        p.drawPolyline(points)

    def _fmt_speed(self, b_s):
        if b_s < 1024: return f"{int(b_s)} B/s"
        elif b_s < 1024**2: return f"{b_s/1024:.1f} KB/s"
        else: return f"{b_s/(1024**2):.1f} MB/s"
