from PySide6.QtWidgets import QGraphicsView, QGraphicsRectItem, QGraphicsTextItem
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QFont

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.scale_factor = 1.15
        
        # Use OpenGL Viewport for performance
        from PySide6.QtOpenGLWidgets import QOpenGLWidget
        self.setViewport(QOpenGLWidget())
        
        self.preview_engine = None

    def set_engine(self, engine):
        self.preview_engine = engine

    def drawBackground(self, p, rect):
        p.save()
        # Do NOT resetTransform to keep scene coordinates (so it zooms/pans)
        
        # Fill strictly the 1920x1080 area
        # We don't need to fillRect outside because the scene usually handles that or we just leave it.
        # But wait, QGraphicsView draws background for the update rect.
        # We only want to draw the effect inside 0,0,1920,1080.
        
        # Draw base for effect
        p.fillRect(0, 0, 1920, 1080, QColor(0, 0, 0))
        
        # Clip to ensure no overdraw if effect is messy
        p.setClipRect(0, 0, 1920, 1080)
        
        if self.preview_engine:
            self.preview_engine.draw(p, 1920, 1080)
            
        p.setClipping(False)
        
        # Draw Border
        p.setPen(QPen(QColor(255, 0, 0), 4))
        p.setBrush(Qt.NoBrush)
        p.drawRect(0, 0, 1920, 1080)
            
        p.restore()

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.scale(self.scale_factor, self.scale_factor)
            else:
                self.scale(1.0 / self.scale_factor, 1.0 / self.scale_factor)
        else:
            super().wheelEvent(event)

class DraggableWidget(QGraphicsRectItem):
    def __init__(self, x, y, size_x, size_y, label, widget_data, on_select_cb=None, on_move_cb=None):
        super().__init__(0, 0, size_x, size_y)
        self.setPos(x, y)
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        
        self.widget_data = widget_data
        self.on_select_cb = on_select_cb
        self.on_move_cb = on_move_cb
        
        # Try to instantiate real widget for preview
        from src.widgets.base import WidgetRegistry
        registry = WidgetRegistry()
        self.real_widget = registry.create_widget(widget_data.get("type"), widget_data)
        
        # Transparent background, white border
        self.setBrush(QBrush(QColor(0, 0, 0, 10))) 
        self.setPen(QPen(QColor(255, 255, 255, 100), 1))

    def paint(self, painter, option, widget=None):
        # Draw bounding box
        super().paint(painter, option, widget)
        
        # Draw real widget preview
        if self.real_widget:
            painter.save()
            # Widget draw methods expect (p, w, h, phase)
            # They usually draw at (self.x, self.y) relative to window
            # But here we are in item coords (0,0 is top-left of this item)
            # We need to temporarily force widget x,y to 0,0
            old_x, old_y = self.real_widget.x, self.real_widget.y
            self.real_widget.x = 0
            self.real_widget.y = 0
            
            # Use our rect size as "window size" for relative scaling? 
            # Or just draw it? Most widgets use absolute pixels or anchor.
            # If we want WYSIWYG, we should pass the full 1920x1080 and rely on Item transformation?
            # No, DraggableWidget IS the position.
            
            try:
                # We are at (0,0) of the item.
                self.real_widget.draw(painter, int(self.rect().width()), int(self.rect().height()), 0)
            except Exception as e:
                painter.setPen(Qt.red)
                painter.drawText(10, 20, f"Error: {e}")
                
            self.real_widget.x = old_x
            self.real_widget.y = old_y
            painter.restore()
        else:
             painter.setPen(Qt.white)
             painter.drawText(10, 20, self.widget_data.get("type", "Unknown"))

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self.on_select_cb:
            self.on_select_cb(self.widget_data)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        # Update data position
        self.widget_data["x"] = int(self.pos().x())
        self.widget_data["y"] = int(self.pos().y())
        if self.on_move_cb:
            self.on_move_cb(self.widget_data, self.pos())

