import math

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsLineItem
from PyQt5.QtCore import QPoint, QObject, Qt
from PyQt5.QtGui import QColor, QPen, QFont, QBrush
from window.Tools import TranslucentTextItem
from window.Tools.BaseTool import BaseTool
from window.slide_window.utils.SlideHelper import SlideHelper

class MeasureTool(BaseTool):
    def __init__(self, scene: QGraphicsScene, view: QGraphicsView):
        super(MeasureTool, self).__init__(scene, view)
        self.mpp = 0.25

    def initialize(self):
        self.DRAW_FLAG = True

        self.pen = QPen()
        self.pen.setColor(self.COLOR)
        self.pen.setWidth(4)

        self.line_item = QGraphicsLineItem()
        self.line_item.setPen(self.pen)
        self.text_item = TranslucentTextItem()

        # 用于记录起点与终点
        self.points = []
        # 用于记录控制点
        self.control_point_items = []


    def mousePressEvent(self, event, downsample):
        if self.COLOR is not None:
            self.initialize()
            scene_pos = self.view.mapToScene(event.pos())
            point = [scene_pos.x() * downsample, scene_pos.y() * downsample]
            self.points.append(point)

            # 绘制起始控制点
            self.addCycle2Scene(scene_pos)
            self.line_item.setLine(scene_pos.x(), scene_pos.y(), scene_pos.x()+1, scene_pos.y()+1)
            self.last_point = [(scene_pos.x() + 1) * downsample, (scene_pos.y() + 1) * downsample]
            self.scene.addItem(self.line_item)
            self.scene.addItem(self.text_item)
            self.line_item.setZValue(25)
            self.line_item.setZValue(25)

    def drawLine(self, event, downsample):
        scene_pos = self.view.mapToScene(event.pos())
        # 获取起点
        start_x = self.points[0][0] / downsample
        start_y = self.points[0][1] / downsample
        # 绘制直线
        self.line_item.setLine(start_x, start_y, scene_pos.x(), scene_pos.y())
        # 记录当前的坐标点
        self.last_point = [(scene_pos.x()) * downsample, (scene_pos.y()) * downsample]
        return scene_pos, start_x, start_y

    def showText(self, distance, start_x, start_y, scene_pos):
        # 显示长度
        self.text_item.setPlainText(f"{distance:.2f}μm")
        self.text_item.setFont(QFont(" ", 12))
        self.text_item.setDefaultTextColor(Qt.black)
        # 设置文本位置
        self.text_item.setPos((start_x + scene_pos.x()) / 2,
                              (start_y + scene_pos.y()) / 2)


    def mouseMoveEvent(self, event, downsample):
        if self.DRAW_FLAG:
            scene_pos, start_x, start_y = self.drawLine(event, downsample)

            # 计算长度
            distance = self.measureDistance([start_x, start_y], scene_pos, downsample) * self.mpp
            self.showText(distance, start_x, start_y, scene_pos)

    def mouseReleaseEvent(self, event, downsample):
        if self.DRAW_FLAG:
            self.DRAW_FLAG = False
            scene_pos, start_x, start_y = self.drawLine(event, downsample)

            # 计算长度
            distance = self.measureDistance([start_x, start_y], scene_pos, downsample) * self.mpp
            if distance > 10:
                # 保留这个item
                self.showText(distance, start_x, start_y, scene_pos)
                # 添加终点的控制点
                self.addCycle2Scene(scene_pos)
                self.points.append([scene_pos.x() * downsample, scene_pos.y() * downsample])
                color = list(self.COLOR.getRgb())
                type = self.TYPE
                # 记录下绘制的item
                annotataion_info = {
                    "location": self.points,
                    "color": color,
                    'tool': "测量工具",
                    "type": type,
                    "distance": distance,
                    'annotation_item': self.line_item,
                    'text_item': self.text_item,
                    "control_point_items": self.control_point_items
                }
                return annotataion_info

            else:
                # 删除绘制的item
                self.scene.removeItem(self.line_item)
                self.scene.removeItem(self.text_item)
                for item in self.control_point_items:
                    self.scene.removeItem(item)
        return None

    def redraw(self, downsample, width=None):
        if self.DRAW_FLAG:
            if width is not None:
                self.pen.setWidth(width)
            self.line_item = QGraphicsLineItem()
            self.line_item.setPen(self.pen)
            self.text_item = TranslucentTextItem()

            # 初始的位置
            start_x = self.points[0][0] / downsample
            start_y = self.points[0][1] / downsample

            end_x = self.last_point[0] / downsample
            end_y = self.last_point[1] / downsample

            # 绘制控制点, 由于是修改control_point_item, 因此不能使用self.addCycle2Scene
            cycle = self.scene.addEllipse(0, 0, 8, 8)
            cycle.setPos(QPoint(start_x - 4, start_y - 4))
            cycle.setPen(QPen(self.COLOR))
            cycle.setBrush(QBrush(self.COLOR))
            cycle.setZValue(30)
            self.control_point_items = [cycle]

            self.line_item.setLine(start_x, start_y, end_x, end_y)
            self.line_item.setZValue(25)
            self.scene.addItem(self.line_item)


    def stopDraw(self):
        if self.DRAW_FLAG:
            self.DRAW_FLAG = False
            try:
                self.scene.removeItem(self.line_item)
                self.scene.removeItem(self.text_item)
                for item in self.control_point_items:
                    self.scene.removeItem(item)
            except:
                return

    def draw(self, points, distance, color, width, text_width, downsample, choosed=False):
        control_point_items = []
        lineItem = QGraphicsLineItem()
        pen = QPen()
        pen.setColor(color)
        pen.setWidth(width)
        lineItem.setPen(pen)

        start_x = points[0][0] / downsample
        start_y = points[0][1] / downsample

        end_x = points[1][0] / downsample
        end_y = points[1][1] / downsample

        lineItem.setLine(start_x, start_y, end_x, end_y)
        self.scene.addItem(lineItem)
        lineItem.setZValue(25)

        # 显示距离
        text_item = TranslucentTextItem()
        self.scene.addItem(text_item)
        text_item.setPlainText(f"{distance:.2f}μm")
        text_item.setFont(QFont("宋体", text_width))
        text_item.setDefaultTextColor(Qt.black)
        # 设置文本位置
        text_item.setPos((start_x + end_x) / 2,
                         (start_y + end_y) / 2)
        text_item.setZValue(25)

        # 绘制控制点
        if choosed:
            control_points = [[start_x, start_y], [end_x, end_y]]
            for i in range(2):
                cycle = self.scene.addEllipse(0, 0, 2 * width, 2 * width)
                cycle.setPos(QPoint(control_points[i][0] - width, control_points[i][1] - width))
                cycle.setPen(QPen(color))
                cycle.setBrush(QBrush(color))
                cycle.setZValue(30)
                control_point_items.append(cycle)

        return lineItem, control_point_items, text_item

    def measureDistance(self, pos1, pos2, downsample):
        x1 = pos1[0] * downsample
        y1 = pos1[1] * downsample
        x2 = pos2.x() * downsample
        y2 = pos2.y() * downsample
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def set_mpp(self, mpp):
        self.mpp = mpp