import os
import hashlib
from PySide6.QtCore import Qt, QSize, QUrl, Signal, QObject, QRect
from PySide6.QtGui import QImage, QPixmap, QMovie, QPainter
from PySide6.QtMultimedia import QMediaPlayer, QVideoSink, QAudioOutput

class BackgroundManager(QObject):
    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        self.bg_type = self.config.get("type", "none")  # none, image, gif, video
        self.path = self.config.get("path", "")
        
        self.image = None
        self.movie = None
        self.player = None
        self.video_sink = None
        self.audio_output = None
        self.current_frame = None
        self._processing_frame = False
        
        self.cache_dir = "cache"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        self._init_background()

    def cleanup(self):
        """Очистка ресурсів перед видаленням менеджера"""
        if self.player:
            self.player.stop()
            self.player.setVideoSink(None)
            self.player.deleteLater()
        if self.movie:
            self.movie.stop()
        self.current_frame = None
        self.image = None

    def _init_background(self):
        from src.core.resources import resolve_path
        
        if not self.path:
            self.bg_type = "none"
            return
            
        # Resolve path (Bundle -> Absolute -> Relative)
        resolved_path = resolve_path(self.path)
        
        if not os.path.exists(resolved_path):
            print(f"BackgroundManager: File not found: {resolved_path} (Raw: {self.path})")
            self.bg_type = "none"
            return
            
        self.path = resolved_path
        print(f"BackgroundManager: Initializing {self.bg_type}: {self.path}")
        
        if self.bg_type == "image":
            # Image will be loaded and cached on first resize in draw()
            pass
        elif self.bg_type == "gif":
            self.movie = QMovie(self.path)
            self.movie.setCacheMode(QMovie.CacheAll)
            self.movie.start()
        elif self.bg_type == "video":
            self.player = QMediaPlayer()
            self.video_sink = QVideoSink()
            self.player.setVideoSink(self.video_sink)
            
            # Disable audio
            self.audio_output = QAudioOutput()
            self.audio_output.setMuted(True)
            self.player.setAudioOutput(self.audio_output)
            
            self.player.setSource(QUrl.fromLocalFile(os.path.abspath(self.path)))
            self.player.setLoops(QMediaPlayer.Infinite)
            self.video_sink.videoFrameChanged.connect(self._on_video_frame)
            self.player.play()

    def _on_video_frame(self, frame):
        self.current_frame = frame.toImage()

    def get_cached_image(self, w, h):
        if not self.path:
            return None
            
        # Create a unique key for the cache based on path and size
        file_hash = hashlib.md5(self.path.encode()).hexdigest()
        cache_file = os.path.join(self.cache_dir, f"{file_hash}_{w}x{h}.png")
        
        if os.path.exists(cache_file):
            return QImage(cache_file)
        
        # If not cached, load original and scale
        original = QImage(self.path)
        if original.isNull():
            return None
            
        scaled = original.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        scaled.save(cache_file, "PNG")
        return scaled

    def _on_video_frame(self, frame):
        if self.bg_type == "video":
            # Обмежуємо обробку кадрів (наприклад, не більше 30 FPS)
            # або просто пропускаємо кадр, якщо попередній ще не відображено.
            if hasattr(self, '_frame_ready') and self._frame_ready:
                return
                
            if hasattr(self, '_processing_frame') and self._processing_frame:
                return
                
            self._processing_frame = True
            try:
                # ВАЖЛИВО: Використовуємо спрощений метод отримання зображення.
                # Якщо кадр вже в пам'яті GPU, toImage() викличе затримку.
                img = frame.toImage()
                if not img.isNull():
                    # Якщо відео FHD або вище, а вікно менше, 
                    # масштабування до розумних меж (720p) значно економить RAM.
                    if img.width() > 1280:
                        img = img.scaled(1280, 720, Qt.KeepAspectRatio, Qt.FastTransformation)
                    
                    self.current_frame = img
                    self._frame_ready = True # Кадр готовий до малювання
            finally:
                self._processing_frame = False

    def draw(self, p: QPainter, w: int, h: int):
        p.setCompositionMode(QPainter.CompositionMode_Source)
        target_rect = QRect(0, 0, w, h)
        
        if self.bg_type == "image":
            if self.image is None or self.image.width() != w or self.image.height() != h:
                self.image = self.get_cached_image(w, h)
            if self.image:
                p.drawImage(target_rect, self.image)
                
        elif self.bg_type == "gif":
            if self.movie:
                frame = self.movie.currentImage()
                if not frame.isNull():
                    p.drawImage(target_rect, frame)
                    
        elif self.bg_type == "video":
            if self.current_frame:
                p.drawImage(target_rect, self.current_frame)
                # Mark as drawn, ready for next
                self._frame_ready = False
        
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)
