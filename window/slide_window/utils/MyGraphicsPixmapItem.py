from PyQt5.QtWidgets import QGraphicsPixmapItem

class MyGraphicsPixmapItem(QGraphicsPixmapItem):
    def __init__(self, pixmap, idx):
        super(MyGraphicsPixmapItem, self).__init__(pixmap)
        self.key = idx