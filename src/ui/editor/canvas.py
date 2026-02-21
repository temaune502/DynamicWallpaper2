from PySide6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtGui import QPixmap, QColor, QPen
from PySide6.QtCore import Qt, Signal, QObject
from src.ui.editor.graphics import ZoomableGraphicsView, DraggableWidget
from src.ui.editor.preview import PreviewEngine

class CanvasManager(QObject):
    widget_selected = Signal(dict)
    widget_moved = Signal(dict, object) # dict, pos

    def __init__(self, parent_layout):
        super().__init__()
        self.scene = QGraphicsScene()
        # self.scene.setBackgroundBrush(QColor(20, 20, 20)) # Handled by drawBackground now
        self.view = ZoomableGraphicsView(self.scene)
        parent_layout.addWidget(self.view)
        
        self.engine = PreviewEngine()
        self.view.set_engine(self.engine)
        self.engine.on_update = self.scene.update # Trigger redraw on tick
        self.engine.start()
        
        self.bg_item = None
        self.widgets = []
        self.widget_items = []
        
        # Draw initial bounds
        self.scene.setSceneRect(0, 0, 1920, 1080)
        self.scene.addRect(0, 0, 1920, 1080, QPen(QColor(100, 100, 100), 2))

    def update_config(self, config):
        self.engine.set_config(config)

    def add_widget(self, config):
        # Create Draggable Widget item
        from src.ui.editor.graphics import DraggableWidget
        
        w_item = DraggableWidget(config["x"], config["y"], 200, 100, config["type"], config)
        self.scene.addItem(w_item)
        self.widget_items.append(w_item)
        self.widgets.append(config)

    def set_widgets(self, widgets):
        self.clear_widgets()
        for w in widgets:
            self.add_widget(w)

    def clear_widgets(self):
        for item in self.widget_items:
            self.scene.removeItem(item)
        self.widget_items.clear()
        self.widgets = []

    def set_widgets(self, widgets_data):
        self.clear_widgets()
        for w_data in widgets_data:
            self.add_widget_item(w_data)

    def add_widget_item(self, w_data):
        self.widgets.append(w_data)
        x = w_data.get("x", 100)
        y = w_data.get("y", 100)
        w_type = w_data.get("type", "Unknown")
        
        item = DraggableWidget(x, y, 200, 100, w_type, w_data,
                               on_select_cb=self._on_item_selected,
                               on_move_cb=self._on_item_moved)
        self.scene.addItem(item)
        self.widget_items.append(item)

    def _on_item_selected(self, data):
        self.widget_selected.emit(data)

    def _on_item_moved(self, data, pos):
        data['x'] = int(pos.x())
        data['y'] = int(pos.y())
        self.widget_moved.emit(data, pos)

    def refresh(self):
        self.scene.update()
