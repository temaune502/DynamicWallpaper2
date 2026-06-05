from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPainter
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from src.effects.base import EffectRegistry
from src.widgets.base import WidgetRegistry
from src.core.backgrounds import BackgroundManager
from src.core.audio import AudioCapture
from src.core.preset_handler import load_preset
from src.utils.performance import VisibilityChecker, FPSCounter

class DynamicWallpaper(QOpenGLWidget):
    fps_update_signal = Signal(int)

    def __init__(self, config=None):
        super().__init__()
        self.config = config or {"effect": "glitch", "widgets": [], "fps": 22}
        
        self.effect_registry = EffectRegistry()
        self.widget_registry = WidgetRegistry()
        self.bg_manager = BackgroundManager(self.config.get("background"))
        
        self.playlist = self.config.get("effects_playlist", [])
        self.playlist_interval = self.config.get("playlist_interval", 30000)
        self.current_playlist_idx = 0
        
        self.current_effect = self.effect_registry.get_effect(self.config.get("effect", "glitch"))
        self.next_effect = None
        self.transition_alpha = 0.0
        self.is_transitioning = False
        
        self.active_widgets = []
        for i, w_conf in enumerate(self.config.get("widgets", [])):
            if widget := self.widget_registry.create_widget(w_conf.get("type"), w_conf):
                widget.id = w_conf.get('id', f"widget_{i}")
                self.active_widgets.append(widget)

        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.Tool | Qt.BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.resize(QApplication.primaryScreen().size())

        self.phase = 0.0
        self.fps = self.config.get("fps", 22)
        self.frame_interval = int(1000 / self.fps)
        
        self.fps_counter = FPSCounter()
        self.vis_checker = VisibilityChecker()

        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(self._tick)
        self.timer.start(self.frame_interval)
        
        self.vis_checker.start(self.winId(), self.timer.start, self.timer.stop)

        if self.playlist:
            self.p_timer = QTimer(self)
            self.p_timer.timeout.connect(self.next_playlist_effect)
            self.p_timer.start(self.playlist_interval)

        self.audio = AudioCapture()
        self.audio.data_signal.connect(self._on_audio)
        self.audio.start()
        self.last_audio = {'bass': 0, 'mid': 0, 'treble': 0}

    def switch_effect(self, name):
        if new_eff := self.effect_registry.get_effect(name):
            if self.is_transitioning and self.next_effect:
                self.current_effect = self.next_effect
            self.next_effect = new_eff
            self.is_transitioning = True
            self.transition_alpha = 0.0
            if hasattr(self.current_effect, 'show_background'):
                 self.next_effect.set_show_background(self.current_effect.show_background)

    def set_show_background(self, show):
        if self.current_effect: self.current_effect.set_show_background(show)
        if self.next_effect: self.next_effect.set_show_background(show)

    def set_background_source(self, conf):
        if self.bg_manager: self.bg_manager.cleanup()
        self.bg_manager = BackgroundManager(conf)
        self.config['background'] = conf

    def set_target_fps(self, fps):
        self.fps, self.config['fps'] = int(fps), int(fps)
        self.frame_interval = int(1000 / self.fps)
        if hasattr(self, 'timer'): self.timer.setInterval(self.frame_interval)

    def add_local_widget(self, conf):
        if w := self.widget_registry.create_widget(conf.get("type"), conf):
            self.active_widgets.append(w)
            self.config.setdefault('widgets', []).append(conf)

    def remove_local_widget(self, idx):
        if 0 <= idx < len(self.active_widgets):
            w = self.active_widgets.pop(idx)
            if hasattr(w, 'cleanup'): w.cleanup()
            if 0 <= idx < len(self.config.get('widgets', [])): self.config['widgets'].pop(idx)

    def update_local_widget(self, idx, conf):
        if 0 <= idx < len(self.active_widgets):
            self.active_widgets[idx].config.update(conf)
            for k in ['x', 'y', 'anchor']:
                if k in conf: setattr(self.active_widgets[idx], k, conf[k])
            if 0 <= idx < len(self.config.get('widgets', [])):
                self.config['widgets'][idx].update(conf)

    def load_preset(self, name): load_preset(self, name)

    def next_playlist_effect(self):
        if not self.playlist or self.is_transitioning: return
        self.current_playlist_idx = (self.current_playlist_idx + 1) % len(self.playlist)
        item = self.playlist[self.current_playlist_idx]
        name = item if isinstance(item, str) else item.get("effect", "none")
        conf = item.get("config", {}) if isinstance(item, dict) else {}
        
        self.next_effect = self.effect_registry.get_effect(name)
        if conf and self.next_effect: self.next_effect.configure(conf)
        if self.next_effect != self.current_effect:
            self.is_transitioning, self.transition_alpha = True, 0.0

    def closeEvent(self, e):
        if self.audio: self.audio.stop()
        for w in self.active_widgets: 
            if hasattr(w, 'cleanup'): w.cleanup()
        if self.bg_manager: self.bg_manager.cleanup()
        super().closeEvent(e)

    def _tick(self):
        self.phase = (self.phase + 0.0035) % 1.0
        if self.is_transitioning:
            self.transition_alpha += 0.015
            if self.transition_alpha >= 1.0:
                self.transition_alpha, self.current_effect, self.next_effect, self.is_transitioning = 1.0, self.next_effect, None, False
        self.update()
        if (fps := self.fps_counter.tick()) != -1: self.fps_update_signal.emit(fps)

    def paintGL(self):
        p = QPainter(self)
        try:
            p.setRenderHint(QPainter.Antialiasing, True)
            w, h = self.width(), self.height()
            self.bg_manager.draw(p, w, h)

            audio = self.last_audio
            if self.current_effect:
                self.current_effect.audio_data = audio
                if self.is_transitioning and self.next_effect:
                    p.setOpacity(1.0 - self.transition_alpha)
                    self.current_effect.draw(p, w, h, self.phase)
                    p.setOpacity(self.transition_alpha)
                    self.next_effect.audio_data = audio
                    self.next_effect.draw(p, w, h, self.phase)
                    p.setOpacity(1.0)
                else:
                    self.current_effect.draw(p, w, h, self.phase)
            for wid in self.active_widgets: wid.draw(p, w, h, self.phase)
        finally: p.end()

    def _on_audio(self, b, m, t): self.last_audio = {'bass': b, 'mid': m, 'treble': t}
