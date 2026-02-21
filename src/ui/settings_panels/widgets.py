from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QPushButton, QGroupBox, QListWidget, 
                               QListWidgetItem, QFormLayout, QSpinBox)
from PySide6.QtCore import Qt, Signal
from src.widgets.base import WidgetRegistry

class WidgetsSettingsTab(QWidget):
    add_widget_signal = Signal(dict)
    remove_widget_signal = Signal(int)
    update_widget_signal = Signal(int, dict)
    request_refresh_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_widgets_data = []
        self.is_updating_ui = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Top Bar: Add & Refresh
        top_layout = QHBoxLayout()
        self.widget_type_combo = QComboBox()
        self.widget_registry = WidgetRegistry()
        self.widget_type_combo.addItems(sorted(list(self.widget_registry.available_classes.keys())))
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._on_add_widget)
        
        refresh_btn = QPushButton("↻")
        refresh_btn.setFixedWidth(30)
        refresh_btn.setToolTip("Refresh List")
        refresh_btn.clicked.connect(self.request_refresh_signal.emit) 

        top_layout.addWidget(QLabel("Type:"))
        top_layout.addWidget(self.widget_type_combo)
        top_layout.addWidget(add_btn)
        top_layout.addWidget(refresh_btn)
        layout.addLayout(top_layout)
        
        # List of widgets
        self.widget_list = QListWidget()
        self.widget_list.currentRowChanged.connect(self._on_widget_selected)
        layout.addWidget(self.widget_list)
        
        # Edit Properties Group
        self.edit_group = QGroupBox("Selected Widget Properties")
        self.edit_group.setEnabled(False)
        form = QFormLayout()
        
        self.w_anchor = QComboBox()
        self.w_anchor.addItems(["top-left", "top-right", "bottom-left", "bottom-right", "center"])
        self.w_anchor.currentTextChanged.connect(self._on_widget_prop_changed)
        
        self.w_x = QSpinBox()
        self.w_x.setRange(-2000, 4000)
        self.w_x.setSingleStep(10)
        self.w_x.valueChanged.connect(self._on_widget_prop_changed)
        
        self.w_y = QSpinBox()
        self.w_y.setRange(-2000, 4000)
        self.w_y.setSingleStep(10)
        self.w_y.valueChanged.connect(self._on_widget_prop_changed)
        
        form.addRow("Anchor:", self.w_anchor)
        form.addRow("X Offset:", self.w_x)
        form.addRow("Y Offset:", self.w_y)
        
        # Quick Nudge Buttons
        nudge_layout = QHBoxLayout()
        btn_up = QPushButton("▲")
        btn_down = QPushButton("▼")
        btn_left = QPushButton("◄")
        btn_right = QPushButton("►")
        
        for btn in [btn_up, btn_down, btn_left, btn_right]:
            btn.setFixedWidth(30)
            btn.setFocusPolicy(Qt.NoFocus)
            
        btn_up.clicked.connect(lambda _: self.w_y.setValue(self.w_y.value() - 10))
        btn_down.clicked.connect(lambda _: self.w_y.setValue(self.w_y.value() + 10))
        btn_left.clicked.connect(lambda _: self.w_x.setValue(self.w_x.value() - 10))
        btn_right.clicked.connect(lambda _: self.w_x.setValue(self.w_x.value() + 10))
        
        nudge_layout.addWidget(QLabel("Move:"))
        nudge_layout.addWidget(btn_left)
        nudge_layout.addWidget(btn_up)
        nudge_layout.addWidget(btn_down)
        nudge_layout.addWidget(btn_right)
        nudge_layout.addStretch()
        
        form.addRow(nudge_layout)
        
        self.edit_group.setLayout(form)
        layout.addWidget(self.edit_group)
        
        # Remove
        self.remove_btn = QPushButton("Delete Selected Widget")
        self.remove_btn.setObjectName("delete_btn")
        self.remove_btn.clicked.connect(self._on_remove_widget)
        self.remove_btn.setEnabled(False)
        layout.addWidget(self.remove_btn)

    def set_widgets_list(self, widgets_data):
        current_row = self.widget_list.currentRow()
        
        self.is_updating_ui = True
        self.active_widgets_data = widgets_data
        self.widget_list.clear()
        
        for i, w in enumerate(widgets_data):
            w_type = w.get('type', 'Unknown')
            anchor = w.get('anchor', '?')
            label = f"{i+1}. {w_type.upper()} [{anchor}]"
            item = QListWidgetItem(label)
            self.widget_list.addItem(item)
            
        self.is_updating_ui = False
        
        if current_row >= 0 and current_row < self.widget_list.count():
            self.widget_list.setCurrentRow(current_row)
        else:
            self.edit_group.setEnabled(False)
            self.remove_btn.setEnabled(False)

    def _on_widget_selected(self, row):
        if row < 0 or row >= len(self.active_widgets_data):
            self.edit_group.setEnabled(False)
            self.remove_btn.setEnabled(False)
            return
            
        self.is_updating_ui = True
        data = self.active_widgets_data[row]
        self.edit_group.setEnabled(True)
        self.remove_btn.setEnabled(True)
        
        self.w_anchor.setCurrentText(data.get('anchor', 'top-left'))
        self.w_x.setValue(data.get('x', 0))
        self.w_y.setValue(data.get('y', 0))
        self.is_updating_ui = False

    def _on_widget_prop_changed(self, *args):
        if self.is_updating_ui: return
        
        row = self.widget_list.currentRow()
        if row < 0: return
        
        new_data = {
            'anchor': self.w_anchor.currentText(),
            'x': self.w_x.value(),
            'y': self.w_y.value()
        }
        
        self.active_widgets_data[row].update(new_data)
        
        w_type = self.active_widgets_data[row].get('type', 'Unknown')
        new_label = f"{row+1}. {w_type.upper()} [{new_data['anchor']}]"
        
        item = self.widget_list.item(row)
        if item.text() != new_label:
            item.setText(new_label)
        
        self.update_widget_signal.emit(row, new_data)

    def _on_add_widget(self):
        w_type = self.widget_type_combo.currentText()
        default_config = {
            "type": w_type,
            "anchor": "top-left",
            "x": 50, 
            "y": 50
        }
        self.add_widget_signal.emit(default_config)

    def _on_remove_widget(self):
        row = self.widget_list.currentRow()
        if row >= 0:
            self.remove_widget_signal.emit(row)
