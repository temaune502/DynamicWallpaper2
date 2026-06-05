from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QComboBox, 
                               QLabel, QPushButton, QHBoxLayout, QScrollArea, QLineEdit, QFileDialog, QTabWidget)
from PySide6.QtCore import Signal
from src.ui.editor.panels import EffectConfigPanel, PlaylistPanel, WidgetConfigPanel
from src.effects.base import EffectRegistry
from src.ui.editor.preset_mgr import PresetManager

class SidebarManager(QWidget):
    preset_load_signal = Signal(str) # name
    preset_save_signal = Signal()
    preset_new_signal = Signal()
    
    effect_changed_signal = Signal(str, dict)
    playlist_changed_signal = Signal(list, int)
    bg_changed_signal = Signal(dict)
    
    add_widget_signal = Signal(str)
    widget_updated_signal = Signal(dict)
    
    def __init__(self, preset_mgr):
        super().__init__()
        self.preset_mgr = preset_mgr
        self.layout = QVBoxLayout(self)
        self.registry = EffectRegistry()
        self._init_ui()
        self.current_effect_config = {}

    def _init_ui(self):
        # Top: Presets
        p_group = QGroupBox("Preset")
        p_layout = QVBoxLayout()
        self.preset_combo = QComboBox()
        self._refresh_presets()
        
        btn_layout = QHBoxLayout()
        self.load_btn = QPushButton("Load")
        self.load_btn.clicked.connect(lambda: self.preset_load_signal.emit(self.preset_combo.currentText()))
        
        new_btn = QPushButton("New")
        new_btn.clicked.connect(self.preset_new_signal.emit)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.preset_save_signal.emit)
        
        btn_layout.addWidget(self.load_btn)
        btn_layout.addWidget(new_btn)
        btn_layout.addWidget(save_btn)
        
        p_layout.addWidget(self.preset_combo)
        p_layout.addLayout(btn_layout)
        p_group.setLayout(p_layout)
        self.layout.addWidget(p_group)

        # Tabs
        self.tabs = QTabWidget()
        
        # --- Tab 1: General (Effect & BG) ---
        tab_gen = QWidget()
        gen_layout = QVBoxLayout(tab_gen)
        
        # Effect
        e_group = QGroupBox("Active Effect")
        e_layout = QVBoxLayout()
        self.effect_combo = QComboBox()
        self.effect_combo.addItems(["none"] + sorted(list(self.registry.effects.keys())))
        self.effect_combo.currentTextChanged.connect(self._on_effect_type_changed)
        
        self.config_panel = EffectConfigPanel()
        self.config_panel.on_change_callback = self._on_config_changed
        
        scroll = QScrollArea()
        scroll.setWidget(self.config_panel)
        scroll.setWidgetResizable(True)
        
        e_layout.addWidget(self.effect_combo)
        e_layout.addWidget(scroll)
        e_group.setLayout(e_layout)
        gen_layout.addWidget(e_group)

        # Background
        b_group = QGroupBox("Background")
        b_layout = QVBoxLayout()
        self.bg_combo = QComboBox()
        self.bg_combo.addItems(["none", "image", "video"])
        self.bg_combo.currentTextChanged.connect(self._on_bg_type_changed)
        
        self.bg_path = QLineEdit()
        self.bg_path.setPlaceholderText("File Path...")
        self.bg_browse = QPushButton("Browse")
        self.bg_browse.clicked.connect(self._browse_bg)
        
        b_layout.addWidget(QLabel("Type:"))
        b_layout.addWidget(self.bg_combo)
        b_layout.addWidget(QLabel("Path:"))
        b_layout.addWidget(self.bg_path)
        b_layout.addWidget(self.bg_browse)
        b_group.setLayout(b_layout)
        gen_layout.addWidget(b_group)
        
        self.tabs.addTab(tab_gen, "General")
        
        # --- Tab 2: Playlist ---
        self.playlist_panel = PlaylistPanel(self.registry)
        self.playlist_panel.playlist_changed.connect(self.playlist_changed_signal.emit)
        self.tabs.addTab(self.playlist_panel, "Playlist")
        
        # --- Tab 3: Widgets ---
        tab_wid = QWidget()
        wid_layout = QVBoxLayout(tab_wid)
        
        # Add
        add_group = QGroupBox("Add Widget")
        add_layout = QHBoxLayout()
        self.widget_combo = QComboBox()
        from src.widgets.base import WidgetRegistry
        self.w_registry = WidgetRegistry()
        self.widget_combo.addItems(sorted(list(self.w_registry.available_classes.keys())))
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_widget)
        
        add_layout.addWidget(self.widget_combo)
        add_layout.addWidget(add_btn)
        add_group.setLayout(add_layout)
        wid_layout.addWidget(add_group)
        
        # Edit
        edit_group = QGroupBox("Edit Selected")
        edit_layout = QVBoxLayout()
        self.widget_config_panel = WidgetConfigPanel()
        self.widget_config_panel.widget_changed.connect(self.widget_updated_signal.emit)
        
        w_scroll = QScrollArea()
        w_scroll.setWidget(self.widget_config_panel)
        w_scroll.setWidgetResizable(True)
        
        edit_layout.addWidget(w_scroll)
        edit_group.setLayout(edit_layout)
        wid_layout.addWidget(edit_group)
        
        self.tabs.addTab(tab_wid, "Widgets")
        
        self.layout.addWidget(self.tabs)

    def _refresh_presets(self):
        self.preset_combo.clear()
        presets = self.preset_mgr.list_presets()
        for p in presets:
            self.preset_combo.addItem(p["name"])

    def set_state(self, config):
        # Update UI from config
        eff = config.get("effect", "none")
        self.effect_combo.blockSignals(True)
        self.effect_combo.setCurrentText(eff)
        self.effect_combo.blockSignals(False)
        
        self.current_effect_config = config.get("effect_config", {})
        self._update_panel(eff)
        
        bg = config.get("background", {}).get("type", "none")
        path = config.get("background", {}).get("path", "")
        self.bg_combo.blockSignals(True)
        self.bg_combo.setCurrentText(bg)
        self.bg_combo.blockSignals(False)
        self.bg_path.setText(path)
        
        # Playlist
        pl = config.get("effects_playlist", [])
        inter = config.get("playlist_interval", 5000)
        self.playlist_panel.load_state(pl, inter)
        
        # Clear widget selection
        self.widget_config_panel.load_widget(None)
        
    def on_widget_selected(self, widget_data):
        # Switch to widgets tab
        self.tabs.setCurrentIndex(2)
        self.widget_config_panel.load_widget(widget_data)

    def _on_effect_type_changed(self, text):
        self.current_effect_config = {} # Reset on type change
        self._update_panel(text)
        self.effect_changed_signal.emit(text, self.current_effect_config)

    def _update_panel(self, effect_name):
        effect = self.registry.get_effect(effect_name)
        if effect and hasattr(effect, 'get_schema'):
            schema = effect.get_schema()
            if schema:
                self.config_panel.load_schema(schema, self.current_effect_config)
                self.config_panel.setVisible(True)
                return
        self.config_panel.setVisible(False)

    def _on_config_changed(self, new_config):
        self.current_effect_config = new_config
        self.effect_changed_signal.emit(self.effect_combo.currentText(), new_config)

    def _on_bg_type_changed(self, text):
        self.bg_changed_signal.emit({"type": text, "path": self.bg_path.text()})
        
    def _browse_bg(self):
        file_filter = "All Files (*.*)"
        bg_type = self.bg_combo.currentText()
        if bg_type == "image": file_filter = "Images (*.png *.jpg *.jpeg *.bmp)"
        elif bg_type == "video": file_filter = "Videos (*.mp4 *.avi *.mkv *.mov)"
        
        path, _ = QFileDialog.getOpenFileName(self, "Select Background", "", file_filter)
        if path: 
            self.bg_path.setText(path)
            self.bg_changed_signal.emit({"type": bg_type, "path": path})

    def _add_widget(self):
        w_type = self.widget_combo.currentText()
        if w_type:
            self.add_widget_signal.emit(w_type)
