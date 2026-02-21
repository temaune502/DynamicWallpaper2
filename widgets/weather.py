from PySide6.QtCore import Qt, QPointF, QThread, Signal
from PySide6.QtGui import QPainter, QColor, QFont, QRadialGradient
import math
import requests
import time
from widgets import BaseWidget

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
            # 1. Формуємо пошуковий запит
            if self.lat is None or self.lon is None:
                # Спробуємо кілька варіантів запиту для кращої точності
                queries_to_try = []
                
                # Варіант 1: Повний запит (Місто + Регіон + Країна)
                full_q = self.city_name
                if self.region: full_q += f" {self.region}"
                if self.country: full_q += f" {self.country}"
                queries_to_try.append(full_q)
                
                # Варіант 2: Тільки місто та країна
                if self.country:
                    queries_to_try.append(f"{self.city_name} {self.country}")
                
                # Варіант 3: Тільки місто
                queries_to_try.append(self.city_name)
                
                res = None
                for q in queries_to_try:
                    safe_q = urllib.parse.quote(q)
                    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={safe_q}&count=1&language=en&format=json"
                    geo_res = requests.get(geo_url, timeout=10)
                    geo_data = geo_res.json()
                    
                    if "results" in geo_data and len(geo_data["results"]) > 0:
                        res = geo_data["results"][0]
                        break
                
                if res:
                    self.lat = res["latitude"]
                    self.lon = res["longitude"]
                    found_name = res.get("name", self.city_name)
                else:
                    print(f"Location not found after trying: {queries_to_try}")
                    return
            else:
                found_name = self.city_name

            # 2. Отримуємо погоду
            url = f"https://api.open-meteo.com/v1/forecast?latitude={self.lat}&longitude={self.lon}&current_weather=true"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if "current_weather" in data:
                cw = data["current_weather"]
                code = cw["weathercode"]
                condition = "Sunny"
                if code in [1, 2, 3]: condition = "Cloudy"
                elif code in [45, 48]: condition = "Cloudy" # Fog
                elif code >= 51: condition = "Rainy"
                
                self.finished.emit({
                    "temp": round(cw["temperature"]),
                    "condition": condition,
                    "city": found_name,
                    "lat": self.lat,
                    "lon": self.lon
                })
        except Exception as e:
            print(f"Weather update error: {e}")

