from PySide6.QtCore import Qt, QRectF, QThread, Signal
from PySide6.QtGui import QPainter, QColor, QLinearGradient
import math
import numpy as np
try:
    import soundcard as sc
    HAS_SOUNDCARD = True
except ImportError:
    HAS_SOUNDCARD = False

from widgets import BaseWidget

import warnings

# Ігноруємо попередження про розриви даних, оскільки для візуалізації це не критично
# і дозволяє уникнути засмічення консолі та мікро-затримок
warnings.filterwarnings("ignore", category=UserWarning, module="soundcard")

import queue

class AudioCaptureThread(QThread):
    data_ready = Signal(np.ndarray)

    def __init__(self, num_bars=20, gain=1.0):
        super().__init__()
        self.num_bars = num_bars
        self.gain = gain
        self.running = True
        self.sample_rate = 44100 / 2 
        self.chunk_size = 2048 # Збільшуємо для стабільності
        self.freq_weights = np.linspace(0.8, 2.5, num_bars) # Зменшили ваги
        self.audio_queue = queue.Queue(maxsize=20)
        
        # Для автоматичного регулювання підсилення
        self.max_history = []
        # Початкове значення gain має бути невеликим, щоб не було стрибка на старті
        self._auto_gain = 0.1 
        self._startup_frames = 0

    def run(self):
        if not HAS_SOUNDCARD:
            return

        def process_fft():
            while self.running:
                try:
                    data = self.audio_queue.get(timeout=0.1)
                    
                    # FFT
                    window = np.hanning(len(data))
                    fft_data = np.abs(np.fft.rfft(data * window))
                    
                    # Більш вузький діапазон (до 15кГц) для чистоти
                    max_idx = int(len(fft_data) * 0.7)
                    fft_data = fft_data[:max_idx]
                    
                    if len(fft_data) > self.num_bars:
                        if not hasattr(self, '_cached_indices'):
                            self._cached_indices = np.logspace(0, np.log10(len(fft_data)-1), self.num_bars + 1).astype(int)
                        
                        idx = self._cached_indices
                        bars = []
                        for i in range(self.num_bars):
                            val = np.max(fft_data[idx[i]:idx[i+1]+1])
                            bars.append(val * self.freq_weights[i])
                        
                        bars = np.array(bars)
                        
                        # АВТОМАТИЧНЕ ПІДСИЛЕННЯ (AGC)
                        current_max = np.max(bars)
                        if current_max > 0.0001:
                            self.max_history.append(current_max)
                            if len(self.max_history) > 60: self.max_history.pop(0)
                        
                        # Розраховуємо цільовий gain
                        avg_max = np.mean(self.max_history) if len(self.max_history) > 5 else 0.5
                        #print(f"avg_max: {avg_max}")
                        if avg_max < 0.001: avg_max = 0.001
                        
                        target_gain = 0.65 / avg_max
                        #print(f"target_gain: {target_gain}")
                        
                        # На старті адаптуємося швидше, потім плавно
                        if self._startup_frames < 100:
                            adaptation_speed = 0.2
                            self._startup_frames += 1
                        else:
                            adaptation_speed = 0.03
                            
                        self._auto_gain += (target_gain - self._auto_gain) * adaptation_speed
                        
                        # Застосовуємо gain та логарифмічну компресію
                        # Ваше ділення на 2.5 я інтегрував у базовий множник (80 / 2.5 = 32)
                        bars = bars * 32 * self.gain * self._auto_gain
                        
                        # Більш агресивна компресія
                        bars = np.log10(1 + bars) / 1.2
                        
                        # Експоненціальна крива
                        bars = np.power(bars, 1.4)
                        
                        self.data_ready.emit(np.clip(bars, 0, 1))
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"FFT processing error: {e}")

        import threading
        self.processing_thread = threading.Thread(target=process_fft, daemon=True)
        self.processing_thread.start()

        try:
            speaker = sc.default_speaker()
            mic = sc.get_microphone(id=str(speaker.name), include_loopback=True)
            
            # Використовуємо blocksize для MediaFoundation
            with mic.recorder(samplerate=self.sample_rate, blocksize=self.chunk_size) as recorder:
                while self.running:
                    # ТІЛЬКИ ЗЧИТУВАННЯ
                    data = recorder.record(numframes=self.chunk_size)
                    if data is not None and len(data) > 0:
                        # Беремо один канал без зайвих функцій numpy
                        mono = data[:, 0] if data.ndim > 1 else data
                        try:
                            self.audio_queue.put_nowait(mono)
                        except queue.Full:
                            # Очищуємо чергу, якщо вона переповнена (скидаємо старі кадри)
                            try:
                                self.audio_queue.get_nowait()
                                self.audio_queue.put_nowait(mono)
                            except: pass
        except Exception as e:
            print(f"Audio capture error: {e}")

    def stop(self):
        self.running = False
        self.wait() # Чекаємо завершення потоку

