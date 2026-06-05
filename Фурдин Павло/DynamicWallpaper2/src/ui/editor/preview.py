from PySide6.QtCore import QObject, QTimer, Qt
from src.effects.base import EffectRegistry
from src.core.backgrounds import BackgroundManager
# from src.core.audio import AudioCapture # Optional for preview

class PreviewEngine(QObject):
    def __init__(self):
        super().__init__()
        self.effect_registry = EffectRegistry()
        self.bg_manager = BackgroundManager({"type": "none"})
        self.current_effect = None
        self.phase = 0.0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
        self.fps = 30
        self.timer.setInterval(1000 // self.fps)
        
        self.on_update = None # Callback to trigger repaint

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def set_config(self, config):
        # FPS
        self.fps = config.get("fps", 30)
        self.timer.setInterval(1000 // self.fps)
        
        # Background
        bg_conf = config.get("background", {})
        if self.bg_manager: self.bg_manager.cleanup()
        self.bg_manager = BackgroundManager(bg_conf)
        
        # Effect
        eff_name = config.get("effect", "none")
        eff_conf = config.get("effect_config", {})
        
        self.current_effect = self.effect_registry.get_effect(eff_name)
        if self.current_effect:
            self.current_effect.configure(eff_conf)
            self.current_effect.set_show_background(config.get("show_background", True))

    def update_effect_params(self, params):
        if self.current_effect:
            self.current_effect.configure(params)

    def _tick(self):
        self.phase = (self.phase + 0.005) % 1.0
        if self.on_update:
            self.on_update()

    def draw(self, p, w, h):
        # Draw Background
        if self.bg_manager:
            self.bg_manager.draw(p, w, h)
            
        # Draw Effect
        if self.current_effect:
            # We can mock audio data here or leave it empty
            self.current_effect.audio_data = {'bass': 0.5, 'mid': 0.5, 'treble': 0.5} 
            self.current_effect.draw(p, w, h, self.phase)
