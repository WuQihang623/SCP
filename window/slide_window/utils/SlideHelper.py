import openslide
from PyQt5.QtCore import QRectF

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
        return self.slide.read_region((0, 0), level, size)

    def read_region(self, location, level, size):
        return self.slide.read_region(location=location, level=level, size=size)

    def get_thumbnail(self, size):
        return self.slide.get_thumbnail(size)