class AudioVisualizerWidget(BaseWidget):
    """
    Віджет візуалізатора аудіо.
    Реагує на реальне аудіо через loopback або використовує імітацію.
    """
    WIDGET_NAME = "audio_visualizer"
    
    def __init__(self, config=None):
        super().__init__(config)
        self.num_bars = self.config.get("bars", 20)
        self.color_top = QColor(self.config.get("color_top", "#00F2FE"))
        self.color_bottom = QColor(self.config.get("color_bottom", "#4FACFE"))
        self.gain = self.config.get("gain", 1.0)
        self.heights = [0.05] * self.num_bars
        self.smoothness_up = 0.6 # Швидко вгору
        self.smoothness_down = 0.15 # Повільно вниз
        self.use_real_audio = self.config.get("real_audio", True)
        
        self.capture_thread = None
        if self.use_real_audio and HAS_SOUNDCARD:
            self.capture_thread = AudioCaptureThread(self.num_bars, self.gain)
            self.capture_thread.data_ready.connect(self._on_data_ready)
            self.capture_thread.start()

    def _on_data_ready(self, data):
        for i in range(min(len(data), self.num_bars)):
            target = data[i]
            if target > self.heights[i]:
                # Різкий стрибок вгору
                self.heights[i] += (target - self.heights[i]) * self.smoothness_up
            else:
                # Плавне падіння
                self.heights[i] += (target - self.heights[i]) * self.smoothness_down

    def draw(self, p: QPainter, w: int, h: int, phase: float = 0.0):
        p.setRenderHint(QPainter.Antialiasing)
        
        total_w = self.config.get("width", 300)
        total_h = self.config.get("height", 100)
        start_x, start_y = self.get_pos(w, h, total_w, total_h)
        
        # Фон
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 0, 0, 40))
        p.drawRoundedRect(start_x, start_y, total_w, total_h, 8, 8)
        
        bar_gap = 4
        bar_w = (total_w - (self.num_bars + 1) * bar_gap) / self.num_bars
        
        # Симуляція, якщо немає реального аудіо
        if not self.capture_thread or not self.capture_thread.isRunning():
            for i in range(self.num_bars):
                target_h = (math.sin(phase * 8 + i * 0.4) * 0.2 + 
                           math.sin(phase * 4 - i * 0.7) * 0.1 + 0.3)
                self.heights[i] += (target_h - self.heights[i]) * 0.05

        # Малюємо бари
        for i in range(self.num_bars):
            val = self.heights[i]
            curr_bar_h = val * (total_h - 25)
            curr_bar_h = max(3, curr_bar_h)
            
            rect = QRectF(
                start_x + bar_gap + i * (bar_w + bar_gap),
                start_y + total_h - curr_bar_h - 10,
                bar_w,
                curr_bar_h
            )
            
            grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            grad.setColorAt(0, self.color_top)
            grad.setColorAt(1, self.color_bottom)
            
            # Glow ефект
            glow_color = QColor(self.color_top)
            glow_color.setAlpha(int(40 * val))
            p.setBrush(glow_color)
            p.drawRoundedRect(rect.adjusted(-2, -2, 2, 2), 2, 2)
            
            p.setBrush(grad)
            p.drawRoundedRect(rect, 2, 2)
            
            # Піковий індикатор
            peak_h = val * 1.1
            peak_y = start_y + total_h - peak_h * (total_h - 25) - 15
            peak_y = max(start_y + 5, peak_y)
            
            p.setBrush(self.color_top)
            p.drawRect(rect.x(), peak_y, bar_w, 1.5)

    def cleanup(self):
        """ Зупиняємо потік захоплення звуку """
        if self.capture_thread:
            self.capture_thread.stop()
            self.capture_thread = None

    def __del__(self):
        self.cleanup()
