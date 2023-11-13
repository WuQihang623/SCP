import openslide
import numpy as np
from PyQt5.QtCore import QRectF
from function.vis_multi_channel import display_composite

class SlideHelper():
    def __init__(self, slide_path: str):
        self.slide_path = slide_path
        self.slide = openslide.open_slide(slide_path)
        self.level_downsamples = self.slide.level_downsamples
        self.level_dimensions = self.slide.level_dimensions
        self.level_count = self.slide.level_count
        try:
            self.mpp = float(self.slide.properties['openslide.mpp-x'])
        except:
            self.mpp = 0.25
        self.init_fluorescene()

    def get_slide_path(self):
        return self.slide_path

    def get_downsample_for_level(self, level):
        return self.level_downsamples[level]

    def get_level_dimension(self, level):
        return self.level_dimensions[level]

    def get_rect_for_level(self, level) -> QRectF:
        size_ = self.get_level_dimension(level)
        rect = QRectF(0, 0, size_[0], size_[1])
        return rect

    def get_max_level(self):
        return len(self.level_downsamples) - 1

    def get_levels(self):
        return list(range(self.level_count))

    def get_best_level_for_downsample(self, downsample):
        return self.slide.get_best_level_for_downsample(downsample)

    def get_overview(self, level, size):
        if self.is_fluorescene is False:
            return self.slide.read_region((0, 0), level, size)
        else:
            downsample = self.level_downsamples[level]
            show_num_markers = self.level_downsamples.count(downsample)
            slide_list = []
            for markers_idx in range(0, show_num_markers):
                level_i = self.get_markers_downsample_level(markers_idx, downsample)
                slide_image = self.slide.read_region((0, 0), level_i, size).convert('L')
                slide_list.append(np.array(slide_image, dtype=np.uint8))
            slide_image = np.stack(slide_list, axis=0)
            slide_image = display_composite(slide_image)
            return slide_image

    def read_region(self, location, level, size):
        return self.slide.read_region(location=location, level=level, size=size)

    def get_thumbnail(self, size):
        return self.slide.get_thumbnail(size)

    # 一下的内容为荧光图像添加
    def init_fluorescene(self):
        self.downsamples = list(set(self.level_downsamples))
        self.is_fluorescene = True if len(self.level_downsamples) > len(self.downsamples) else False
        if self.is_fluorescene:
            self.num_markers = (len(self.level_downsamples) - 1) // (len(self.downsamples) - 1)

    def get_markers_downsample_level(self, marker_idx, downsample):
        # marker_idx 只会是存在的
        level = self.level_downsamples.index(downsample)
        return level + marker_idx