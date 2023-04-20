import math
import time

import openslide
import numpy as np
from PyQt5.QtGui import QPixmap, QPainterPath, QPen, QColor
from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition, QRectF

from window.slide_window.utils.SlideHelper import SlideHelper
from window.utils.ContourItem import ContourPathItem


class RegionContourLoader(QThread):
    addContourItemSignal = pyqtSignal(ContourPathItem)
    removeItemSignal = pyqtSignal(ContourPathItem)
    def __init__(self, scene: QGraphicsScene):
        super(RegionContourLoader, self).__init__()

        # 初始化
        self.scene = scene

        # 用于保护线程中共享变量不回同时被两个线程读取
        self.mutex = QMutex()
        # 使线程在没有任务时暂停执行，并等待重新绘制的信号
        self.condition = QWaitCondition()
        # 当要显示或者关闭轮廓包括重新绘制轮廓时置为True
        self.restart = False
        # 当页面关闭时，要退出该线程
        self.abort = False

        self.contours = []
        self.colors = []
        self.types = []

    # 如果是要显示或者关闭某个类别的轮廓
    def load_contour(self, current_level, current_downsample, contours=None, colors=None, types=None, show_types=None, remove_types=None):
        """
        :param current_downsample: 当前scene的slide的downsample
        :param contours: 所有的区域轮廓列表
        :param colors: 轮廓的颜色列表
        :param types: 轮廓的类型列表，值为1~4
        :param show_types: 要绘制的轮廓类型
        :param remove_types: 要删除的轮廓类型
        :return:
        """
        # 如果当前正在执行线程，则停止

        # 定义一个函数来返回具有特定属性的对象的迭代器
        def find_matching_objects(lst, att_category, att_is_region, categorys):
            for obj in lst:
                if getattr(obj, att_category, None) in categorys and getattr(obj, att_is_region, None) is True:
                    yield obj

        if self.isRunning():
            self.restart = True
        self.current_level = current_level
        self.current_downsample = current_downsample
        self.contours = contours if contours is not None else []
        self.colors = colors if colors is not None else []
        self.types = types if types is not None else []
        self.show_types = show_types if show_types is not None else []

        # TODO: 如果点击了移除某个类型，则进行删除
        if remove_types is not None:
            match_items = find_matching_objects(self.scene.items(), 'category', 'is_region', remove_types)
            for item in match_items:
                self.removeItemSignal.emit(item)

        if self.isRunning():
            self.restart = True
            self.condition.wakeOne()
        # 如果线程没有在执行则开启线程
        else:
            self.start(QThread.NormalPriority)

    # 将所有的
    def run(self):
        while True:
            # 获取共享变量
            self.mutex.lock()
            current_downsample = self.current_downsample
            contours = self.contours
            colors = self.colors
            types = self.types
            show_types = self.show_types
            current_level = self.current_level
            self.mutex.unlock()

            if show_types is not None:
                for contour, color, type in zip(contours, colors, types):
                    if self.restart:
                        break
                    if self.abort:
                        return
                    if type in show_types:
                        # TODO:宽度随着视图缩放而改变
                        width = 4
                        pathItem = ContourPathItem(type, current_level)
                        path = QPainterPath()
                        pen = QPen()
                        pen.setColor(QColor(color[0], color[1], color[2]))
                        pen.setWidth(width)
                        pathItem.setPen(pen)
                        for idx, point in enumerate(contour):
                            if idx == 0:
                                path.moveTo(point[0] / current_downsample, point[1] / current_downsample)
                            else:
                                path.lineTo(point[0] / current_downsample, point[1] / current_downsample)
                        path.closeSubpath()
                        pathItem.setPath(path)
                        pathItem.setZValue(15)
                        self.addContourItemSignal.emit(pathItem)

            # 等待其他线程对self.restart的修改，等待重新载入tile
            self.mutex.lock()
            if not self.restart:
                self.condition.wait(self.mutex)
            self.restart = False
            self.mutex.unlock()

    def __del__(self):
        print('regionContourloader is del')
        self.mutex.lock()
        self.abort = True
        self.condition.wakeOne()
        self.mutex.unlock()
        self.wait()