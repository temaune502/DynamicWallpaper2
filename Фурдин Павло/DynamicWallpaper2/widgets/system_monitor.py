from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient
import psutil
from widgets import BaseWidget

class SystemMonitorWidget(BaseWidget):
    WIDGET_NAME = "system_monitor"
    
    def __init__(self, config=None):
        super().__init__(config)
        self.config.setdefault('update_interval', 1000)
        self.cpu_history = []
        self.ram_history = []
        
        # Throttling
        self.last_update = 0
        self.cached_cpu = 0
        self.cached_ram = 0
        self.cached_disk = 0
        
        # Colors
        self.cpu_color = QColor(0, 255, 127) # Spring Green
        self.ram_color = QColor(0, 120, 255) # Blue
        self.bg_color = QColor(20, 20, 30, 180) # Dark transparent
        
    def draw(self, p: QPainter, w: int, h: int, phase: float = 0.0):
        import time
        # Data Update (1s throttle)
        if time.time() - self.last_update > 1.0:
            self.cached_cpu = psutil.cpu_percent()
            self.cached_ram = psutil.virtual_memory().percent
            self.cached_disk = psutil.disk_usage('/').percent
            self.last_update = time.time()
            
        cpu = self.cached_cpu
        ram = self.cached_ram
        disk = self.cached_disk
        
        # Dimensions
        total_w = 220
        total_h = 110
        x, y = self.get_pos(w, h, total_w, total_h)
        
        # 1. Glass Background
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(self.bg_color)
        p.drawRoundedRect(x, y, total_w, total_h, 15, 15)
        
        # Border glow
        border_pen = QPen(QColor(255, 255, 255, 30), 1)
        p.setPen(border_pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(x, y, total_w, total_h, 15, 15)

        # 2. CPU Circular Gauge (Left side)
        cx, cy = x + 60, y + 55
        radius = 35
        
        # Track
        p.setPen(QPen(QColor(255, 255, 255, 20), 6, Qt.SolidLine, Qt.RoundCap))
        p.drawEllipse(QPointF(cx, cy), radius, radius)
        
        # Arc
        angle = int(-cpu * 3.6 * 16) # 16 units per degree
        start_angle = 90 * 16 # Top
        
        p.setPen(QPen(self.cpu_color, 6, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(int(cx - radius), int(cy - radius), int(radius*2), int(radius*2), start_angle, angle)
        
        # Text Center
        p.setFont(QFont("Segoe UI", 12, QFont.Bold))
        p.setPen(Qt.white)
        p.drawText(QRectF(cx - 30, cy - 15, 60, 30), Qt.AlignCenter, f"{int(cpu)}%")
        
        p.setFont(QFont("Segoe UI", 8))
        p.setPen(QColor(200, 200, 200))
        p.drawText(QRectF(cx - 30, cy + 10, 60, 20), Qt.AlignCenter, "CPU")
        
        # 3. RAM Progress Bar (Right side)
        rx = x + 110
        ry = y + 30
        rw = 90
        
        # Label
        p.setFont(QFont("Segoe UI", 9, QFont.Bold))
        p.setPen(Qt.white)
        p.drawText(rx, ry, "RAM")
        
        # Value
        p.setPen(self.ram_color)
        p.drawText(rx + 50, ry, f"{int(ram)}%")
        
        # Bar BG
        bar_y = ry + 10
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 20))
        p.drawRoundedRect(rx, bar_y, rw, 8, 4, 4)
        
        # Bar Fill
        fill_w = max(4, int(rw * (ram / 100.0)))
        p.setBrush(self.ram_color)
        p.drawRoundedRect(rx, bar_y, fill_w, 8, 4, 4)
        
        # 4. Storage/Disk (Optional simple line below RAM)
        # Let's add Disk Usage
        disk = psutil.disk_usage('/').percent
        dy = bar_y + 25
        
        p.setPen(Qt.white)
        p.drawText(rx, dy, "DISK")
        p.setPen(QColor(255, 100, 255))
        p.drawText(rx + 50, dy, f"{int(disk)}%")
        
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 20))
        p.drawRoundedRect(rx, dy + 10, rw, 8, 4, 4)
        
        fill_disk = max(4, int(rw * (disk / 100.0)))
        p.setBrush(QColor(255, 100, 255))
        p.drawRoundedRect(rx, dy + 10, fill_disk, 8, 4, 4)

from PySide6.QtCore import QPointF
