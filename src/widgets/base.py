import os
import sys
import time
import importlib.util
import inspect
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPainter, QColor, QFont

from src.core.resources import get_resource_path

# Add root and widgets dir to sys.path
root_dir = get_resource_path("")
widgets_dir = get_resource_path("widgets")
for d in [root_dir, widgets_dir]:
    if d not in sys.path:
        sys.path.append(d)

class BaseWidget:
    def __init__(self, config=None):
        self.config = config or {}
        self.x = self.config.get('x', 30)
        self.y = self.config.get('y', 30)
        self.anchor = self.config.get('anchor', 'top-left')

    def get_pos(self, w, h, tw, th):
        px, py = self.x, self.y
        if self.anchor == 'top-right':
            px = w - tw - self.x
        elif self.anchor == 'bottom-left':
            py = h - th - self.y
        elif self.anchor == 'bottom-right':
            px = w - tw - self.x
            py = h - th - self.y
        elif self.anchor == 'center':
            px = w // 2 - tw // 2 + self.x
            py = h // 2 - th // 2 + self.y
        return px, py

    def draw(self, p: QPainter, w: int, h: int, phase: float = 0.0):
        pass

    def cleanup(self):
        """ Очищення ресурсів перед видаленням віджета """
        pass

class PluginWidgetWrapper:
    """ Обертка для динамічного завантаження віджетів """
    def __init__(self, file_path, class_name, config=None):
        self.file_path = file_path
        self.class_name = class_name
        self.config = config or {}
        self.instance = None
        self.last_mtime = 0
        self.last_check_time = 0
        self._reload_if_needed()

    def _reload_if_needed(self):
        now = time.time()
        if now - self.last_check_time < 2.0:
            return
        self.last_check_time = now

        try:
            mtime = os.path.getmtime(self.file_path)
            if mtime > self.last_mtime:
                mod_name = f"widget_plugin_{os.path.basename(self.file_path)}"
                if mod_name in sys.modules:
                    del sys.modules[mod_name]
                
                spec = importlib.util.spec_from_file_location(mod_name, self.file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                cls = getattr(module, self.class_name)
                self.instance = cls(self.config)
                self.last_mtime = mtime
                print(f"Widget {self.class_name} reloaded")
        except Exception as e:
            if self.instance is None:
                print(f"Error loading widget plugin {self.file_path}: {e}")

    @property
    def x(self):
        # Prefer instance value if available, else config
        if self.instance: return self.instance.x
        return self.config.get('x', 0)

    @x.setter
    def x(self, value):
        self.config['x'] = value
        if self.instance: self.instance.x = value

    @property
    def y(self):
        if self.instance: return self.instance.y
        return self.config.get('y', 0)

    @y.setter
    def y(self, value):
        self.config['y'] = value
        if self.instance: self.instance.y = value

    @property
    def anchor(self):
        if self.instance: return self.instance.anchor
        return self.config.get('anchor', 'top-left')

    @anchor.setter
    def anchor(self, value):
        self.config['anchor'] = value
        if self.instance: self.instance.anchor = value

    def draw(self, p, w, h, phase):
        self._reload_if_needed()
        if not self.instance: return

        # Check update interval (ms)
        interval = self.config.get('update_interval', 0)
        
        if interval <= 0:
            # Draw directly if caching disabled (dynamic widgets)
            try:
                self.instance.draw(p, w, h, phase)
            except Exception as e:
                print(f"Error drawing widget {self.class_name}: {e}")
            return

        # Caching Logic
        import time
        now = time.time()
        
        # Invalidate cache if size changed
        if not hasattr(self, '_cache_pixmap') or self._cache_pixmap.width() != w or self._cache_pixmap.height() != h:
            self._cache_pixmap = None

        # Check if update is needed
        if (not getattr(self, '_cache_pixmap', None) or 
            (now - getattr(self, '_last_cache_update', 0)) * 1000 > interval):
            
            # Create/Update Cache
            from PySide6.QtGui import QPixmap, QPainter
            self._cache_pixmap = QPixmap(w, h)
            self._cache_pixmap.fill(Qt.transparent)
            
            cache_painter = QPainter(self._cache_pixmap)
            # Transfer render hints
            cache_painter.setRenderHints(p.renderHints())
            
            try:
                self.instance.draw(cache_painter, w, h, phase)
            except Exception as e:
                print(f"Error caching widget {self.class_name}: {e}")
            finally:
                cache_painter.end()
                
            self._last_cache_update = now

        # Draw Cached Pixmap
        if self._cache_pixmap:
            p.drawPixmap(0, 0, self._cache_pixmap)

    def cleanup(self):
        if hasattr(self, '_cache_pixmap'):
            del self._cache_pixmap
        if self.instance and hasattr(self.instance, 'cleanup'):
            try:
                self.instance.cleanup()
            except Exception as e:
                print(f"Error cleaning up widget {self.class_name}: {e}")

class WidgetRegistry:
    def __init__(self):
        self.available_classes = {} # name -> (file_path, class_name)
        self._load_plugins()

    def _load_plugins(self):
        widgets_dir = get_resource_path("widgets")
        if not os.path.exists(widgets_dir):
            return

        for file in os.listdir(widgets_dir):
            if file.endswith(".py") and file != "__init__.py":
                file_path = os.path.join(widgets_dir, file)
                try:
                    # Використовуємо унікальне ім'я модуля для завантаження
                    mod_name = f"widgets.plugin_{file[:-3]}"
                    spec = importlib.util.spec_from_file_location(mod_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[mod_name] = module
                    spec.loader.exec_module(module)
                    
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, BaseWidget) and obj != BaseWidget:
                            widget_id = getattr(obj, 'WIDGET_NAME', name.lower().replace('widget', ''))
                            self.available_classes[widget_id] = (file_path, name)
                            print(f"Registered widget: {widget_id}")
                except Exception as e:
                    print(f"Error scanning widget {file}: {e}")

    def load_bundle_widgets(self, bundle_path):
        widgets_dir = os.path.join(bundle_path, "widgets")
        if not os.path.exists(widgets_dir): return

        print(f"Scanning bundle widgets in {widgets_dir}...")
        for file in os.listdir(widgets_dir):
            if file.endswith(".py"):
                file_path = os.path.join(widgets_dir, file)
                try:
                    mod_name = f"bundle_widget_{os.path.basename(bundle_path)}_{file[:-3]}"
                    spec = importlib.util.spec_from_file_location(mod_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[mod_name] = module
                    spec.loader.exec_module(module)
                    
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, BaseWidget) and obj != BaseWidget:
                            widget_id = getattr(obj, 'WIDGET_NAME', name)
                            self.available_classes[widget_id] = (file_path, name)
                            print(f"Registered bundle widget: {widget_id}")
                except Exception as e:
                    print(f"Error loading bundle widget {file}: {e}")

    def create_widget(self, name, config=None):
        if name in self.available_classes:
            file_path, class_name = self.available_classes[name]
            return PluginWidgetWrapper(file_path, class_name, config)
        return None
