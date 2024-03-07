import os
import json
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem
from PyQt5.QtCore import QObject, QPoint
from PyQt5.QtGui import QColor, QPen, QBrush

# 矩形工具的基类
class BaseTool(QObject):

    def __init__(self, scene: QGraphicsScene, view: QGraphicsView):
        super().__init__()
        self.scene = scene
        self.view = view

        self.COLOR = None  # 绘制的颜色
        self.TYPE = None  # 标注的类型
        self.DRAW_FLAG = False
        self.width = 1

    # 绘制时设置初始化(Rect)
    def initialize(self):
        self.DRAW_FLAG = True
        self.pen = QPen()
        self.pen.setColor(self.COLOR)
        self.pen.setWidth(self.width)
        self.rect_item = QGraphicsRectItem()
        self.rect_item.setPen(self.pen)
        self.control_point_items = []
        # 用于记录矩形框的左上角与右下角
        self.points = []

    def set_AnnotationColor(self, type, color):
        # 正在绘制时不能切换颜色
        if self.DRAW_FLAG:
            return
        self.TYPE = type
        self.COLOR = QColor(*color)

    # 在scene_pos绘制控制原点
    def addCycle2Scene(self, scene_pos):
        cycle = self.scene.addEllipse(0, 0, self.width*2, self.width*2)
        cycle.setPos(QPoint(scene_pos.x() - self.width, scene_pos.y() - self.width))
        cycle.setPen(QPen(self.COLOR))
        cycle.setBrush(QBrush(self.COLOR))
        cycle.setZValue(30)
        self.control_point_items.append(cycle)

    # 如果切换工具、切换子窗口，则停止绘制
    def stopDraw(self):
        try:
            if self.DRAW_FLAG:
                self.DRAW_FLAG = False
                self.scene.removeItem(self.rect_item)
                for item in self.control_point_items:
                    self.scene.removeItem(item)
        except:
            return