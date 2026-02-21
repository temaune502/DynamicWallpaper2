import ctypes
from PySide6.QtCore import QAbstractNativeEventFilter

class HotkeyFilter(QAbstractNativeEventFilter):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        
    def nativeEventFilter(self, eventType, message):
        if eventType == b"windows_generic_MSG":
            msg = ctypes.wintypes.MSG.from_address(int(message))
            if msg.message == 0x0312: # WM_HOTKEY
                if msg.wParam == 1: # Our Hotkey ID
                    self.callback()
                    return False, 0
        return False, 0
