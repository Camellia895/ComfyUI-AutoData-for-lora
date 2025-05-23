# image_marker_tool/image_viewer.py
try:
    from PyQt5.QtWidgets import QGraphicsView, QGraphicsPixmapItem
    from PyQt5.QtGui import QPainter, QTransform, QWheelEvent
    from PyQt5.QtCore import Qt, QRectF
except ImportError:
    print("错误：image_viewer.py - PyQt5 未安装或无法导入。")
    # 可以选择抛出异常或提供备用实现（如果可能）
    raise

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self._current_zoom = 1.0
        self._min_zoom = 0.1
        self._max_zoom = 10.0

    def wheelEvent(self, event: QWheelEvent):
        """通过鼠标滚轮进行缩放"""
        angle = event.angleDelta().y()
        factor = 1.15 if angle > 0 else 1 / 1.15
        
        new_zoom = self._current_zoom * factor
        if self._min_zoom <= new_zoom <= self._max_zoom:
            self.scale(factor, factor)
            self._current_zoom = new_zoom
            # 如果主窗口有滑块，可以在这里发出信号或调用方法来同步滑块
            if hasattr(self.parent(), "sync_zoom_slider_from_view"):
                 self.parent().sync_zoom_slider_from_view(self._current_zoom)


    def set_zoom(self, zoom_level: float):
        """外部调用以设置缩放级别 (例如通过滑块)"""
        if zoom_level < self._min_zoom: zoom_level = self._min_zoom
        if zoom_level > self._max_zoom: zoom_level = self._max_zoom

        if self._current_zoom == 0: self._current_zoom = 1e-9 # 避免除以零
        
        # 计算相对于当前缩放的缩放因子
        factor = zoom_level / self._current_zoom
        
        self.scale(factor, factor)
        self._current_zoom = zoom_level
        
    def reset_zoom_and_fit(self, pixmap_item: QGraphicsPixmapItem = None):
        """重置缩放并将图片适应视图"""
        self.resetTransform() # 必须先重置变换
        self._current_zoom = 1.0 # 重置内部缩放因子
        if pixmap_item and self.scene():
            self.fitInView(pixmap_item, Qt.KeepAspectRatio)
            # 更新内部缩放因子以匹配fitInView后的实际缩放
            self._current_zoom = self.transform().m11() 
        elif self.scene() and self.scene().items(): # 如果没有特定item但场景有内容
            self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
            self._current_zoom = self.transform().m11()
        
        # 如果主窗口有滑块，可以在这里发出信号或调用方法来同步滑块
        if hasattr(self.parent(), "sync_zoom_slider_from_view"):
            self.parent().sync_zoom_slider_from_view(self._current_zoom)

    def get_current_zoom(self) -> float:
        return self._current_zoom