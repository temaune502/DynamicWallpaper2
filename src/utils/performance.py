import ctypes
from PySide6.QtCore import QObject, QTimer, Signal
from src.utils.win_utils import is_occluded

class VisibilityChecker(QObject):
    def __init__(self, check_interval=800):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check)
        self.interval = check_interval
        self.win_id = 0
        self.on_visible = None
        self.on_occluded = None
        self.is_paused = False

    def start(self, win_id, on_visible, on_occluded):
        self.win_id = int(win_id)
        self.on_visible = on_visible
        self.on_occluded = on_occluded
        self.timer.start(self.interval)

    def _check(self):
        if not self.win_id: return
        occluded = is_occluded(self.win_id, use_work_area=True, tolerance=4)
        if occluded and not self.is_paused:
            print("Desktop occluded: pause animation")
            if self.on_occluded: self.on_occluded()
            self.is_paused = True
        elif not occluded and self.is_paused:
            print("Desktop visible: resume animation")
            if self.on_visible: self.on_visible()
            self.is_paused = False

class FPSCounter:
    def __init__(self):
        self.frame_count = 0
        self.last_print_ms = 0
    
    def tick(self) -> int:
        """Returns fps if second elapsed, else -1"""
        self.frame_count += 1
        now_ms = ctypes.windll.kernel32.GetTickCount64()
        if self.last_print_ms == 0:
            self.last_print_ms = now_ms
            return -1
        elif now_ms - self.last_print_ms >= 1000:
            fps = self.frame_count
            self.frame_count = 0
            self.last_print_ms = now_ms
            return fps
        return -1
