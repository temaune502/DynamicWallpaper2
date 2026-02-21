import time
import psutil
import collections
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QLinearGradient, QFont, QPolygonF

from effects import BaseEffect

class NetGraphEffect(BaseEffect):
    EFFECT_NAME = "net_graph"
    
    def __init__(self):
        super().__init__()
        self.history_size = 100
        self.download_history = collections.deque([0.0]*self.history_size, maxlen=self.history_size)
        self.upload_history = collections.deque([0.0]*self.history_size, maxlen=self.history_size)
        
        self.last_time = time.time()
        # Initialize last_io
        try:
            self.last_io = psutil.net_io_counters()
        except Exception:
            self.last_io = None

        self.current_down = 0.0
        self.current_up = 0.0
        self.max_val = 1024 * 1024 # Start with 1MB scale
        
        # Throttling
        self.update_interval = 0.5 # Update stats every 0.5s
        
        # Config
        self.show_grid = True
        self.line_width = 2
        self.color_down = QColor(0, 255, 255) # Cyan
        self.color_up = QColor(255, 0, 128)   # Magenta

    @classmethod
    def get_schema(cls):
        return {
            "interval": {
                "type": "float",
                "min": 0.1,
                "max": 5.0,
                "default": 0.5,
                "label": "Update Interval (s)"
            },
            "width": {
                "type": "int",
                "min": 1,
                "max": 10,
                "default": 2,
                "label": "Line Width"
            }
        }

    def configure(self, config: dict):
        if 'interval' in config: self.update_interval = float(config['interval'])
        if 'width' in config: self.line_width = int(config['width'])

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        # 1. Background
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(10, 10, 15))
            
        # 2. Grid lines
        if self.show_grid:
            p.setPen(QPen(QColor(255, 255, 255, 20), 1))
            # Horizontal lines
            for i in range(1, 5):
                y = h - (h * i / 5)
                p.drawLine(0, int(y), w, int(y))
            # Vertical lines
            for i in range(1, 10):
                x = w * i / 10
                p.drawLine(int(x), 0, int(x), h)
                
        # 3. Update Data
        now = time.time()
        dt = now - self.last_time
        
        if self.last_io and dt >= self.update_interval:
            try:
                io = psutil.net_io_counters()
                
                # Bytes since last check
                bytes_recv = io.bytes_recv - self.last_io.bytes_recv
                bytes_sent = io.bytes_sent - self.last_io.bytes_sent
                
                # Normalize to per second
                if dt > 0:
                    self.current_down = bytes_recv / dt
                    self.current_up = bytes_sent / dt
                
                self.download_history.append(self.current_down)
                self.upload_history.append(self.current_up)
                
                # Dynamic scaling
                local_max = max(max(self.download_history), max(self.upload_history))
                if local_max > 0:
                    # Smoothly adjust scale? Just snap for now, minimum 1KB
                    self.max_val = max(1024.0, local_max * 1.2) 
                
                self.last_io = io
                self.last_time = now
            except Exception:
                pass
            
        # 4. Draw Graphs
        
        # Build Points
        points_down = []
        points_up = []
        
        if self.history_size > 1:
            step_x = w / (self.history_size - 1)
        else:
            step_x = w

        # Download (Cyan)
        for i, val in enumerate(self.download_history):
            x = i * step_x
            # Invert Y so 0 is at bottom (h)
            # val/max_val is 0..1
            ratio = val / self.max_val
            if ratio > 1.0: ratio = 1.0
            y = h - (ratio * h)
            points_down.append(QPointF(x, y))
            
        # Upload (Magenta)
        for i, val in enumerate(self.upload_history):
            x = i * step_x
            ratio = val / self.max_val
            if ratio > 1.0: ratio = 1.0
            y = h - (ratio * h)
            points_up.append(QPointF(x, y))
            
        # Draw Up Fill (first so it's behind down if overlapping, or blend)
        # Using a semi-transparent brush
        
        # Up
        if len(points_up) > 1:
            poly_up = QPolygonF(points_up)
            poly_up.append(QPointF(points_up[-1].x(), h))
            poly_up.append(QPointF(points_up[0].x(), h))
            
            # Gradient
            grad = QLinearGradient(0, h, 0, 0) # Bottom to Top
            c = QColor(self.color_up)
            c.setAlpha(50)
            grad.setColorAt(0, c)
            c_top = QColor(self.color_up)
            c_top.setAlpha(150)
            grad.setColorAt(1, c_top)
            
            p.setPen(Qt.NoPen)
            p.setBrush(grad)
            p.drawPolygon(poly_up)
            
            # Line
            p.setPen(QPen(self.color_up, self.line_width))
            p.drawPolyline(points_up)

        # Down
        if len(points_down) > 1:
            poly_down = QPolygonF(points_down)
            poly_down.append(QPointF(points_down[-1].x(), h))
            poly_down.append(QPointF(points_down[0].x(), h))
            
            grad = QLinearGradient(0, h, 0, 0)
            c = QColor(self.color_down)
            c.setAlpha(50)
            grad.setColorAt(0, c)
            c_top = QColor(self.color_down)
            c_top.setAlpha(150)
            grad.setColorAt(1, c_top)
            
            p.setPen(Qt.NoPen)
            p.setBrush(grad)
            p.drawPolygon(poly_down)
            
            # Line
            p.setPen(QPen(self.color_down, self.line_width))
            p.drawPolyline(points_down)
            
        # 5. Text Info
        p.setFont(QFont("Consolas", 14, QFont.Bold))
        
        # Down Text
        p.setPen(self.color_down)
        down_str = self._format_speed(self.current_down)
        p.drawText(20, 40, f"DWN: {down_str}")
        
        # Up Text
        p.setPen(self.color_up)
        up_str = self._format_speed(self.current_up)
        p.drawText(20, 70, f"UP:  {up_str}")
        
        # Scale Text
        p.setPen(QColor(150, 150, 150))
        p.setFont(QFont("Arial", 10))
        scale_str = self._format_speed(self.max_val)
        p.drawText(w - 150, 30, f"Scale: {scale_str}")

    def _format_speed(self, bytes_sec):
        if bytes_sec < 1024:
            return f"{bytes_sec:.0f} B/s"
        elif bytes_sec < 1024**2:
            return f"{bytes_sec/1024:.1f} KB/s"
        elif bytes_sec < 1024**3:
            return f"{bytes_sec/1024**2:.1f} MB/s"
        else:
            return f"{bytes_sec/1024**3:.1f} GB/s"
