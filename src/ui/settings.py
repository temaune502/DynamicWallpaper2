from PySide6.QtWidgets import QDialog, QVBoxLayout, QTabWidget
from PySide6.QtCore import Signal
from src.ui.settings_panels.general import GeneralSettingsTab
from src.ui.settings_panels.widgets import WidgetsSettingsTab
from src.ui.styles import DARK_THEME

class SettingsWindow(QDialog):
    change_effect_signal = Signal(str)
    load_preset_signal = Signal(str)
    toggle_background_signal = Signal(bool)
    set_background_signal = Signal(dict)
    set_fps_signal = Signal(int)

    add_widget_signal = Signal(dict)
    remove_widget_signal = Signal(int)
    update_widget_signal = Signal(int, dict)
    request_refresh_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wallpaper Settings")
        self.resize(400, 600)
        self.setStyleSheet(DARK_THEME)
        
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        self.general_tab = GeneralSettingsTab()
        self.widgets_tab = WidgetsSettingsTab()
        
        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.widgets_tab, "Widgets")
        
        self.layout.addWidget(self.tabs)

        # Connect General Tab Signals
        self.general_tab.change_effect_signal.connect(self.change_effect_signal.emit)
        self.general_tab.load_preset_signal.connect(self.load_preset_signal.emit)
        self.general_tab.toggle_background_signal.connect(self.toggle_background_signal.emit)
        self.general_tab.set_background_signal.connect(self.set_background_signal.emit)
        self.general_tab.set_fps_signal.connect(self.set_fps_signal.emit)

        # Connect Widgets Tab Signals
        self.widgets_tab.add_widget_signal.connect(self.add_widget_signal.emit)
        self.widgets_tab.remove_widget_signal.connect(self.remove_widget_signal.emit)
        self.widgets_tab.update_widget_signal.connect(self.update_widget_signal.emit)
        self.widgets_tab.request_refresh_signal.connect(self.request_refresh_signal.emit)

    def resize_ui(self):
        self.resize(450, 650)
    
    def set_current_state(self, effect_name, show_bg):
        self.general_tab.set_current_state(effect_name, show_bg)

    def set_fps(self, fps):
        self.general_tab.set_fps(fps)

    def update_fps(self, fps):
        # We can update the label in general tab if we want to show real-time FPS
        # For now, just ignoring or maybe updating title?
        self.setWindowTitle(f"Settings (FPS: {fps})")

    def set_widgets_list(self, widgets_data):
        self.widgets_tab.set_widgets_list(widgets_data)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
