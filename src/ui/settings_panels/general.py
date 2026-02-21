import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QPushButton, QGroupBox, QLineEdit, 
                               QSpinBox, QSlider, QFileDialog)
from PySide6.QtCore import Qt, Signal
from src.effects.base import EffectRegistry
from src.core.resources import get_resource_path

class GeneralSettingsTab(QWidget):
    change_effect_signal = Signal(str)
    load_preset_signal = Signal(str)
    toggle_background_signal = Signal(bool)
    set_background_signal = Signal(dict)
    set_fps_signal = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.preset_dir = get_resource_path("presets")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Effects Section
        eff_group = QGroupBox("Effects")
        eff_layout = QVBoxLayout()
        
        self.effect_combo = QComboBox()
        self.effect_registry = EffectRegistry()
        effects = sorted(list(self.effect_registry.effects.keys()))
        self.effect_combo.addItem("none")
        self.effect_combo.addItems(effects)
        self.effect_combo.currentTextChanged.connect(self._on_effect_changed)
        
        eff_layout.addWidget(QLabel("Select Active Effect:"))
        eff_layout.addWidget(self.effect_combo)
        eff_group.setLayout(eff_layout)
        layout.addWidget(eff_group)

        # Presets Section
        preset_group = QGroupBox("Presets")
        preset_layout = QVBoxLayout()
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("-- Select Preset --")
        self._load_presets()
        self.preset_combo.currentIndexChanged.connect(self._on_preset_selected)
        
        # Editor Button
        self.edit_btn = QPushButton("Open Preset Editor")
        self.edit_btn.clicked.connect(self._open_editor)
        
        preset_layout.addWidget(QLabel("Load Preset:"))
        preset_layout.addWidget(self.preset_combo)
        preset_layout.addWidget(self.edit_btn)
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)

        # Background Toggle
        self.bg_btn = QPushButton("Toggle Background")
        self.bg_btn.setCheckable(True)
        self.bg_btn.setChecked(True)
        self.bg_btn.clicked.connect(self._on_bg_toggled)
        layout.addWidget(self.bg_btn)

        # Background Source
        bg_source_group = QGroupBox("Background Source")
        bg_source_layout = QVBoxLayout()
        
        # Type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.bg_type_combo = QComboBox()
        self.bg_type_combo.addItems(["none", "image", "video", "gif"])
        self.bg_type_combo.currentTextChanged.connect(self._on_bg_type_changed)
        type_layout.addWidget(self.bg_type_combo)
        bg_source_layout.addLayout(type_layout)
        
        # Path
        path_layout = QHBoxLayout()
        self.bg_path_edit = QLineEdit()
        self.bg_path_edit.setPlaceholderText("Path to file...")
        self.bg_browse_btn = QPushButton("...")
        self.bg_browse_btn.setFixedWidth(30)
        self.bg_browse_btn.clicked.connect(self._on_browse_bg)
        path_layout.addWidget(self.bg_path_edit)
        path_layout.addWidget(self.bg_browse_btn)
        bg_source_layout.addLayout(path_layout)
        
        self.bg_apply_btn = QPushButton("Apply Background")
        self.bg_apply_btn.clicked.connect(self._on_apply_bg)
        bg_source_layout.addWidget(self.bg_apply_btn)
        
        bg_source_group.setLayout(bg_source_layout)
        layout.addWidget(bg_source_group)

        # Performance
        perf_group = QGroupBox("Performance")
        perf_layout = QVBoxLayout()
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("Target FPS:"))
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(5, 144)
        self.fps_spin.setValue(30)
        self.fps_spin.setFixedWidth(50)
        self.fps_slider = QSlider(Qt.Horizontal)
        self.fps_slider.setRange(5, 144)
        self.fps_slider.setValue(30)
        self.fps_spin.valueChanged.connect(self.fps_slider.setValue)
        self.fps_slider.valueChanged.connect(self.fps_spin.setValue)
        self.fps_slider.valueChanged.connect(self._on_fps_changed)
        fps_layout.addWidget(self.fps_slider)
        fps_layout.addWidget(self.fps_spin)
        perf_layout.addLayout(fps_layout)
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)

        layout.addStretch()

    def _open_editor(self):
        from src.ui.editor.main import ConfigEditor
        self.editor_window = ConfigEditor()
        self.editor_window.show()

    def _load_presets(self):
        if os.path.exists(self.preset_dir):
            items = []
            for f in os.listdir(self.preset_dir):
                full_path = os.path.join(self.preset_dir, f)
                if f.endswith(".json"):
                    items.append(f[:-5])
                elif os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, "preset.json")):
                    items.append(f) # Add folder name as preset
            
            self.preset_combo.addItems(sorted(items))

    def _on_effect_changed(self, text):
        if text: self.change_effect_signal.emit(text)

    def _on_preset_selected(self, index):
        if index > 0:
            self.load_preset_signal.emit(self.preset_combo.currentText())

    def _on_bg_toggled(self, checked):
        state = "On" if checked else "Off"
        self.bg_btn.setText(f"Background: {state}")
        self.toggle_background_signal.emit(checked)
    
    def set_current_state(self, effect_name, show_bg):
        self.effect_combo.blockSignals(True)
        self.effect_combo.setCurrentText(effect_name)
        self.effect_combo.blockSignals(False)
        self.bg_btn.setChecked(show_bg)
        self._on_bg_toggled(show_bg)

    def set_fps(self, fps):
        self.fps_slider.blockSignals(True)
        self.fps_spin.blockSignals(True)
        self.fps_slider.setValue(fps)
        self.fps_spin.setValue(fps)
        self.fps_slider.blockSignals(False)
        self.fps_spin.blockSignals(False)

    def _on_fps_changed(self, value):
        self.set_fps_signal.emit(value)

    def _on_bg_type_changed(self, text):
        self.bg_path_edit.setEnabled(text != "none")
        self.bg_browse_btn.setEnabled(text != "none")

    def _on_browse_bg(self):
        file_filter = "All Files (*.*)"
        bg_type = self.bg_type_combo.currentText()
        if bg_type == "image": file_filter = "Images (*.png *.jpg *.jpeg *.bmp)"
        elif bg_type == "video": file_filter = "Videos (*.mp4 *.avi *.mkv *.mov)"
        elif bg_type == "gif": file_filter = "GIF (*.gif)"
        path, _ = QFileDialog.getOpenFileName(self, "Select Background", "", file_filter)
        if path: self.bg_path_edit.setText(path)

    def _on_apply_bg(self):
        bg_type = self.bg_type_combo.currentText()
        config = {"type": bg_type}
        if bg_type != "none": config["path"] = self.bg_path_edit.text()
        self.set_background_signal.emit(config)
