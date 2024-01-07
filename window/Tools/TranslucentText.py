import typing
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsTextItem, QWidget, QStyleOptionGraphicsItem

# 创建一个带有半透明背景的文本项
class TranslucentTextItem(QGraphicsTextItem):
    def __init__(self):
        super(TranslucentTextItem, self).__init__()

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: QWidget) -> None:
        color = QColor(Qt.white)
        color.setAlpha(50)
        painter.setBrush(color)
        painter.drawRect(self.boundingRect())
        QGraphicsTextItem.paint(self, painter, option, widget)