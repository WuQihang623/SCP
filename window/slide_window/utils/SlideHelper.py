import openslide
import numpy as np
from collections import Counter
from PyQt5.QtCore import QRectF
from function.vis_multi_channel import display_composite

class SlideHelper():
    def __init__(self, slide_path: str):
        self.slide_path = slide_path
        self.slide = openslide.open_slide(slide_path)
        self.level_downsamples = self.slide.level_downsamples
        self.level_dimensions = self.slide.level_dimensions
        self.level_count = self.slide.level_count
        self.fluorescene_color_list = []
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
        downsamples = np.array(self.slide.level_downsamples)
        downsamples = np.abs(downsamples - downsample)
        return int(np.argmin(downsamples))

    def get_overview(self, level, size, seleted_channels=None, channel_intensities=None):
        if self.is_fluorescene is False:
            return self.slide.read_region((0, 0), level, size)
        else:
            downsample = self.level_downsamples[level]
            show_num_markers = self.level_downsamples.count(downsample)
            show_num_markers = list(i for i in range(show_num_markers))
            if seleted_channels is not None:
                show_num_markers = list(set(show_num_markers) & set(seleted_channels))
            slide_list = []
            for markers_idx in show_num_markers:
                level_i = self.get_markers_downsample_level(markers_idx, downsample)
                slide_image = self.slide.read_region((0, 0), level_i, size).convert('L')
                slide_list.append(np.array(slide_image, dtype=np.uint8))
            slide_image = np.stack(slide_list, axis=0)
            slide_image = display_composite(slide_image, show_num_markers, channel_intensities)
            return slide_image

    def read_region(self, location, level, size):
        return self.slide.read_region(location=location, level=level, size=size)

    def get_thumbnail(self, size):
        return self.slide.get_thumbnail(size)

    # 一下的内容为荧光图像添加
    def init_fluorescene(self):
        self.downsamples = sorted(list(set(self.level_downsamples)))
        self.is_fluorescene = True if len(self.level_downsamples) > len(self.downsamples) else False
        if self.is_fluorescene:
            self.get_fluorescene_color()
            element_counts = Counter(self.level_downsamples)
            self.num_markers = max(element_counts.values())

    def get_markers_downsample_level(self, marker_idx, downsample):
        # marker_idx 只会是存在的
        level = self.level_downsamples.index(downsample)
        return level + marker_idx

    def get_fluorescene_color(self):
        import xml.etree.ElementTree as ET
        data = self.slide.properties
        keys = []
        for key, value in data.items():
            keys.append(key)
        print(keys)
        comment = data['openslide.comment']
        root = ET.fromstring(comment)
        for child in root:
            if child.tag == 'ScanProfile':
                for subchild in child:
                    if subchild.tag == 'root':
                        for subsubchild in subchild:
                            if subsubchild.tag == 'ScanColorTable':
                                for colorname in subsubchild:
                                    if colorname.tag == 'ScanColorTable-k':
                                        self.fluorescene_color_list.append(colorname.text.split('_')[0])
