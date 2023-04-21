from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QGraphicsPixmapItem

# 用于诊断窗口的图像框
class MyGraphicsPixmapItem(QGraphicsPixmapItem):
    def __init__(self, pixmap, idx):
        super(MyGraphicsPixmapItem, self).__init__(pixmap)
        self.key = idx


