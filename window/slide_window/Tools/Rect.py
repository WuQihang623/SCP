import math
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPen, QBrush
from window.slide_window.Tools.BaseTool import BaseTool

class DrawRect(BaseTool):
    def __init__(self, scene: QGraphicsScene, view: QGraphicsView):
        super().__init__(scene, view)

    def mousePressEvent(self, event, downsample):
        if self.COLOR is not None:
            self.initialize()
            # 将可见范围的x,y坐标转换成在整张图中的坐标
            scene_pos = self.view.mapToScene(event.pos())
            point = [scene_pos.x() * downsample, scene_pos.y() * downsample]
            self.points.append(point)
            self.last_point = point

            # 绘制矩形框
            self.rect_item.setRect(scene_pos.x(), scene_pos.y(), 1, 1)
            self.scene.addItem(self.rect_item)
            self.rect_item.setZValue(25)

            # 绘制控制点
            self.addCycle2Scene(scene_pos)

    def mouseMoveEvent(self, event, downsample):
        if self.DRAW_FLAG:
            # 初始的位置
            start_x = self.points[0][0] / downsample
            start_y = self.points[0][1] / downsample
            # 绘制矩形框
            scene_pos = self.view.mapToScene(event.pos())
            self.rect_item.setRect(min(start_x, scene_pos.x()),
                                   min(start_y, scene_pos.y()),
                                   abs(start_x - scene_pos.x()),
                                   abs(start_y - scene_pos.y()))
            self.last_point = [scene_pos.x() * downsample, scene_pos.y() * downsample]

    def mouseRelease(self, event, downsample):
        if self.DRAW_FLAG:
            self.DRAW_FLAG = False
            # 初始的位置
            start_x = self.points[0][0] / downsample
            start_y = self.points[0][1] / downsample
            # 绘制矩形框
            scene_pos = self.view.mapToScene(event.pos())
            self.rect_item.setRect(min(start_x, scene_pos.x()),
                                   min(start_y, scene_pos.y()),
                                   abs(start_x - scene_pos.x()),
                                   abs(start_y - scene_pos.y()))

            # 判断矩形框大小，如果太小就不进行绘制
            if self.getArea(abs(start_x - scene_pos.x()),
                            abs(start_y - scene_pos.y())) * downsample**2 > 128**2:
                # 添加终点的控制点
                self.addCycle2Scene(scene_pos)
                self.points.append([scene_pos.x() * downsample, scene_pos.y() * downsample])
                color = list(self.COLOR.getRgb())
                type = self.TYPE
                # 记录下绘制的item
                annotataion_info = {
                    "location": self.points,
                    "color": color,
                    'tool': "矩形",
                    "type": type,
                    'annotation_item': self.rect_item,
                    "control_point_items": self.control_point_items
                }
                return annotataion_info

            else:
                self.scene.removeItem(self.rect_item)
                for item in self.control_point_items:
                    self.scene.removeItem(item)
                return None
        return None

    # 当scene改变后，需要重新绘制当前绘制的这个形状
    def redraw(self, downsample, width=None):
        if self.DRAW_FLAG:
            if width is not None:
                self.pen.setWidth(width)
            self.rect_item = QGraphicsRectItem()
            self.rect_item.setPen(self.pen)

            # 初始的位置
            start_x = self.points[0][0] / downsample
            start_y = self.points[0][1] / downsample

            end_x = self.last_point[0] / downsample
            end_y = self.last_point[1] / downsample
            self.rect_item.setRect(min(start_x, end_x),
                                   min(start_y, end_y),
                                   abs(start_x - end_x),
                                   abs(start_y - end_y))
            self.rect_item.setZValue(25)
            self.scene.addItem(self.rect_item)
            # 绘制控制点, 由于是修改control_point_item, 因此不能使用self.addCycle2Scene
            cycle = self.scene.addEllipse(0, 0, 8, 8)
            cycle.setPos(QPoint(start_x - 4, start_y - 4))
            cycle.setPen(QPen(self.COLOR))
            cycle.setBrush(QBrush(self.COLOR))
            cycle.setZValue(30)
            self.control_point_items = [cycle]

    def draw(self, points, color, width, downsample, choosed=False):
        control_point_items = []
        rect_item = QGraphicsRectItem()
        pen = QPen()
        pen.setColor(color)
        pen.setWidth(width)
        rect_item.setPen(pen)
        start_x, start_y = points[0][0] / downsample, points[0][1] / downsample
        end_x, end_y = points[1][0] / downsample, points[1][1] / downsample
        rect_item.setRect(min(start_x, end_x), min(start_y, end_y), abs(start_x - end_x), abs(start_y - end_y))
        rect_item.setZValue(25)
        self.scene.addItem(rect_item)
        # 绘制控制点
        if choosed:
            control_points = [[start_x, start_y], [end_x, end_y]]
            for i in range(2):
                cycle = self.scene.addEllipse(0, 0, 2*width, 2*width)
                cycle.setPos(QPoint(control_points[i][0] - width, control_points[i][1] - width))
                cycle.setPen(QPen(color))
                cycle.setBrush(QBrush(color))
                cycle.setZValue(30)
                control_point_items.append(cycle)

        return rect_item, control_point_items, None

    def getArea(self, width, height):
        area = width * height
        return area



