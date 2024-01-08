import numpy as np
from PyQt5.QtGui import QPainterPath, QPen, QColor, QBrush
from PyQt5.QtWidgets import QGraphicsScene
from window.utils.ContourItem import ContourPathItem, EllipseItem, TriangleItem

class NucleiContourLoader():
    def __init__(self, scene: QGraphicsScene):
        super(NucleiContourLoader, self).__init__()
        # 初始化
        self.scene = scene

        # 初始化上一次的level
        self.last_level = -1
        self.last_nuclei = None
        self.contours = None

    def load_contour(self, current_rect,
                     current_level,
                     current_downsample,
                     contours,
                     centers,
                     types,
                     color_dict=None,
                     show_types=None,
                     remove_types=None):

        def find_matching_objects(lst, att_category, att_is_region, categorys):
            """
                定义一个函数来返回具有特定属性的对象的迭代器
            """
            for obj in lst:
                if getattr(obj, att_category, None) in categorys and getattr(obj, att_is_region, None) is False:
                    yield obj

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
        if remove_types is not None and remove_types is not set([]):
            match_items = find_matching_objects(self.scene.items(), 'category', 'is_region', remove_types)
            for item in match_items:
                self.scene.removeItem(item)
        self.run()

    def run(self):
        if self.show_types is None or self.contours is None or self.types is None or self.centers is None:
            return
        if self.current_downsample <= 2:
            step = 1
        else:
            step = int(self.current_downsample * 2)
        # 计算当前画面中的细胞
        show_nuclei = self.get_current_rect_nuclei(current_rect=self.current_rect,
                                                   current_level=self.current_level,
                                                   current_downsample=self.current_downsample,
                                                   centers=self.centers[::step],
                                                   last_level=self.last_level,
                                                   last_nuclei=self.last_nuclei)

        for contour, center, type in zip(self.contours[::step][show_nuclei], self.centers[::step][show_nuclei], self.types[::step][show_nuclei]):
            if type in self.show_types:
                # 绘制轮廓
                if self.current_level < 1:
                    self.draw_contour(contour, type, self.current_level, self.current_downsample)
                # 绘制点
                else:
                    self.draw_Ellipse(center, type, self.current_level, self.current_downsample)

    def get_current_rect_nuclei(self, current_rect, current_level, current_downsample, centers, last_level, last_nuclei):
        """
            获取当前视图下的细胞
        """
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
        self.scene.addItem(pathItem)


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
        self.scene.addItem(cycle)

    def __del__(self):
        print("nucleiContourloader is del")
        if hasattr(self, "contours"):
            del self.contours
        if hasattr(self, "centers"):
            del self.centers
        if hasattr(self, "types"):
            del self.types
