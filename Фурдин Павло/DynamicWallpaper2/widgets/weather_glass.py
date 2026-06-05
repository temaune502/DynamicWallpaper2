from PySide6.QtCore import Qt, QPointF, QThread, Signal, QRectF
from PySide6.QtGui import QPainter, QColor, QFont, QRadialGradient, QLinearGradient, QBrush, QPen
import math
import requests
import time
from widgets import BaseWidget

# Re-using the logic from the original weather widget but keeping code self-contained
class WeatherFetchThread(QThread):
    finished = Signal(dict)

    def __init__(self, city_name, country=None, region=None, lat=None, lon=None):
        super().__init__()
        self.city_name = city_name
        self.country = country
        self.region = region
        self.lat = lat
        self.lon = lon

    def run(self):
        try:
            import urllib.parse
            if self.lat is None or self.lon is None:
                q = self.city_name
                if self.country: q += f" {self.country}"
                safe_q = urllib.parse.quote(q)
                geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={safe_q}&count=1&language=en&format=json"
                
                resp = requests.get(geo_url, timeout=5)
                data = resp.json()
                if "results" in data and len(data["results"]) > 0:
                    res = data["results"][0]
                    self.lat = res["latitude"]
                    self.lon = res["longitude"]
                    self.city_name = res.get("name", self.city_name)
                else:
                    return

            url = f"https://api.open-meteo.com/v1/forecast?latitude={self.lat}&longitude={self.lon}&current_weather=true"
            data = requests.get(url, timeout=5).json()
            
            if "current_weather" in data:
                cw = data["current_weather"]
                code = cw["weathercode"]
                
                # Simple mapping
                cond = "Sunny"
                if code in [1, 2, 3, 45, 48]: cond = "Cloudy"
                elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: cond = "Rainy"
                elif code in [71, 73, 75, 77, 85, 86]: cond = "Snowy"
                elif code in [95, 96, 99]: cond = "Storm"
                
                self.finished.emit({
                    "temp": round(cw["temperature"]),
                    "condition": cond,
                    "wind": cw.get("windspeed", 0),
                    "city": self.city_name,
                    "lat": self.lat,
                    "lon": self.lon
                })
        except Exception as e:
            print(f"Weather fetch error: {e}")

class WeatherGlassWidget(BaseWidget):
    WIDGET_NAME = "weather_glass"
    
    def __init__(self, config=None):
        super().__init__(config)
        self.temp = "--"
        self.condition = "Sunny"
        self.wind = 0
        self.city = self.config.get('city', 'Kyiv')
        
        self.lat = self.config.get('lat')
        self.lon = self.config.get('lon')
        
        self.last_update = 0
        self.fetch_thread = None
        
    def _update_weather(self):
        if time.time() - self.last_update < 1800: # 30 mins
            return
        if self.fetch_thread and self.fetch_thread.isRunning():
            return
            
        self.fetch_thread = WeatherFetchThread(self.city, lat=self.lat, lon=self.lon)
        self.fetch_thread.finished.connect(self._on_data)
        self.fetch_thread.start()
        self.last_update = time.time()
        
    def _on_data(self, data):
        self.temp = data["temp"]
        self.condition = data["condition"]
        self.wind = data["wind"]
        self.city = data["city"]
        self.lat = data["lat"]
        self.lon = data["lon"]
        
        # Cache coord
        self.config['lat'] = self.lat
        self.config['lon'] = self.lon

    def draw(self, p: QPainter, w: int, h: int, phase: float = 0.0):
        self._update_weather()
        
        p.setRenderHint(QPainter.Antialiasing)
        
        total_w = 260
        total_h = 100
        x, y = self.get_pos(w, h, total_w, total_h)
        
        # 1. Glass Background
        grad = QLinearGradient(x, y, x, y + total_h)
        grad.setColorAt(0, QColor(255, 255, 255, 30))
        grad.setColorAt(1, QColor(255, 255, 255, 10))
        p.setBrush(grad)
        p.setPen(QPen(QColor(255, 255, 255, 50), 1))
        p.drawRoundedRect(x, y, total_w, total_h, 16, 16)
        
        # 2. Icon Area (Left)
        icon_cx = x + 50
        icon_cy = y + 50
        
        if self.condition == "Sunny":
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 220, 50))
            p.drawEllipse(QPointF(icon_cx, icon_cy), 20, 20)
            
            # Rays
            p.setPen(QPen(QColor(255, 200, 50, 150), 2))
            for i in range(8):
                angle = phase * 2 + i * (math.pi / 4)
                dx = math.cos(angle) * 30
                dy = math.sin(angle) * 30
                p.drawLine(QPointF(icon_cx, icon_cy), QPointF(icon_cx + dx, icon_cy + dy))
                
        elif self.condition == "Cloudy":
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(220, 220, 220, 200))
            p.drawEllipse(QPointF(icon_cx - 10, icon_cy + 5), 15, 15)
            p.drawEllipse(QPointF(icon_cx + 10, icon_cy + 5), 18, 18)
            p.drawEllipse(QPointF(icon_cx, icon_cy - 10), 16, 16)
            
        elif self.condition == "Rainy":
             # Cloud
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(100, 100, 120, 200))
            p.drawEllipse(QPointF(icon_cx, icon_cy - 5), 20, 15)
            # Rain
            p.setPen(QPen(QColor(100, 200, 255), 2))
            for i in range(3):
                offset = (phase * 20 + i * 10) % 20
                rx = icon_cx - 10 + i * 10
                ry = icon_cy + 10 + offset
                p.drawLine(QPointF(rx, ry), QPointF(rx, ry + 5))
                
        # 3. Info (Right)
        text_x = x + 100
        
        # Temp
        p.setFont(QFont("Segoe UI", 28, QFont.Bold))
        p.setPen(Qt.white)
        p.drawText(text_x, y + 45, f"{self.temp}°")
        
        # Condition
        p.setFont(QFont("Segoe UI", 12))
        p.setPen(QColor(255, 255, 255, 200))
        p.drawText(text_x, y + 70, self.condition)
        
        # City
        p.setFont(QFont("Segoe UI", 10, QFont.Bold))
        p.setPen(QColor(255, 255, 255, 150))
        p.drawText(x + 15, y + 25, self.city.upper())

    def cleanup(self):
        if self.fetch_thread:
            self.fetch_thread.terminate()
