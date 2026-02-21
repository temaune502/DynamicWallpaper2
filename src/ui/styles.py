DARK_THEME = """
QWidget {
    background-color: #2b2b2b;
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}

QGroupBox {
    border: 1px solid #444;
    border-radius: 5px;
    margin-top: 10px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    background-color: #2b2b2b;
    color: #aaaaaa;
}

QPushButton {
    background-color: #3e3e3e;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 5px 10px;
}

QPushButton:hover {
    background-color: #4e4e4e;
    border-color: #666;
}

QPushButton:pressed {
    background-color: #2e2e2e;
}

QPushButton:checked {
    background-color: #4A90E2;
    border-color: #4A90E2;
    color: white;
}

QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {
    background-color: #333;
    border: 1px solid #555;
    border-radius: 3px;
    padding: 4px;
    color: #eee;
}

QComboBox:hover, QSpinBox:hover, QLineEdit:hover {
    border-color: #777;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QListWidget {
    background-color: #333;
    border: 1px solid #555;
    border-radius: 3px;
}

QListWidget::item:selected {
    background-color: #4A90E2;
    color: white;
}

QTabWidget::pane {
    border: 1px solid #444;
    border-top: none;
}

QTabBar::tab {
    background-color: #333;
    border: 1px solid #444;
    padding: 6px 12px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #2b2b2b;
    border-bottom: 2px solid #4A90E2; 
}

QSlider::groove:horizontal {
    border: 1px solid #555;
    height: 6px;
    background: #333;
    margin: 2px 0;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #4A90E2;
    border: 1px solid #4A90E2;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
"""
