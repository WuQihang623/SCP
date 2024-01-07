import os
import json
import math
from numbers import Number
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsLineItem, QGraphicsPathItem
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPen, QBrush, QPainterPath
from window.slide_window.Tools.BaseTool import BaseTool


class DrawPolygon(BaseTool):
    PolygonClosureSignal = pyqtSignal(dict, float)
    def __init__(self, scene: QGraphicsScene, view: QGraphicsView):
        super(DrawPolygon, self).__init__(scene, view)
        self.CONTINUE_FLAG = False
        self.CLOSE_FLAG = False
        self.CLOSE_CYCLE_COLOR = [255, 255, 0, 255]

    # 初始化
    def initialize(self):
        self.DRAW_FLAG = True

        self.pen = QPen()
        self.pen.setColor(self.COLOR)
        self.pen.setWidth(4)
        self.PathItem = QGraphicsPathItem()
        self.path = QPainterPath()
        self.PathItem.setPen(self.pen)
        # 用于记录多边形顶点的Item
        self.control_point_items = []
        # 用于记录多边形的顶点
        self.points = []

        # 可以用来绘制任意线条，包括水平线、垂直线、斜线等
        self.line_item = QGraphicsLineItem()
        self.line_item.setPen(self.pen)

        # 提示close polygon的点
        self.close_cycle_items = []

    def continueDrawLine(self, scene_pos, downsample):
        # 将路径的终点设置为当前鼠标的位置
        self.path.lineTo(scene_pos)
        self.PathItem.setPath(self.path)
        point = [scene_pos.x() * downsample, scene_pos.y() * downsample]
        # 记录标注的位置
        self.points.append(point)
        # 添加控制点
        self.addCycle2Scene(scene_pos)

    def mousePressEvent(self, event, downsample):
        if self.COLOR is not None:
            # 如果是绘制多边形的第一个点，则需要初始化
            if not self.DRAW_FLAG:
                self.initialize()
            # 长按鼠标左键则打开连续绘制功能
            self.CONTINUE_FLAG = True

            # 将可见范围的x,y坐标转换成在整张图中的坐标
            scene_pos = self.view.mapToScene(event.pos())
            self.last_line_point = [scene_pos.x() * downsample, scene_pos.y() * downsample]

            # 查看是否为第一个点
            if self.points == []:
                # 将路径的起点设置为鼠标的位置
                self.path.moveTo(scene_pos)
                # 将路径添加到场景中
                self.scene.addItem(self.PathItem)
                self.PathItem.setZValue(25)

                # 绘制直线
                self.line_item.setLine(scene_pos.x(), scene_pos.y(), scene_pos.x()+1, scene_pos.y()+1)
                self.scene.addItem(self.line_item)
                self.line_item.setZValue(25)
                point = [scene_pos.x() * downsample, scene_pos.y() * downsample]
                self.points.append(point)

                # 绘制控制点
                self.addCycle2Scene(scene_pos)

            # 闭合曲线
            elif self.CLOSE_FLAG:
                self.path.closeSubpath()
                self.PathItem.setPath(self.path)
                self.DRAW_FLAG = False
                self.CONTINUE_FLAG = False
                self.CLOSE_FLAG = False
                self.scene.removeItem(self.line_item)

                # 删除闭合提示点
                if hasattr(self, 'close_cycle'):
                    if self.scene.clear_flag is False:
                        self.scene.removeItem(self.close_cycle)
                    else:
                        self.scene.clear_flag = False
                    del self.close_cycle


                # 发送该标注信号
                color = list(self.COLOR.getRgb())
                type = self.TYPE
                annotation_info = {
                    "location": self.points,
                    "color": color,
                    'tool': "多边形",
                    "type": type,
                    'annotation_item': self.PathItem,
                    "control_point_items": self.control_point_items
                }
                self.PolygonClosureSignal.emit(annotation_info, downsample)

            else:
                self.continueDrawLine(scene_pos, downsample)

    def mouseMoveEvent(self, event, downsample):
        if self.DRAW_FLAG:
            scene_pos = self.view.mapToScene(event.pos())
            last_point = self.points[-1]  # 当一个顶点在level=0下的坐标
            # 上一个顶点在当前场景的坐标
            last_pos = [last_point[0] / downsample, last_point[1] / downsample]
            # 如果是连续绘制，则需要判断移动的距离是否大于15，是的话就记录该点并绘制控制点
            if self.CONTINUE_FLAG:
                distance = self.mearsureDistance(last_pos, scene_pos)
                # 距离大于10，则记录当前鼠标位置为顶点
                if distance > 10:
                    self.continueDrawLine(scene_pos, downsample)
                    return

            # 如果没有记录多边形顶点，则让直线终点指向鼠标坐标
            self.line_item.setLine(last_pos[0], last_pos[1], scene_pos.x(), scene_pos.y())
            self.last_line_point = [scene_pos.x() * downsample, scene_pos.y() * downsample]

            """判断当前的鼠标坐标是否接近与起始坐标"""
            if len(self.points )> 2:
                start_point = self.points[0]
                start_pos = [start_point[0] / downsample, start_point[1] / downsample]
                distance = self.mearsureDistance(start_pos, scene_pos)
                # 如果与初始距离小于5，则将CLOSE_FLAG设置为True
                if distance < 5:
                    self.CLOSE_FLAG = True
                    # 绘制终点指示
                    if not hasattr(self, 'close_cycle'):
                        self.close_cycle = self.scene.addEllipse(0, 0, 10, 10)
                        self.close_cycle.setPos(QPoint(start_pos[0] - 5, start_pos[1] - 5))
                        color = QColor(*self.CLOSE_CYCLE_COLOR)
                        self.close_cycle.setPen(QPen(color))
                        self.close_cycle.setBrush(QBrush(color))
                        self.close_cycle.setZValue(35)
                    # 如果scene被clear了，那么终点位置还是要重画
                    elif self.scene.clear_flag:
                        self.close_cycle = self.scene.addEllipse(0, 0, 10, 10)
                        self.close_cycle.setPos(QPoint(start_pos[0] - 5, start_pos[1] - 5))
                        color = QColor(*self.CLOSE_CYCLE_COLOR)
                        self.close_cycle.setPen(QPen(color))
                        self.close_cycle.setBrush(QBrush(color))
                        self.close_cycle.setZValue(35)
                        self.scene.clear_flag = False
                # 如果距离大于5，则把之前绘制的close_cycle删除了
                else:
                    self.CLOSE_FLAG = False
                    if hasattr(self, 'close_cycle'):
                        print('delete1')
                        if self.scene.clear_flag is False:
                            print('delete2')
                            self.scene.removeItem(self.close_cycle)
                        else:
                            self.scene.clear_flag = False
                        del self.close_cycle

    # 释放鼠标时就不能连续绘制
    def mouseReleaseEvent(self, *args):
        self.CONTINUE_FLAG = False
        return

    def redraw(self, downsample, width=None):
        if self.DRAW_FLAG:
            if width is not None:
                self.pen.setWidth(width)
            self.PathItem = QGraphicsPathItem()
            self.path = QPainterPath()
            self.PathItem.setPen(self.pen)
            self.line_item = QGraphicsLineItem()
            self.line_item.setPen(self.pen)

            # 重新绘制线条
            for idx, point in enumerate(self.points):
                # 绘制path
                if idx == 0:
                    self.path.moveTo(QPoint(point[0] / downsample, point[1] / downsample))
                    self.scene.addItem(self.PathItem)
                    self.PathItem.setZValue(25)
                else:
                    self.path.lineTo(QPoint(point[0] / downsample, point[1] / downsample))
                    self.PathItem.setPath(self.path)

                # 绘制控制点
                cycle = self.scene.addEllipse(0, 0, 8, 8)
                cycle.setPos(QPoint(point[0] / downsample - 4, point[1] / downsample - 4))
                cycle.setPen(QPen(self.COLOR))
                cycle.setBrush(QBrush(self.COLOR))
                cycle.setZValue(30)
                self.control_point_items[idx] = cycle

            last_point = self.points[-1]  # 当一个顶点在level=0下的坐标
            # 上一个顶点在当前场景的坐标
            last_pos = [last_point[0] / downsample, last_point[1] / downsample]
            last_line_pos = [self.last_line_point[0] / downsample, self.last_line_point[1] / downsample]
            self.line_item.setLine(last_pos[0], last_pos[1],last_line_pos[0], last_line_pos[1])
            self.line_item.setZValue(25)
            self.scene.addItem(self.line_item)

    def draw(self, points, color, width, downsample, choosed=False):
        control_point_items = []
        pathItem = QGraphicsPathItem()
        path = QPainterPath()
        pen = QPen()
        pen.setColor(color)
        pen.setWidth(width)
        pathItem.setPen(pen)
        for idx, point in enumerate(points):
            # 计算当前点在scene中的位置
            current_x = point[0] / downsample
            current_y = point[1] / downsample
            qpoint = QPoint(current_x, current_y)
            if idx == 0:
                path.moveTo(qpoint)
            else:
                path.lineTo(qpoint)
            if choosed:
                cycle = self.scene.addEllipse(0, 0, 2 * width, 2 * width)
                cycle.setPos(QPoint(current_x - width, current_y - width))
                cycle.setPen(QPen(color))
                cycle.setBrush(QBrush(color))
                cycle.setZValue(30)
                control_point_items.append(cycle)
        # 闭合曲线
        path.closeSubpath()
        pathItem.setPath(path)
        pathItem.setZValue(25)
        self.scene.addItem(pathItem)

        return pathItem, control_point_items, None


    # 切换工具与切换模式都要执行
    def stopDraw(self):
        if self.DRAW_FLAG:
            self.DRAW_FLAG = False
            self.CONTINUE_FLAG = False
            try:
                self.scene.removeItem(self.line_item)
                self.scene.removeItem(self.PathItem)
                for item in self.control_point_items:
                    self.scene.removeItem(item)
            except:
                return

    def mearsureDistance(self, pos1, pos2):
        x1 = pos1[0]
        y1 = pos1[1]
        x2 = pos2.x()
        y2 = pos2.y()
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)