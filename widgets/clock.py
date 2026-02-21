from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPainter, QColor, QFont
import math
from widgets import BaseWidget


class TimeDateWidget(BaseWidget):
    WIDGET_NAME = "clock"
    
    def draw(self, p: QPainter, w: int, h: int, phase: float = 0.0):
        now = QDateTime.currentDateTime()
        time_str = now.toString(self.config.get('time_format', "HH:mm"))
        date_str = now.toString(self.config.get('date_format', "ddd, d MMM"))

        base_size = min(w, h)
        time_size = self.config.get('time_size', base_size // 18)
        date_size = self.config.get('date_size', base_size // 45)
        
        time_font = QFont("Segoe UI", time_size, QFont.DemiBold)
        date_font = QFont("Segoe UI", date_size, QFont.Normal)

        p.setFont(time_font)
        time_metrics = p.fontMetrics()
        time_rect = time_metrics.boundingRect(time_str)
        
        p.setFont(date_font)
        date_metrics = p.fontMetrics()
        date_rect = date_metrics.boundingRect(date_str)

        total_w = max(time_rect.width(), date_rect.width())
        total_h = time_rect.height() + date_rect.height() // 2 + 10

        start_x, start_y = self.get_pos(w, h, total_w, total_h)
        glow = 0.5 + 0.5 * math.sin(phase * 2 * math.pi)
        
        p.setFont(time_font)
        p.setPen(QColor(0, 0, 0, int(80 + 40 * glow)))
        p.drawText(start_x + 2, start_y + time_rect.height() + 2, time_str)
        p.setPen(QColor(255, 255, 255, int(200 + 55 * glow)))
        p.drawText(start_x, start_y + time_rect.height(), time_str)

        p.setFont(date_font)
        date_y = start_y + time_rect.height() + date_rect.height() // 2 + 5
        p.setPen(QColor(0, 0, 0, 120))
        p.drawText(start_x + 1, date_y + 1, date_str)
        p.setPen(QColor(200, 220, 255, 180))
        p.drawText(start_x, date_y, date_str)
