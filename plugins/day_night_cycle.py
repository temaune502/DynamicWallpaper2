import math
import time
import random
from PySide6.QtGui import QColor, QLinearGradient, QBrush, QPen, QRadialGradient
from PySide6.QtCore import Qt, QPointF
from effects import BaseEffect

class DayNightCycleEffect(BaseEffect):
    EFFECT_NAME = "day_night_cycle"
    
    def __init__(self):
        super().__init__()
        self.stars = None
        self.comets = []
        self.clouds = None
        self.mountains = None
        self.DEBUG_MODE = False 
        self.speed_factor = 1.0 # 1.0 = Real time, >1 = Fast forward
        self.demo_mode = False # If true, cycle repeatedly
        self.manual_time = -1.0 # -1 = auto

    @classmethod
    def get_schema(cls):
        return {
            "demo_mode": {
                "type": "bool",
                "default": False,
                "label": "Demo Mode (Fast Cycle)"
            },
            "speed": {
                "type": "float",
                "min": 0.1,
                "max": 10.0,
                "default": 1.0,
                "label": "Demo Speed"
            }
        }

    def configure(self, config: dict):
        if 'demo_mode' in config: self.demo_mode = bool(config['demo_mode'])
        if 'speed' in config: self.speed_factor = float(config['speed'])

    def draw(self, p, w, h, phase):
        if self.demo_mode:
            # Cycle based on phase and speed
            # phase is usually increasing 0.01 per frame
            # 2pi cycle
            time_factor = (phase * 0.05 * self.speed_factor) % 1.0 
        else:
            if self.DEBUG_MODE:
                 time_factor = (phase * 0.1) % 1.0 
            else:
                t = time.localtime()
                current_hour = t.tm_hour + t.tm_min / 60.0 + t.tm_sec / 3600.0
                time_factor = current_hour / 24.0

        # Положення горизонту
        horizon_y = h * 0.7

        # 1. Траєкторія Сонця та Місяця
        sun_angle = (time_factor * 2 * math.pi) - math.pi
        sun_x = w/2 + math.cos(sun_angle) * (w * 0.7)
        sun_y = horizon_y + math.sin(sun_angle) * (h * 0.6)

        moon_angle = sun_angle + math.pi
        moon_x = w/2 + math.cos(moon_angle) * (w * 0.7)
        moon_y = horizon_y + math.sin(moon_angle) * (h * 0.6)

        # 2. Логіка кольорів неба
        sun_height = -math.sin(sun_angle) 
        
        sky_grad = QLinearGradient(0, 0, 0, horizon_y)
        
        if sun_height > 0.15: # День
            c1 = QColor(70, 150, 255) 
            c2 = QColor(140, 200, 255)
        elif sun_height > -0.15: # Світанок / Захід
            p_val = (sun_height + 0.15) / 0.3
            # Золота година
            c1 = self._blend_colors(QColor(10, 10, 40), QColor(255, 100, 50), p_val)
            c2 = self._blend_colors(QColor(0, 0, 10), QColor(255, 180, 100), p_val)
        else: # Ніч
            c1 = QColor(2, 2, 15)
            c2 = QColor(5, 5, 25)

        sky_grad.setColorAt(0, c1)
        sky_grad.setColorAt(1, c2)
        if self.show_background:
            p.fillRect(0, 0, w, horizon_y, QBrush(sky_grad))

        # 3. Зірки
        star_alpha = int(max(0, min(255, -sun_height * 500 - 50)))
        if star_alpha > 0:
            if self.stars is None:
                self.stars = []
                for _ in range(200):
                    self.stars.append({
                        'x': random.uniform(0, w),
                        'y': random.uniform(0, horizon_y),
                        'size': random.uniform(0.5, 1.8),
                        'blink_speed': random.uniform(1, 3),
                        'blink_offset': random.uniform(0, math.pi * 2)
                    })
            for s in self.stars:
                blink = (math.sin(phase * s['blink_speed'] + s['blink_offset']) * 0.5 + 0.5)
                current_alpha = int(star_alpha * (0.4 + 0.6 * blink))
                p.setPen(QColor(255, 255, 255, current_alpha))
                p.drawEllipse(QPointF(s['x'], s['y']), s['size'], s['size'])

        # 4. Хмари
        if self.clouds is None:
            self.clouds = []
            for _ in range(8):
                self.clouds.append({
                    'x': random.uniform(-100, w),
                    'y': random.uniform(50, horizon_y - 100),
                    'speed': random.uniform(0.2, 0.5),
                    'scale': random.uniform(0.8, 1.5),
                    'parts': [{'ox': random.uniform(-30, 30), 'oy': random.uniform(-10, 10), 'r': random.uniform(20, 40)} for _ in range(5)]
                })
        
        # Колір хмар залежно від сонця
        if sun_height > 0.2:
            cloud_color = QColor(255, 255, 255, 180)
        elif sun_height > -0.1:
            p_val = (sun_height + 0.1) / 0.3
            cloud_color = self._blend_colors(QColor(80, 50, 80, 150), QColor(255, 200, 150, 200), p_val)
        else:
            cloud_color = QColor(20, 20, 40, 100)

        for c in self.clouds:
            c['x'] = (c['x'] + c['speed']) % (w + 200)
            p.setBrush(cloud_color)
            p.setPen(Qt.NoPen)
            for part in c['parts']:
                p.drawEllipse(QPointF(c['x'] - 100 + part['ox'], c['y'] + part['oy']), part['r'] * c['scale'], part['r'] * c['scale'])

        # 5. Місяць
        moon_alpha = int(max(0, min(255, -sun_height * 400 + 100)))
        if moon_alpha > 0:
            p.setBrush(QColor(230, 230, 255, moon_alpha))
            p.drawEllipse(QPointF(moon_x, moon_y), 35, 35)
            p.setBrush(c1)
            p.drawEllipse(QPointF(moon_x + 10, moon_y - 5), 35, 35)

        # 6. Сонце
        if sun_y < horizon_y + 100:
            glow_alpha = int(max(0, min(180, sun_height * 600)))
            if glow_alpha > 0:
                grad = QRadialGradient(sun_x, sun_y, 150)
                grad.setColorAt(0, QColor(255, 200, 50, glow_alpha))
                grad.setColorAt(1, Qt.transparent)
                p.setBrush(grad)
                p.drawEllipse(QPointF(sun_x, sun_y), 150, 150)
            p.setBrush(QColor(255, 255, 220))
            p.drawEllipse(QPointF(sun_x, sun_y), 40, 40)

        # 7. Ландшафт та Вода
        # Малюємо воду спочатку
        water_grad = QLinearGradient(0, horizon_y, 0, h)
        if sun_height > 0:
            w1 = self._blend_colors(c2, QColor(50, 100, 200), 0.5)
            w2 = QColor(20, 40, 100)
        else:
            w1 = QColor(5, 10, 30)
            w2 = QColor(2, 5, 15)
        
        water_grad.setColorAt(0, w1)
        water_grad.setColorAt(1, w2)
        p.fillRect(0, int(horizon_y), int(w), int(h - horizon_y), QBrush(water_grad))

        # Відображення сонця/місяця у воді
        if sun_height > -0.2: # Сонце
            ref_y = horizon_y + (horizon_y - sun_y)
            ref_alpha = int(max(0, min(150, sun_height * 400)))
            if ref_alpha > 0:
                grad = QRadialGradient(sun_x, ref_y, 100)
                grad.setColorAt(0, QColor(255, 220, 100, ref_alpha))
                grad.setColorAt(1, Qt.transparent)
                p.setBrush(grad)
                p.drawEllipse(QPointF(sun_x, ref_y), 120, 40)

        # Гори
        if self.mountains is None:
            self.mountains = []
            # Дальні гори
            m1 = []
            for i in range(11):
                m1.append(QPointF(i * (w/10), horizon_y - random.uniform(50, 120)))
            self.mountains.append(m1)
            # Ближчі гори
            m2 = []
            for i in range(11):
                m2.append(QPointF(i * (w/10), horizon_y - random.uniform(20, 60)))
            self.mountains.append(m2)

        # Колір гір залежить від освітлення
        m_color1 = self._blend_colors(QColor(10, 20, 40), QColor(60, 80, 120), max(0, sun_height))
        m_color2 = self._blend_colors(QColor(5, 10, 25), QColor(40, 60, 90), max(0, sun_height))

        for idx, m in enumerate(self.mountains):
            color = m_color1 if idx == 0 else m_color2
            p.setBrush(color)
            poly = [QPointF(0, horizon_y)] + m + [QPointF(w, horizon_y)]
            p.drawPolygon(poly)

        # Рябь на воді
        p.setPen(QPen(QColor(255, 255, 255, 30), 1))
        for _ in range(10):
            rx = random.uniform(0, w)
            ry = random.uniform(horizon_y, h)
            rw = random.uniform(20, 50)
            p.drawLine(int(rx), int(ry), int(rx + rw), int(ry))
    
    def _blend_colors(self, c1, c2, factor):
        factor = max(0, min(1, factor))
        r = int(c1.red() + (c2.red() - c1.red()) * factor)
        g = int(c1.green() + (c2.green() - c1.green()) * factor)
        b = int(c1.blue() + (c2.blue() - c1.blue()) * factor)
        return QColor(r, g, b)
