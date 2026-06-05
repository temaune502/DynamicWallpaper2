import time
import numpy as np
import pyaudio
from PySide6.QtCore import QThread, Signal, QObject

class AudioCapture(QThread):
    # Sends (bass, mid, treble) normalized 0.0-1.0
    data_signal = Signal(float, float, float)

    def __init__(self):
        super().__init__()
        self.running = True
        self.pa = None
        self.stream = None
        self.chunk_size = 1024
        self.rate = 44100
        
    def run(self):
        try:
            self.pa = pyaudio.PyAudio()
            
            # Find default input device
            # For loopback (hearing what computer plays), we usually need a specific setup (WASAPI loopback)
            # helping user finding a working input is hard automatically.
            # We'll try default input first (microphone).
            # To get system output, Windows WASAPI loopback is needed.
            
            # Try to find a loopback device if possible, or just default
            device_index = None
            
            # Simple default implementation
            try:
                info = self.pa.get_default_input_device_info()
                device_index = info['index']
            except OSError:
                print("No default input device found. Audio reactivity disabled.")
                return

            self.stream = self.pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size
            )
            
            print(f"Audio Capture started on device: {device_index}")

            while self.running:
                try:
                    data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                    # Convert to numpy array
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    
                    # FFT
                    fft_data = np.fft.rfft(audio_data)
                    fft_mag = np.abs(fft_data)
                    
                    # Normalize (log scale is often better for audio)
                    # chunk=1024 -> rfft=513 bins. 0-22050Hz
                    # Bass: 20-250Hz -> bins 1-12
                    # Mid: 250-4000Hz -> bins 12-185
                    # Treble: 4000-20000Hz -> bins 185-512
                    
                    # Scaling factor (empirical)
                    scale = 100000.0 
                    
                    bass = np.mean(fft_mag[1:12]) / scale
                    mid = np.mean(fft_mag[12:185]) / scale
                    treble = np.mean(fft_mag[185:]) / scale
                    
                    # Clip to 0-1 (soft)
                    bass = min(1.0, bass * 2.0)
                    mid = min(1.0, mid * 3.0)
                    treble = min(1.0, treble * 5.0)
                    
                    self.data_signal.emit(bass, mid, treble)
                    
                except Exception as e:
                    print(f"Audio read error: {e}")
                    time.sleep(0.1)

        except Exception as e:
            print(f"Audio Capture Init Error: {e}")
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.pa:
                self.pa.terminate()

    def stop(self):
        self.running = False
        self.wait()
