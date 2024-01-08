import numpy as np
from PyQt5.QtWidgets import QGraphicsScene
from window.utils.ContourItem import TriangleItem


class NucleusMarkLoader():
    def __init__(self, scene: QGraphicsScene):
        super(NucleusMarkLoader, self).__init__()
        # 初始化
        self.scene = scene

        # 初始化上一次的level
        self.last_level = -1
        self.last_nucleus = None

    def load_nucleus_mark(self, current_rect,
                                current_level,
                                current_downsample,
                                centers,
                                nucleus_marks,
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
            self.last_nucleus = None

        self.current_rect = current_rect
        self.current_level = current_level
        self.current_downsample = current_downsample
        self.centers = centers
        self.nucleus_marks = nucleus_marks
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
        if self.show_types is None or self.centers is None or self.nucleus_marks is None:
            return
        if self.current_downsample <= 2:
            step = 1
        else:
            step = int(self.current_downsample * 2)
        # 计算当前画面中的细胞
        show_nucleus = self.get_current_rect_nuclei(current_rect=self.current_rect,
                                                   current_level=self.current_level,
                                                   current_downsample=self.current_downsample,
                                                   centers=self.centers[::step],
                                                   last_level=self.last_level,
                                                   last_nucleus=self.last_nucleus)
        for center, mark in zip (self.centers[::step][show_nucleus], self.nucleus_marks[::step][show_nucleus]):
            if mark in self.show_types:
                self.draw_triangle(center, mark, current_level=self.current_level, current_downsample=self.current_downsample)

    def get_current_rect_nuclei(self, current_rect, current_level, current_downsample, centers, last_level, last_nucleus):
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

        current_nuclues = centers[:, 0] > top_left_x
        current_nuclues = current_nuclues * (centers[:, 0] < bottom_right_x)
        current_nuclues = current_nuclues * (centers[:, 1] > top_left_y)
        current_nuclues = current_nuclues * (centers[:, 1] < bottom_right_y)

        if self.current_level == self.last_level:
            if self.last_nucleus is None:
                show_nuclei = current_nuclues
                self.last_nucleus = current_nuclues
            else:
                show_nuclei = np.int8(current_nuclues) - np.int8(last_nucleus)
                show_nuclei = show_nuclei > 0
                self.last_nucleus = np.logical_or(show_nuclei, current_nuclues)
        else:
            show_nuclei = current_nuclues
            self.last_nucleus = current_nuclues
            self.last_level = current_level
        return show_nuclei

    def draw_triangle(self, center, mark, current_level, current_downsample):
        """ 显示出FP，FN的细胞核
            Args:
                center: x, y
                mark: FP or FN
                current_level: 当前slide的level, 用于标识item
                current_downsample: 当前的下采样倍数
        """
        color = self.color_dict["mark"]
        triangle = TriangleItem(x=center[0] / current_downsample, y=center[1] / current_downsample, color=color,
                                category=mark, level=current_level)
        triangle.setZValue(35)
        self.scene.addItem(triangle)

    def __del__(self):
        print("nucleiContourloader is del")
        if hasattr(self, "contours"):
            del self.contours
        if hasattr(self, "centers"):
            del self.centers
        if hasattr(self, "types"):
            del self.types