class WeatherWidget(BaseWidget):
    WIDGET_NAME = "weather"
    
    def __init__(self, config=None):
        super().__init__(config)
        self.temp = self.config.get('temp', "--")
        self.condition = self.config.get('condition', 'Sunny')
        
        # Назва для відображення (пріоритет: display_name -> city)
        self.display_name = self.config.get('display_name')
        self.city = self.config.get('city', 'Kyiv')
        
        # Додаткові параметри точності
        self.country = self.config.get('country')
        self.region = self.config.get('region')
        
        self.lat = self.config.get('lat')
        self.lon = self.config.get('lon')
        
        self.last_update = 0
        self.update_interval = 1800
        self.fetch_thread = None
        self._last_search_key = ""
        
    def _update_weather(self):
        # Ключ для перевірки змін (місто + регіон + країна)
        search_key = f"{self.config.get('city')}|{self.config.get('region')}|{self.config.get('country')}"
        
        if search_key != self._last_search_key:
            self.last_update = 0 
            self._last_search_key = search_key
            self.city = self.config.get('city', 'Kyiv')
            self.region = self.config.get('region')
            self.country = self.config.get('country')
            self.display_name = self.config.get('display_name')
            self.lat = self.config.get('lat')
            self.lon = self.config.get('lon')

        if time.time() - self.last_update < self.update_interval:
            return
            
        if self.fetch_thread and self.fetch_thread.isRunning():
            return
            
        self.fetch_thread = WeatherFetchThread(self.city, self.country, self.region, self.lat, self.lon)
        self.fetch_thread.finished.connect(self._on_weather_fetched)
        self.fetch_thread.start()
        self.last_update = time.time()

    def _on_weather_fetched(self, data):
        self.temp = data["temp"]
        self.condition = data["condition"]
        # Якщо display_name не задано, використовуємо офіційну назву міста
        if not self.display_name:
            self.city = data["city"]
        
        self.lat = data["lat"]
        self.lon = data["lon"]
        
        self.config['lat'] = self.lat
        self.config['lon'] = self.lon
        if not self.display_name:
            self.config['city'] = self.city

    def cleanup(self):
        """ Зупиняємо потік отримання погоди """
        if self.fetch_thread and self.fetch_thread.isRunning():
            self.fetch_thread.terminate()
            self.fetch_thread.wait()

    def __del__(self):
        self.cleanup()

    def draw(self, p: QPainter, w: int, h: int, phase: float = 0.0):
        self._update_weather()
        
        # Configuration
        font_city = QFont("Segoe UI", 10, QFont.Normal)
        font_temp = QFont("Segoe UI", 24, QFont.DemiBold)
        
        # Визначаємо текст міста для відображення
        city_text = self.display_name if self.display_name else self.city
        
        # Measure text
        p.setFont(font_temp)
        temp_str = f"{self.temp}°C"
        
        total_w = 150
        total_h = 70
        start_x, start_y = self.get_pos(w, h, total_w, total_h)
        
        # Background glow
        p.setPen(Qt.NoPen)
        grad = QRadialGradient(start_x + total_w/2, start_y + total_h/2, total_w)
        grad.setColorAt(0, QColor(0, 0, 0, 40))
        grad.setColorAt(1, Qt.transparent)
        p.setBrush(grad)
        p.drawRoundedRect(start_x, start_y, total_w, total_h, 15, 15)
        
        # 1. Draw Icon (Animated)
        icon_x = start_x + 30
        icon_y = start_y + 35
        
        p.setRenderHint(QPainter.Antialiasing)
        if self.condition == 'Sunny':
            glow = 0.5 + 0.5 * math.sin(phase * 2 * math.pi)
            p.setBrush(QColor(255, 200, 0, int(100 + 100 * glow)))
            p.drawEllipse(QPointF(icon_x, icon_y), 15 + 3 * glow, 15 + 3 * glow)
            p.setBrush(QColor(255, 255, 0, 255))
            p.drawEllipse(QPointF(icon_x, icon_y), 10, 10)
            
        elif self.condition == 'Cloudy':
            offset = 3 * math.sin(phase * 2 * math.pi)
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(200, 200, 200, 200))
            p.drawEllipse(QPointF(icon_x - 8, icon_y + offset), 10, 10)
            p.drawEllipse(QPointF(icon_x + 8, icon_y + offset), 12, 12)
            p.drawEllipse(QPointF(icon_x, icon_y - 8 + offset), 10, 10)
            
        elif self.condition == 'Rainy':
            # Cloud
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(100, 100, 150, 200))
            p.drawEllipse(QPointF(icon_x - 5, icon_y - 5), 10, 8)
            p.drawEllipse(QPointF(icon_x + 5, icon_y - 5), 10, 8)
            # Rain drops
            p.setPen(QColor(150, 200, 255, 200))
            for i in range(3):
                drop_phase = (phase * 3 + i * 0.3) % 1.0
                drop_y = icon_y + 5 + drop_phase * 15
                p.drawLine(icon_x - 5 + i * 5, drop_y, icon_x - 5 + i * 5, drop_y + 4)

        # 2. Draw Temp
        p.setFont(font_temp)
        p.setPen(QColor(255, 255, 255, 230))
        p.drawText(start_x + 65, start_y + 40, temp_str)
        
        # 3. Draw City
        p.setFont(font_city)
        p.setPen(QColor(200, 220, 255, 180))
        p.drawText(start_x + 65, start_y + 60, city_text)
