from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QMainWindow
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, QRectF

class MouseItem(QGraphicsItem):
    def __init__(self, size=10):
        super().__init__()
        self.crosshairSize = size

    def boundingRect(self):
        return QRectF(-self.crosshairSize / 2, -self.crosshairSize / 2, self.crosshairSize, self.crosshairSize)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor(255, 255, 0))  # 红色
        painter.drawLine(-self.crosshairSize / 2, 0, self.crosshairSize / 2, 0)
        painter.drawLine(0, -self.crosshairSize / 2, 0, self.crosshairSize / 2)

    def setPos(self, x, y):
        super().setPos(x, y)

    def clearItem(self):
        scene = self.scene()
        if scene:
            scene.removeItem(self)