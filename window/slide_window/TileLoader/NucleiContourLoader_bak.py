import math
import time

import openslide
import numpy as np
from PyQt5.QtGui import QPixmap, QPainterPath, QPen, QColor, QBrush
from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition, QRectF

from window.slide_window.utils.SlideHelper import SlideHelper
from window.utils.ContourItem import ContourPathItem, EllipseItem

class NucleiContourLoader(QThread):
    addContourItemSignal = pyqtSignal(object)
    removeItemSignal = pyqtSignal(object)
    def __init__(self, scene: QGraphicsScene):
        super(NucleiContourLoader, self).__init__()
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

        # 初始化上一次的level
        self.last_level = -1
        self.last_nuclei = None

        self.contours = None

    def load_contour(self, current_rect,
                     current_level,
                     current_downsample,
                     contours, centers,
                     types, color_dict=None,
                     show_types=None,
                     remove_types=None):
        print(current_level, self.last_level)

        if self.isRunning() and self.contours is not None:
            self.restart = True
            # 如果是level改变了，则要重新加载细胞
            if self.last_level != current_level:
                self.last_level = -1
                self.last_nuclei = None

        self.current_rect = current_rect
        self.current_level = current_level
        self.current_downsample = current_downsample
        self.contours = contours
        self.centers = centers
        self.types = types
        self.show_types = show_types
        self.remove_types = remove_types
        self.color_dict = color_dict if color_dict is not None else self.color_dict

        # 如果点击了移除某个类型，则进行删除
        if remove_types is not None:
            for item in self.scene.items():
                if hasattr(item, 'category'):
                    if item.category in remove_types and item.is_region is False:
                        self.removeItemSignal.emit(item)

        if self.isRunning() and self.contours is not None:
            self.restart = True
            # 如果是level改变了，则要重新加载细胞
            if self.last_level != current_level:
                self.last_level = -1
                self.last_nuclei = None
            self.condition.wakeOne()
        # 如果线程没有在执行则开启线程
        else:
            self.start(QThread.HighPriority)

    def run(self):
        while True:
            # 获取共享变量
            self.mutex.lock()
            current_rect = self.current_rect
            current_level = self.current_level
            current_downsample = int(self.current_downsample)
            contours = self.contours
            centers = self.centers
            types = self.types
            show_types = self.show_types
            last_level = self.last_level
            last_nuclei = self.last_nuclei
            self.mutex.unlock()

            if show_types is not None and contours is not None:
                if current_downsample <= 2:
                    step = 1
                else:
                    step = int(current_downsample * 2)
                # 计算当前画面中的细胞
                show_nuclei = self.get_current_rect_nuclei(current_rect=current_rect,
                                                           current_level=current_level,
                                                           current_downsample=current_downsample,
                                                           centers=centers[::step],
                                                           last_level=last_level,
                                                           last_nuclei=last_nuclei)
                for contour, center, type in zip(contours[::step][show_nuclei], centers[::step][show_nuclei], types[::step][show_nuclei]):
                    if self.restart:
                        break
                    if self.abort:
                        return
                    if type in show_types:
                        # 绘制轮廓
                        if current_level < 1:
                            self.draw_contour(contour, type, current_level, current_downsample)
                        # 绘制点
                        else:
                            self.draw_Ellipse(center, type, current_level, current_downsample)

            # 等待其他线程对self.restart的修改，等待重新载入tile
            self.mutex.lock()
            if not self.restart:
                self.condition.wait(self.mutex)
            self.restart = False
            self.mutex.unlock()


    # 获取当前视图下的细胞
    def get_current_rect_nuclei(self, current_rect, current_level, current_downsample, centers,
                                last_level, last_nuclei):
        current_rect = current_rect.getRect()
        top_left_x = current_rect[0] * current_downsample
        top_left_x = 0 if top_left_x < 0 else top_left_x
        top_left_y = current_rect[1] * current_downsample
        top_left_y = 0 if top_left_y < 0 else top_left_y
        bottom_right_x = (current_rect[0] + current_rect[2]) * current_downsample
        bottom_right_y = (current_rect[1] + current_rect[3]) * current_downsample

        current_nuclei = centers[:, 0] > top_left_x
        current_nuclei = current_nuclei * (centers[:, 0] < bottom_right_x)
        current_nuclei = current_nuclei * (centers[:, 1] > top_left_y)
        current_nuclei = current_nuclei * (centers[:, 1] < bottom_right_y)

        if self.current_level == self.last_level:
            if self.last_nuclei is None:
                show_nuclei = current_nuclei
                self.last_nuclei = current_nuclei
            else:
                show_nuclei = np.int8(current_nuclei) - np.int8(last_nuclei)
                show_nuclei = show_nuclei > 0
                self.last_nuclei = np.logical_or(show_nuclei, current_nuclei)
        else:
            show_nuclei = current_nuclei
            self.last_nuclei = current_nuclei
            self.last_level = current_level
        return show_nuclei

    # 绘制轮廓
    def draw_contour(self, contour, type, current_level, current_downsample):
        width = 3
        color = QColor(*self.color_dict[int(type)])
        pathItem = ContourPathItem(type, current_level, False)
        path = QPainterPath()
        pen = QPen()
        pen.setColor(color)
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


    def draw_Ellipse(self, center, type, current_level, current_downsample):
        width = 3
        color = QColor(*self.color_dict[int(type)])
        pen = QPen()
        pen.setColor(color)
        pen.setWidth(width)
        cycle = EllipseItem(0, 0, 2*width, 2* width, type, current_level)
        cycle.setPos(center[0] / current_downsample - width, center[1] / current_downsample - width)
        cycle.setPen(pen)
        cycle.setBrush(QBrush(color))
        cycle.setZValue(15)
        self.addContourItemSignal.emit(cycle)

    def __del__(self):
        print('nucleiContourloader is del')
        self.mutex.lock()
        self.abort = True
        self.condition.wakeOne()
        self.mutex.unlock()
        self.wait()