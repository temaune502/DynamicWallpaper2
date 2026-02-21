from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QColor, QLinearGradient
import math
import random
from widgets import BaseWidget

class MatrixRainWidget(BaseWidget):
    """
    Віджет, що імітує дощ із символів у стилі Матриці.
    Динамічний, стильний і не потребує зовнішніх API.
    """
    WIDGET_NAME = "matrix_rain"
    
    def __init__(self, config=None):
        super().__init__(config)
        self.columns = []
        self.num_columns = 15
        self.chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$#@&%*+=-/<>[]{}"
        self.speed = self.config.get("speed", 1.0)
        self.color = QColor(self.config.get("color", "#00FF41"))
        
        # Ініціалізація колонок
        for _ in range(self.num_columns):
            self.columns.append({
                "x_rel": random.random(), # Відносна позиція по X
                "y_rel": random.random() * -1.0, # Початкова позиція зверху
                "speed": (0.005 + random.random() * 0.01) * self.speed,
                "length": random.randint(5, 15),
                "chars": [random.choice(self.chars) for _ in range(20)]
            })

    def draw(self, p: QPainter, w: int, h: int, phase: float = 0.0):
        p.setRenderHint(QPainter.Antialiasing)
        
        total_w = 200
        total_h = 200
        start_x, start_y = self.get_pos(w, h, total_w, total_h)
        
        # Малюємо фон (напівпрозорий темний прямокутник)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 0, 0, 40))
        p.drawRoundedRect(start_x, start_y, total_w, total_h, 15, 15)
        
        # Обрізаємо малювання по межах віджета
        p.setClipRect(QRectF(start_x, start_y, total_w, total_h))
        
        char_size = 14
        p.setFont(self.get_font(char_size, bold=True))
        
        for col in self.columns:
            # Оновлюємо позицію (на основі фази або просто лінійно)
            # Тут ми використовуємо фазу для синхронізації, але додаємо власну швидкість
            y_pos = (col["y_rel"] + phase * self.speed) % 2.0 - 0.5
            x_pos = start_x + col["x_rel"] * total_w
            
            for i in range(col["length"]):
                char_y = start_y + (y_pos * total_h) - (i * char_size)
                
                if start_y <= char_y <= start_y + total_h:
                    # Перший символ найяскравіший (білий)
                    if i == 0:
                        p.setPen(QColor(255, 255, 255, 255))
                        # Випадково змінюємо символ
                        if random.random() > 0.95:
                            col["chars"][i] = random.choice(self.chars)
                    else:
                        # Інші символи згасають (зелений градієнт)
                        alpha = int(255 * (1.0 - i / col["length"]))
                        p.setPen(QColor(self.color.red(), self.color.green(), self.color.blue(), alpha))
                    
                    p.drawText(QPointF(x_pos, char_y), col["chars"][i % len(col["chars"])])
                    
        p.setClipping(False)

    def get_font(self, size, bold=False):
        from PySide6.QtGui import QFont
        font = QFont("Consolas", size)
        if bold: font.setBold(True)
        return font
