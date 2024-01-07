import os
import json
import constants
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QColor, QPen, QBrush
from window.slide_window.Tools.BaseTool import BaseTool

class DrawFixedRect(BaseTool):
    FixedRectSizePath = os.path.join(constants.cache_path, "FixedRectSize.json")
    def __init__(self, scene: QGraphicsScene, view: QGraphicsView):
        super().__init__(scene, view)
        self.WIDTH = 512  # ROI的大小
        self.HEIGHT = 512

        # 从缓存中读取Rect的大小
        if os.path.exists(self.FixedRectSizePath):
            with open(self.FixedRectSizePath, 'r') as f:
                data = json.load(f)
                width = data.get('width')
                height = data.get("height")
                self.WIDTH = width if width is not None else self.WIDTH
                self.HEIGHT = height if height is not None else self.HEIGHT
                f.close()

    def set_rect_size(self, width, height):
        self.WIDTH = width
        self.HEIGHT = height
        with open(self.FixedRectSizePath, 'w') as f:
            f.write(json.dumps({"width": self.WIDTH, "height": self.HEIGHT}, indent=2))
            f.close()

    def mousePressEvent(self, event, downsample):
        if self.COLOR is not None:
            self.initialize()
            # 将可见范围的x,y坐标转换成在整张图中的坐标
            scene_pos = self.view.mapToScene(event.pos())
            self.rect_item.setRect(scene_pos.x(), scene_pos.y(),
                                   int(self.WIDTH / downsample), int(self.HEIGHT / downsample))
            self.scene.addItem(self.rect_item)
            self.rect_item.setZValue(25)
            self.points = [[scene_pos.x() * downsample, scene_pos.y() * downsample],
                           [scene_pos.x() * downsample + self.WIDTH, scene_pos.y() * downsample + self.HEIGHT]]

    def mouseMoveEvent(self, event, downsample):
        if self.DRAW_FLAG:
            scene_pos = self.view.mapToScene(event.pos())
            self.rect_item.setRect(scene_pos.x(), scene_pos.y(),
                               int(self.WIDTH / downsample), int(self.HEIGHT / downsample))
            self.points = [[scene_pos.x() * downsample, scene_pos.y() * downsample],
                           [scene_pos.x() * downsample + self.WIDTH, scene_pos.y() * downsample + self.HEIGHT]]


    def mouseReleaseEvent(self, event, downsample):
        if self.DRAW_FLAG:
            self.DRAW_FLAG = False
            # 确认最终的位置
            scene_pos = self.view.mapToScene(event.pos())
            self.rect_item.setRect(scene_pos.x(), scene_pos.y(),
                                   int(self.WIDTH / downsample), int(self.HEIGHT / downsample))
            # 绘制左上角的点，用于修改
            self.addCycle2Scene(scene_pos)
            self.points = [[scene_pos.x() * downsample, scene_pos.y() * downsample],
                           [scene_pos.x() * downsample + self.WIDTH, scene_pos.y() * downsample + self.HEIGHT]]

            # 记录下固定矩形的左上角，右下角在level=0时的坐标，颜色，类型
            color = list(self.COLOR.getRgb())
            type = self.TYPE

            # 记录下绘制的item
            annotaion_info = {"location": self.points,
                              "color": color,
                              "type": type,
                              "tool": "固定矩形",
                              'annotation_item': self.rect_item,
                              "control_point_items": self.control_point_items,}
            return annotaion_info
        return None

    # 当scene改变后，需要重新绘制当前绘制的这个形状
    def redraw(self, downsample, width=None):
        if self.DRAW_FLAG:
            self.rect_item = QGraphicsRectItem()
            if width is not None:
                self.pen.setWidth(width)
            self.rect_item.setPen(self.pen)

            start_x = self.points[0][0] / downsample
            start_y = self.points[0][1] / downsample
            self.rect_item.setRect(start_x, start_y,
                                   int(self.WIDTH / downsample), int(self.HEIGHT / downsample))
            self.rect_item.setZValue(25)
            # 重新将形状添加到视图中
            self.scene.addItem(self.rect_item)

    def draw(self, points, color, width, downsample, choosed=False):
        """
        :param points: 矩形顶点
        :param color: 颜色
        :param downsaple: 视图下采样倍率
        :return:
        """
        control_point_items = []
        rect_item = QGraphicsRectItem()
        pen = QPen()
        pen.setColor(color)
        pen.setWidth(width)
        rect_item.setPen(pen)
        x1, y1 = points[0][0] / downsample, points[0][1] / downsample
        x2, y2 = points[1][0] / downsample, points[1][1] / downsample
        rect_item.setRect(min(x1, x2), min(y1, y2), abs(x1 - x2), abs(y1 - y2))
        rect_item.setZValue(25)
        self.scene.addItem(rect_item)
        # 绘制控制点
        if choosed:
            cycle = self.scene.addEllipse(0, 0, 2*width, 2*width)
            cycle.setPos(QPoint(x1 - width, y1 - width))
            cycle.setPen(QPen(color))
            cycle.setBrush(QBrush(color))
            cycle.setZValue(30)
            control_point_items.append(cycle)
        return rect_item, control_point_items, None




