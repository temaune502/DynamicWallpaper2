from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, 
                               QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton, QColorDialog,
                               QLabel, QLineEdit, QComboBox)
from PySide6.QtCore import Signal, Qt

class EffectConfigPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.form = QFormLayout()
        self.layout.addLayout(self.form)
        self.config = {}
        self.on_change_callback = None

    def load_schema(self, schema, current_config):
        # Clear existing
        while self.form.count():
            child = self.form.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            
        self.config = current_config.copy()
        
        for key, meta in schema.items():
            val_type = meta.get("type")
            label = meta.get("label", key)
            default = meta.get("default")
            curr_val = self.config.get(key, default)
            
            widget = None
            if val_type == "float":
                widget = QDoubleSpinBox()
                widget.setRange(meta.get("min", 0.0), meta.get("max", 100.0))
                widget.setValue(float(curr_val))
                widget.setSingleStep(0.1)
                widget.valueChanged.connect(lambda v, k=key: self._update_val(k, v))
                
            elif val_type == "int":
                widget = QSpinBox()
                widget.setRange(meta.get("min", 0), meta.get("max", 100))
                widget.setValue(int(curr_val))
                widget.valueChanged.connect(lambda v, k=key: self._update_val(k, v))
                
            elif val_type == "bool":
                widget = QCheckBox()
                widget.setChecked(bool(curr_val))
                widget.toggled.connect(lambda v, k=key: self._update_val(k, v))
                
            elif val_type == "color":
                widget = QPushButton()
                # If tuple, convert to QColor
                c = curr_val
                if isinstance(c, (list, tuple)) and len(c) >= 3:
                     col = QColor(c[0], c[1], c[2])
                else:
                     col = QColor(255, 255, 255)
                self._set_btn_color(widget, col)
                widget.clicked.connect(lambda _, w=widget, k=key: self._pick_color(w, k))
                
            if widget:
                self.form.addRow(label, widget)

    def _update_val(self, key, value):
        self.config[key] = value
        if self.on_change_callback:
            self.on_change_callback(self.config)

    def _pick_color(self, btn, key):
        c = btn.palette().button().color()
        new_c = QColorDialog.getColor(c, self, "Pick Color")
        if new_c.isValid():
            self._set_btn_color(btn, new_c)
            self._update_val(key, (new_c.red(), new_c.green(), new_c.blue()))

    def _set_btn_color(self, btn, color):
        btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #555;")

from PySide6.QtWidgets import QListWidget, QHBoxLayout, QMessageBox

class PlaylistPanel(QWidget):
    playlist_changed = Signal(list, int) # items, interval

    def __init__(self, effect_registry):
        super().__init__()
        self.registry = effect_registry
        self.layout = QVBoxLayout(self)
        
        # Interval
        int_layout = QHBoxLayout()
        int_layout.addWidget(QLabel("Interval (ms):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(100, 60000)
        self.interval_spin.setValue(5000)
        self.interval_spin.setSingleStep(100)
        self.interval_spin.valueChanged.connect(self._emit_change)
        int_layout.addWidget(self.interval_spin)
        self.layout.addLayout(int_layout)

        # List
        self.list_widget = QListWidget()
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        self.list_widget.model().rowsMoved.connect(self._emit_change)
        self.layout.addWidget(self.list_widget)

        # Controls
        ctrl_layout = QHBoxLayout()
        self.eff_combo = QComboBox()
        self.eff_combo.addItems(sorted(list(self.registry.effects.keys())))
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_item)
        
        del_btn = QPushButton("Remove")
        del_btn.clicked.connect(self._remove_item)
        
        ctrl_layout.addWidget(self.eff_combo)
        ctrl_layout.addWidget(add_btn)
        ctrl_layout.addWidget(del_btn)
        self.layout.addLayout(ctrl_layout)

    def load_state(self, playlist, interval):
        self.list_widget.clear()
        self.list_widget.addItems(playlist)
        self.interval_spin.blockSignals(True)
        self.interval_spin.setValue(int(interval))
        self.interval_spin.blockSignals(False)

    def _add_item(self):
        txt = self.eff_combo.currentText()
        if txt:
            self.list_widget.addItem(txt)
            self._emit_change()

    def _remove_item(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            self.list_widget.takeItem(row)
            self._emit_change()

    def _emit_change(self):
        items = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        self.playlist_changed.emit(items, self.interval_spin.value())


class WidgetConfigPanel(QWidget):
    widget_changed = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.layout = QFormLayout(self)
        self.current_data = None
        self.inputs = {}

    def load_widget(self, widget_data):
        self.current_data = widget_data
        
        # Clear
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        self.inputs = {}
            
        if not widget_data:
            self.layout.addRow(QLabel("No widget selected"))
            return

        # Common fields
        self._add_input("x", int, widget_data.get("x", 0))
        self._add_input("y", int, widget_data.get("y", 0))
        # self._add_input("scale", float, widget_data.get("scale", 1.0)) # Scale is not standard yet?

        # Helper to detect type
        for k, v in widget_data.items():
            if k in ["type", "id", "x", "y"]: continue
            
            if isinstance(v, bool):
                self._add_input(k, bool, v)
            elif isinstance(v, int):
                self._add_input(k, int, v)
            elif isinstance(v, float):
                self._add_input(k, float, v)
            elif isinstance(v, str):
                self._add_input(k, str, v)
            elif isinstance(v, list) and len(v) in [3, 4]: # Color?
                 self._add_input(k, "color", v)

    def _add_input(self, key, type_, value):
        widget = None
        if type_ == int:
            widget = QSpinBox()
            widget.setRange(-9999, 9999)
            widget.setValue(value)
            widget.valueChanged.connect(lambda v: self._on_val(key, v))
        elif type_ == float:
            widget = QDoubleSpinBox()
            widget.setRange(0.1, 100.0)
            widget.setValue(value)
            widget.valueChanged.connect(lambda v: self._on_val(key, v))
        elif type_ == str:
            widget = QLineEdit()
            widget.setText(value)
            widget.textChanged.connect(lambda v: self._on_val(key, v))
        elif type_ == bool:
            widget = QCheckBox()
            widget.setChecked(value)
            widget.toggled.connect(lambda v: self._on_val(key, v))
        elif type_ == "color":
            widget = QPushButton()
            c = QColor(*value[:3])
            widget.setStyleSheet(f"background-color: {c.name()};")
            widget.clicked.connect(lambda: self._pick_color(widget, key))
            
        if widget:
            self.inputs[key] = widget
            self.layout.addRow(key, widget)

    def _on_val(self, key, val):
        if self.current_data:
            self.current_data[key] = val
            self.widget_changed.emit(self.current_data)

    def _pick_color(self, btn, key):
        c = QColorDialog.getColor(Qt.white, self)
        if c.isValid():
            val = [c.red(), c.green(), c.blue(), 255]
            btn.setStyleSheet(f"background-color: {c.name()};")
            self._on_val(key, val)

