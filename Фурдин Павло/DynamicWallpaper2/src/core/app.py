import sys
import ctypes
import json
import os

from PySide6.QtWidgets import QApplication

from src.core.resources import get_resource_path
from src.utils.win_utils import attach_to_workerw
from src.ui.settings import SettingsWindow
from src.core.wallpaper import DynamicWallpaper
from src.utils.hotkeys import HotkeyFilter

def run():
    config = None
    if len(sys.argv) > 1 and sys.argv[1] == "--config":
        if len(sys.argv) > 2 and os.path.exists(sys.argv[2]):
            try:
                with open(sys.argv[2], 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")

    # Load default if none
    if config is None:
        default_preset = get_resource_path(os.path.join('presets', 'main.json'))
        if os.path.exists(default_preset):
            try:
                with open(default_preset, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except: pass

    # GPU Shims
    os.environ["SHIM_MCCOMPAT"] = "0x800000001" 
    os.environ["QT_OPENGL"] = "desktop"

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    wall = DynamicWallpaper(config=config)
    wall.show()

    settings_win = SettingsWindow()
    settings_win.resize_ui()
    
    def toggle_settings():
        if settings_win.isVisible():
            if settings_win.isActiveWindow():
                settings_win.hide()
            else:
                settings_win.activateWindow()
                settings_win.raise_()
        else:
            settings_win.show()
            settings_win.activateWindow()
            settings_win.raise_()
            settings_win.set_current_state(
                "none", 
                wall.current_effect.show_background if wall.current_effect else True
            )
            settings_win.set_fps(wall.fps)

    user32 = ctypes.windll.user32
    if user32.RegisterHotKey(None, 1, 0x0002, 0x33): 
        print("Hotkey Ctrl+3 registered!")
        hotkey_filter = HotkeyFilter(toggle_settings)
        app.installNativeEventFilter(hotkey_filter)
    
    settings_win.change_effect_signal.connect(wall.switch_effect)
    settings_win.load_preset_signal.connect(wall.load_preset)
    settings_win.toggle_background_signal.connect(wall.set_show_background)
    settings_win.set_background_signal.connect(wall.set_background_source)
    settings_win.set_fps_signal.connect(wall.set_target_fps)
    wall.fps_update_signal.connect(settings_win.update_fps)

    settings_win.add_widget_signal.connect(wall.add_local_widget)
    settings_win.remove_widget_signal.connect(wall.remove_local_widget)
    settings_win.update_widget_signal.connect(wall.update_local_widget)
    
    def sync_settings_widgets():
        widget_configs = [w.config for w in wall.active_widgets]
        settings_win.set_widgets_list(widget_configs)
        
    settings_win.request_refresh_signal.connect(sync_settings_widgets)
    
    original_add = wall.add_local_widget
    def add_wrapper(config):
        original_add(config)
        sync_settings_widgets()
        
    original_remove = wall.remove_local_widget
    def remove_wrapper(index):
        original_remove(index)
        sync_settings_widgets()
        
    settings_win.add_widget_signal.disconnect()
    settings_win.remove_widget_signal.disconnect()
    settings_win.add_widget_signal.connect(add_wrapper)
    settings_win.remove_widget_signal.connect(remove_wrapper)
    
    original_toggle = toggle_settings
    def new_toggle():
        original_toggle()
        if settings_win.isVisible():
            sync_settings_widgets()
            
    app.removeNativeEventFilter(hotkey_filter)
    hotkey_filter = HotkeyFilter(new_toggle)
    app.installNativeEventFilter(hotkey_filter)

    attached = attach_to_workerw(int(wall.winId()))
    if not attached:
        print("[WARN] Failed to attach to WorkerW")

    sys.exit(app.exec())
