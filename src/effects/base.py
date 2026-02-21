import math
import random
import os
import sys
import time
import importlib.util
import inspect
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import  QPainter, QColor, QLinearGradient, QBrush, QPen, QFont, QRadialGradient

from src.core.resources import get_resource_path

# Add root to sys.path so plugins can import properly if needed
root_dir = get_resource_path("")
if root_dir not in sys.path:
    sys.path.append(root_dir)

class BaseEffect:
    def __init__(self):
        self.cache = {}
        self.show_background = True
        self.audio_data = None # {'bass': 0.0, 'mid': 0.0, 'treble': 0.0}

    def set_show_background(self, show: bool):
        self.show_background = show

    def configure(self, config: dict):
        pass

    @classmethod
    def get_schema(cls):
        return {}

    def draw(self, p: QPainter, w: int, h: int, phase: float):
        pass

    def reset_cache(self):
        self.cache = {}

class PluginEffectWrapper(BaseEffect):
    """ Обертка для динамічного завантаження та Hot Reload ефектів """
    def __init__(self, file_path, class_name):
        super().__init__()
        self.file_path = file_path
        self.class_name = class_name
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
                # Видаляємо старий модуль з кешу, щоб імпортувати заново
                mod_name = f"plugin_{os.path.basename(self.file_path)}"
                if mod_name in sys.modules:
                    del sys.modules[mod_name]
                
                spec = importlib.util.spec_from_file_location(mod_name, self.file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                cls = getattr(module, self.class_name)
                new_instance = cls()
                # Зберігаємо налаштування тла
                new_instance.show_background = self.show_background
                self.instance = new_instance
                self.last_mtime = mtime
                print(f"Ефект {self.class_name} перезавантажено з {os.path.basename(self.file_path)}")
        except Exception as e:
            # Якщо вже є інстанс, продовжуємо використовувати його при помилці в новому коді
            if self.instance is None:
                print(f"Помилка завантаження плагіна {self.file_path}: {e}")

    def draw(self, p, w, h, phase):
        self._reload_if_needed()
        if self.instance:
            self.instance.show_background = self.show_background
            self.instance.audio_data = self.audio_data
            try:
                self.instance.draw(p, w, h, phase)
            except Exception as e:
                # Виводимо помилку в консоль, але не "палимо" всю програму
                print(f"Помилка виконання ефекту {self.class_name}: {e}")

    def configure(self, config: dict):
        self._reload_if_needed()
        if self.instance and hasattr(self.instance, 'configure'):
            try:
                self.instance.configure(config)
            except Exception as e:
                print(f"Error configuring effect {self.class_name}: {e}")

    def get_schema(self):
        # We need to reload to get the latest schema if it changed
        self._reload_if_needed()
        if self.instance:
            return self.instance.get_schema()
        # Fallback to class if instance not ready (though _reload should create it)
        # But wait, get_schema is usually @classmethod. 
        # On the wrapper, we might call it on the instance or the class.
        # Since PluginEffectWrapper is an instance acting like the effect, 
        # we can just call it on self.instance.
        return {}

class EffectRegistry:
    def __init__(self):
        self.effects = {}
        self._load_plugins()

    def _load_plugins(self):
        plugins_dir = get_resource_path("plugins")
        if not os.path.exists(plugins_dir):
            try:
                os.makedirs(plugins_dir)
            except: pass
            return

        print(f"Сканування плагінів у {plugins_dir}...")
        for file in os.listdir(plugins_dir):
            if file.endswith(".py"):
                file_path = os.path.join(plugins_dir, file)
                try:
                    # Тимчасово імпортуємо, щоб знайти класи
                    mod_name = f"scan_{file}"
                    spec = importlib.util.spec_from_file_location(mod_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, BaseEffect) and obj != BaseEffect:
                            # Шукаємо назву в EFFECT_NAME або генеруємо з імені класу
                            effect_id = getattr(obj, 'EFFECT_NAME', name.lower().replace('effect', ''))
                            self.effects[effect_id] = PluginEffectWrapper(file_path, name)
                            print(f"Зареєстровано ефект: {effect_id} (клас {name})")
                except Exception as e:
                    print(f"Не вдалося завантажити плагін {file}: {e}")

    def load_bundle_effects(self, bundle_path):
        effects_dir = os.path.join(bundle_path, "effects")
        if not os.path.exists(effects_dir): return

        print(f"Scanning bundle effects in {effects_dir}...")
        for file in os.listdir(effects_dir):
            if file.endswith(".py"):
                file_path = os.path.join(effects_dir, file)
                try:
                    # Dynamic load with unique name for bundle
                    mod_name = f"bundle_effect_{os.path.basename(bundle_path)}_{file[:-3]}"
                    spec = importlib.util.spec_from_file_location(mod_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[mod_name] = module
                    spec.loader.exec_module(module)
                    
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, BaseEffect) and obj != BaseEffect:
                            effect_id = getattr(obj, 'EFFECT_NAME', name)
                            # Register with a prefix or override? 
                            # Let's override to allow "custom version of glitch" etc.
                            # But better use unique ID if possible.
                            self.effects[effect_id] = PluginEffectWrapper(file_path, name)
                            print(f"Registered bundle effect: {effect_id}")
                except Exception as e:
                    print(f"Error loading bundle effect {file}: {e}")

    def get_effect(self, name):
        if name == "none":
            return BaseEffect() 
        return self.effects.get(name)

# Compatibility functions (if needed)
def draw_glitch(p, w, h, phase): 
    # This is now just a placeholder or could use registry
    pass
