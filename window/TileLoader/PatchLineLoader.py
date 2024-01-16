from PyQt5.QtGui import QPainterPath, QPen, QColor
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition

from window.utils.ContourItem import LineItem


class PatchLineLoader(QThread):
    addLineItemSignal = pyqtSignal(LineItem)
    removeLineItemSignal = pyqtSignal(LineItem)
    def __init__(self, scene: QGraphicsScene):
        super(PatchLineLoader, self).__init__()

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

        self.dimension_X = None
        self.dimension_Y = None
        self.current_level = None
        self.current_downsample = None
        self.patch_size = None
        self.stride = None
        self.opacity = None
        self.show = False

    def set_opacity(self, opacity):
        def find_matching_objects(lst, att_category, att_is_region, category="Line"):
            for obj in lst:
                if getattr(obj, att_category, None) is category and getattr(obj, att_is_region, None) is False:
                    yield obj

        match_items = find_matching_objects(self.scene.items(), 'category', 'is_region')
        for item in match_items:
            item.setOpacity(opacity/255)

    # 如果是要显示或者关闭某个类别的轮廓
    def load_line(self, dimension_X, dimension_Y, current_level, current_downsample, patch_size=None, stride=None, Opacity=None, show=False):
        # 如果当前正在执行线程，则停止

        # 定义一个函数来返回具有特定属性的对象的迭代器
        def find_matching_objects(lst, att_category, att_is_region, category="Line"):
            for obj in lst:
                if getattr(obj, att_category, None) is category and getattr(obj, att_is_region, None) is False:
                    yield obj

        match_items = find_matching_objects(self.scene.items(), 'category', 'is_region')
        for item in match_items:
            self.removeLineItemSignal.emit(item)

        self.show = show
        if self.isRunning():
            self.restart = True
        if self.show is False:
            return

        self.dimension_X = dimension_X
        self.dimension_Y = dimension_Y
        self.current_level = current_level
        self.current_downsample = current_downsample
        self.patch_size = patch_size if patch_size is not None else self.patch_size
        self.stride = stride if stride is not None else self.stride
        self.opacity = Opacity if Opacity is not None else self.opacity

        if self.patch_size is None:
            return
        if self.isRunning():
            self.restart = True
            self.condition.wakeOne()
        # 如果线程没有在执行则开启线程
        else:
            self.start(QThread.NormalPriority)

    # 将所有的轮廓进行绘制
    def run(self):
        while True:
            # 获取共享变量
            self.mutex.lock()
            current_downsample = self.current_downsample
            patch_size = int(self.patch_size / current_downsample)
            stride = int(self.stride / current_downsample)
            opacity = self.opacity
            dimension_X = int(self.dimension_X / current_downsample)
            dimension_Y = int(self.dimension_Y / current_downsample)
            current_level = self.current_level
            self.mutex.unlock()

            color = [0, 0, 0, opacity]
            x_list = [x for x in range(0, dimension_X, stride)]
            y_list = [y for y in range(0, dimension_Y, stride)]

            for x in x_list:
                if self.restart:
                    break
                if self.abort:
                    return
                lineItem = LineItem(x, 0, x, dimension_Y, color, level=current_level)
                self.addLineItemSignal.emit(lineItem)
                if patch_size != stride:
                    lineItem = LineItem(x+patch_size, 0, x+patch_size, dimension_Y, color=color, level=current_level)
                    self.addLineItemSignal.emit(lineItem)
            for y in y_list:
                if self.restart:
                    break
                if self.abort:
                    return
                lineItem = LineItem(0, y, dimension_X, y, color, level=current_level)
                self.addLineItemSignal.emit(lineItem)
                if patch_size != stride:
                    lineItem = LineItem(0, y+patch_size, dimension_X, y+patch_size, color, level=current_level)
                    self.addLineItemSignal.emit(lineItem)

            # 等待其他线程对self.restart的修改，等待重新载入tile
            self.mutex.lock()
            if not self.restart:
                self.condition.wait(self.mutex)
            self.restart = False
            self.mutex.unlock()

    def __del__(self):
        self.mutex.lock()
        self.abort = True
        self.condition.wakeOne()
        self.mutex.unlock()
        self.wait()