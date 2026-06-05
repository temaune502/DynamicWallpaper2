from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QLabel, QTimer
# Using relative import if possible, or assume it's passed during init?
# To avoid circular imports, maybe we just pass the registry to it.

class DebugViewer(QDialog):
    def __init__(self, effect_registry, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Effect Cache Debug")
        self.resize(500, 600)
        self.registry = effect_registry
        
        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFontPointSize(10)
        layout.addWidget(QLabel("Loaded Effects & Cache Status:"))
        layout.addWidget(self.text_edit)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(1000)
        self.refresh()

    def refresh(self):
        txt = ""
        for name, instance in self.registry.effects.items():
            txt += f"Effect: {name}\n"
            if hasattr(instance, 'config'):
                txt += f"  Config: {instance.config}\n"
            txt += "-"*20 + "\n"
        self.text_edit.setText(txt)
