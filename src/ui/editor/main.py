import sys
import json
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                               QMessageBox, QSplitter)
from PySide6.QtCore import Qt

from src.core.resources import get_resource_path
from src.ui.editor.canvas import CanvasManager
from src.ui.editor.sidebar import SidebarManager
from src.ui.editor.preset_mgr import PresetManager
from src.ui.styles import DARK_THEME

class ConfigEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic Wallpaper Config Editor")
        self.resize(1280, 720)
        self.setStyleSheet(DARK_THEME)
        
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QHBoxLayout(self.central)
        
        self.preset_mgr = PresetManager()
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Sidebar
        self.sidebar = SidebarManager(self.preset_mgr)
        splitter.addWidget(self.sidebar)
        
        # Canvas Container
        canvas_container = QWidget()
        canvas_layout = QHBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(0,0,0,0)
        self.canvas = CanvasManager(canvas_layout)
        splitter.addWidget(canvas_container)
        
        splitter.setSizes([300, 980])
        self.layout.addWidget(splitter)
        
        # Connect signals
        self.sidebar.preset_load_signal.connect(self.load_preset)
        self.sidebar.preset_save_signal.connect(self.save_preset)
        self.sidebar.preset_new_signal.connect(self.new_preset)
        
        self.sidebar.effect_changed_signal.connect(self.update_live_effect)
        self.sidebar.playlist_changed_signal.connect(self.update_playlist)
        self.sidebar.bg_changed_signal.connect(self.update_live_bg)
        self.sidebar.add_widget_signal.connect(self.add_widget)
        self.sidebar.widget_updated_signal.connect(self.update_widget)
        
        self.canvas.widget_selected.connect(self.sidebar.on_widget_selected)
        
        self.current_config = {}
        self.current_preset_name = ""
        self.is_bundle = False
        
        # Initial load
        self.load_preset("main")

    def new_preset(self):
        self.current_config = {
            "effect": "none",
            "background": {"type": "none"},
            "effects_playlist": [],
            "widgets": []
        }
        self.current_preset_name = "new_preset"
        self.is_bundle = False
        self.sidebar.set_state(self.current_config)
        self.canvas.update_config(self.current_config)
        self.canvas.set_widgets([])
        print("New preset created")
        
    def update_playlist(self, items, interval):
        self.current_config["effects_playlist"] = items
        self.current_config["playlist_interval"] = interval

    def update_widget(self, widget_data):
        # Trigger redraw of widget
        # Since widget_data is a reference to the dict in current_config, 
        # changes are already there. We just need to tell canvas to refresh.
        self.canvas.scene.update()

    def load_preset(self, name):
        data, path, is_bundle = self.preset_mgr.load_preset(name)
        if data:
            self.current_config = data
            self.current_preset_name = name
            self.is_bundle = is_bundle
            
            self.sidebar.set_state(self.current_config)
            self.canvas.update_config(self.current_config)
            self.canvas.set_widgets(self.current_config.get("widgets", []))
            print(f"Loaded {name} (Bundle: {is_bundle})")
        else:
             QMessageBox.critical(self, "Error", f"Failed to load preset: {name}")

    def save_preset(self):
        self.preset_mgr.save_preset(self.current_preset_name, self.current_config, self.is_bundle)
        QMessageBox.information(self, "Saved", f"Preset {self.current_preset_name} saved.")

    def update_live_effect(self, effect, config):
        self.current_config["effect"] = effect
        self.current_config["effect_config"] = config
        self.canvas.engine.set_config(self.current_config)

    def update_live_bg(self, bg_config):
        self.current_config["background"] = bg_config
        self.canvas.engine.set_config(self.current_config)

    def add_widget(self, widget_type):
        new_widget_config = {
            "type": widget_type,
            "x": 100, "y": 100,
            "anchor": "top-left",
            "id": f"widget_{len(self.current_config.get('widgets', []))}"
        }
        if "widgets" not in self.current_config:
            self.current_config["widgets"] = []
            
        self.current_config["widgets"].append(new_widget_config)
        self.canvas.add_widget(new_widget_config)

