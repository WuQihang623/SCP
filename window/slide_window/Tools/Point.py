import math
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem, QMessageBox
from PyQt5.QtCore import QPoint, QObject
from PyQt5.QtGui import QPen, QBrush, QColor

class DrawPoint(QObject):
    def __init__(self, scene: QGraphicsScene, view: QGraphicsView):
        super().__init__()
        self.scene = scene
        self.view = view
        self.points = []
        self.point_items = []
        self.colors = [[255, 0, 0],
                       [0, 255, 0],
                       [0, 0, 255],
                       [0, 0, 0]]

    def restart(self):
        self.points = []
        self.point_items = []

    def mouseDoubleClickEvent(self, event, downsample):
        if len(self.points) < 4:
            # 确认最终的位置
            scene_pos = self.view.mapToScene(event.pos())
            self.points.append([scene_pos.x() * downsample, scene_pos.y() * downsample])
            self.draw([scene_pos.x(), scene_pos.y()], len(self.points)-1)

        else:
            QMessageBox.warning(self, "警告", "最多只能设置4个点！")

    def draw(self, point, idx):
        cycle = self.scene.addEllipse(0, 0, 8, 8)
        cycle.setPos(QPoint(point[0] - 4, point[1] - 4))
        color = QColor(*self.colors[idx])
        cycle.setPen(QPen(color))
        cycle.setBrush(QBrush(color))
        cycle.setZValue(30)

    def redraw(self, downsample):
        for idx, point in enumerate(self.points):
            x = point[0] / downsample
            y = point[1] / downsample
            self.draw([x, y], idx)

    def deleteItem(self):
        try:
            for item in self.point_items:
                self.scene.removeItem(item)
            self.point_items = []
        except:
            return

    def get_registration_points(self):
        if len(self.points) == 4:
            return self.points
        else:
            return None


