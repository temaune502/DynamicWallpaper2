import math
import random
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen, QBrush

# Спроба імпортувати BaseEffect з основного модуля
try:
    from effects import BaseEffect
except ImportError:
    # Якщо запуск поза основним додатком (наприклад, для тестування)
    class BaseEffect:
        def __init__(self): self.show_background = True
        def draw(self, p, w, h, phase): pass

class DynamicCircleEffect(BaseEffect):
    """ Приклад зовнішнього ефекту, який можна редагувати 'на льоту' """
    
    # Можна вказати спеціальне ім'я для реєстру
    EFFECT_NAME = "dynamic"

    def __init__(self):
        super().__init__()
        self.circles = []

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        # Малюємо тло, якщо воно увімкнене
        if self.show_background:
            p.fillRect(0, 0, w, h, QColor(20, 20, 30))

        # Додаємо нове коло час від часу
        if len(self.circles) < 20 and random.random() < 0.1:
            self.circles.append({
                'x': random.randint(0, w),
                'y': random.randint(0, h),
                'r': 0,
                'max_r': random.randint(50, 200),
                'color': QColor.fromHsv(random.randint(0, 360), 200, 255, 150)
            })

        p.setBrush(Qt.NoBrush)
        
        # Оновлюємо та малюємо кола
        remaining = []
        for c in self.circles:
            c['r'] += 2
            if c['r'] < c['max_r']:
                alpha = int(255 * (1 - c['r'] / c['max_r']))
                color = c['color']
                color.setAlpha(alpha)
                
                p.setPen(QPen(color, 3))
                p.drawEllipse(int(c['x'] - c['r']), int(c['y'] - c['r']), 
                             int(c['r'] * 2), int(c['r'] * 2))
                remaining.append(c)
        
        self.circles = remaining

        # Текст-підказка
        p.setPen(QColor(255, 255, 255, 100))
        p.drawText(20, h - 20, "Цей ефект завантажено динамічно з папки plugins!")
