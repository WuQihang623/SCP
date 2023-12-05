import math

import numpy as np
from PyQt5.QtGui import QPixmap
from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition, QRectF
from function.heatmap_background import get_colormap_background
from window.slide_window.TileLoader.GraphicsTile import GraphicsTile
from window.slide_window.utils.SlideHelper import SlideHelper
from function.colorspace_transform import colordeconvolution, normalizeStaining, ndarray_to_pixmap

class TileManager(QThread):
    addTileItemSignal = pyqtSignal(GraphicsTile)
    def __init__(self, scene: QGraphicsScene, slide_helper: SlideHelper, tile_size=1024, heatmap_alpha=0.3):
        super(TileManager, self).__init__()
        # 初始化变量
        self.scene = scene
        self.slide_helper = slide_helper
        self.tile_size = tile_size

        # 用于保护线程中共享变量不回同时被两个线程读取
        self.mutex = QMutex()
        # 使线程在没有任务时暂停执行，并等待 load_tiles_for_view() 方法发出的信号来通知有新的任务需要执行
        self.condition = QWaitCondition()

        # 已经加载的当前level的图像块的左上角坐标（在当前level下的坐标）
        self.loaded_tile_rect = []
        # 已经加载的当前level的图像块（GraphicsTile）
        self.loaded_tileItem = []
        # 已经加载的当前level的heatmap（GraphicsTile）
        self.loaded_heatmapItem = []
        # 加载每个level的tile的坐标（x,y,w,h)
        self.tile_rects = self.slice_rect()

        # 当前视图的坐标信息
        self.top_left_x = None
        self.top_left_y = None
        self.bottom_right_x = None
        self.bottom_right_y = None
        self.level = None
        self.downsample = None
        self.heatmap = None
        self.heatmap_downsample = None
        self.heatmap_alpha = heatmap_alpha

        # 图像颜色空间
        if self.slide_helper.is_fluorescene is False:
            self.colorspace = 0
        else:
            self.colorspace = [i for i in range(self.slide_helper.num_markers)]

        # 加载背景图像，背景图像用于等待显示，当该区域的tile没加载出来时显示这个背景图像
        expected_bg_area = 2048 * 1080
        max_slide_area = self.slide_helper.level_dimensions[0][0] * self.slide_helper.level_dimensions[0][1]
        downsample = int(math.sqrt(max_slide_area / expected_bg_area))
        self.backgroud_level = self.slide_helper.get_best_level_for_downsample(downsample)
        self.background_dimension = self.slide_helper.get_level_dimension(self.backgroud_level)
        self.background_image_pil = self.slide_helper.get_overview(self.backgroud_level, self.background_dimension, self.colorspace)
        self.background_image = ImageQt(self.background_image_pil)
        self.background_image = QPixmap.fromImage(self.background_image)
        self.background_image_downsample = self.slide_helper.get_downsample_for_level(self.backgroud_level)
        self.heatmap_background_image = None
        self.background_image_h = None
        self.background_image_d = None
        self.background_stainNorm = None

        """
        当self.background_flag==True时表示background_image还未载入到Scene中
        当self.background_flag==False时表示background_image已经载入到Scene中
        载入了background_image后就应该载入tile
        """
        self.background_flag = True
        # 当移动视图后，需要加载其他区域的缓存图像，设置True，暂停加载当前区域
        self.restart = False
        # 当页面关闭时，要退出该线程
        self.abort = False

    # 当执行了载入操作才执行
    def run(self):
        while True:
            # 获取共享变量
            self.mutex.lock()
            tile_rects = self.tile_rects
            top_left_x = self.top_left_x
            top_left_y = self.top_left_y
            bottom_right_x = self.bottom_right_x
            bottom_right_y = self.bottom_right_y
            level = self.level
            downsample = self.downsample
            heatmap_downsample = self.heatmap_downsample
            heatmap = self.heatmap
            colorspace = self.colorspace
            heatmap_alpha = self.heatmap_alpha
            self.mutex.unlock()
            for tile_rect in tile_rects[level]:
                if self.restart:
                    break
                if self.abort:
                    return
                # 如果该图像块已经被载入，则跳过
                if tile_rect in self.loaded_tile_rect:
                    continue
                x = tile_rect[0]
                y = tile_rect[1]

                """
                将存在与目前这个视图的tile的坐标读取出来
                top_left的坐标是已经减去self.tile_size的
                """
                if x >= top_left_x and y >= top_left_y:
                    if x <= bottom_right_x and y <= bottom_right_y:
                        self.addTileItem(tile_rect, level, downsample, heatmap, heatmap_downsample, colorspace, heatmap_alpha)

            # 等待其他线程对self.restart的修改，等待重新载入tile
            self.mutex.lock()
            if not self.restart:
                self.condition.wait(self.mutex)
            self.restart = False
            self.mutex.unlock()

    # 将item读出来并添加到视图中,并且加到缓存池中
    def addTileItem(self, tile_rect, level, downsample, heatmap, heatmap_downsample, colorspace, heatmap_alpha):
        item = GraphicsTile(self.slide_helper, tile_rect, self.slide_helper.get_slide_path(),
                            level, downsample, heatmap, heatmap_downsample, colorspace, heatmap_alpha)
        if heatmap is None:
            self.loaded_tileItem.append([item.level, item.x_y_w_h, item.pixmap])
            # 缓存池中一共有150个图像块
            if len(self.loaded_tileItem) > 150:
                del self.loaded_tileItem[0]
        else:
            self.loaded_heatmapItem.append([item.level, item.x_y_w_h, item.pixmap])
            if len(self.loaded_heatmapItem) > 150:
                del self.loaded_heatmapItem[0]
        item.setPos(tile_rect[0], tile_rect[1])

        if not self.restart:
            self.loaded_tile_rect.append(tile_rect)
            # TODO: 将tile添加到scene中
            self.addTileItemSignal.emit(item)

    # 每次缩放场景都会添加这个背景
    def addBackgroundItem(self):
        if self.heatmap is None:
            if self.slide_helper.is_fluorescene is False:
                if self.colorspace == 0:
                    background = QGraphicsPixmapItem(self.background_image)
                elif self.colorspace == 1:
                    background = QGraphicsPixmapItem(self.background_image_h)
                elif self.colorspace == 2:
                    background = QGraphicsPixmapItem(self.background_image_d)
                else:
                    background = QGraphicsPixmapItem(self.background_stainNorm)
            else:
                background = QGraphicsPixmapItem(self.background_image)
            scale = self.background_image_downsample / self.slide_helper.get_downsample_for_level(self.level)
        else:
            background = QGraphicsPixmapItem(self.heatmap_background_image)
            scale = self.heatmap_background_downsample / self.slide_helper.get_downsample_for_level(self.level)
        background.setScale(scale)
        self.scene.addItem(background)
        self.background_flag = False
        return

    # 加载背景热图
    def update_heatmap_background(self, heatmap_background, heatmap_alpha=0.3):
        self.heatmap_alpha = heatmap_alpha
        if isinstance(heatmap_background, QPixmap):
            self.heatmap_background_image = heatmap_background
            self.heatmap_background_downsample = self.slide_helper.level_dimensions[0][0] / heatmap_background.size().width()
        else:
            self.heatmap_background = heatmap_background
            self.heatmap_background_image = get_colormap_background(self.slide_helper, heatmap_background, self.heatmap_alpha)
            self.heatmap_background_downsample = self.slide_helper.level_dimensions[0][0] / heatmap_background.shape[1]

    # 加载某个视图下的tile
    def load_tiles_in_view(self, level, view_scene_rect: QRectF, heatmap=None, heatmap_downsample=None):
        # 若上一个线程还在执行，则停止，重开
        if self.isRunning():
            self.restart = True
        self.level = level
        self.heatmap = heatmap if isinstance(heatmap, np.ndarray) else None
        self.heatmap_downsample = heatmap_downsample
        self.downsample = self.slide_helper.get_downsample_for_level(self.level)
        top_left = view_scene_rect.topLeft()
        bottom_right = view_scene_rect.bottomRight()
        self.top_left_x = top_left.x() - self.tile_size
        self.top_left_y = top_left.y() - self.tile_size
        self.bottom_right_x = bottom_right.x()
        self.bottom_right_y = bottom_right.y()

        if self.background_flag:
            # 先加载背景再加载tile
            self.addBackgroundItem()

            # 加载tile
            if self.heatmap is None:
                loaded_tileItem = self.loaded_tileItem
            else:
                loaded_tileItem = self.loaded_heatmapItem
            """
            将该视图中在缓存中的图片加入scene
            loaded_tileItem是一个列表,每个元素包含[item.level, item.x_y_w_h, item.pixmap]
            """
            for item in loaded_tileItem:
                # 提取当前level中的缓存图片
                if item[0] == level:
                    # 过滤掉已经显示在上面的
                    if item[1] in self.loaded_tile_rect:
                        continue
                    x = item[1][0]
                    y = item[1][1]
                    if x >= self.top_left_x and y >= self.top_left_y:
                        if x <= self.bottom_right_x and y <= self.bottom_right_y:
                            pix_item = QGraphicsPixmapItem(item[2])
                            pix_item.setPos(x, y)
                            self.loaded_tile_rect.append(item[1])
                            self.scene.addItem(pix_item)

        if not self.isRunning():
            # 开启线程
            self.start(QThread.NormalPriority)
        else:
            # 重新加载缓存图片，让暂停的线程恢复工作并上面已经设置好新的view
            self.restart = True
            self.condition.wakeOne()

    # TODO:在视图level变更时
    def restart_load_set(self):
        self.loaded_tile_rect = []
        self.loaded_heatmapItem = []
        # 重新加载缩略图像
        self.background_flag = True

    # 将每个level的tile坐标都记录下来，当要读取某个level时就不需要每次都重新执行slice_rect
    def slice_rect(self):
        tile_rects = {}
        for level in self.slide_helper.get_levels():
            tile_rects[level] = []
            tile_dimension = self.slide_helper.level_dimensions[level]
            for x in range(0, tile_dimension[0], self.tile_size):
                for y in range(0, tile_dimension[1], self.tile_size):
                    w = self.tile_size if x + self.tile_size < tile_dimension[0] else tile_dimension[0] - x
                    h = self.tile_size if y + self.tile_size < tile_dimension[1] else tile_dimension[1] - y
                    tile_rects[level].append((x, y, w, h))
        return tile_rects

    # 更新background图
    def color_transform(self, colorspace):
        if self.slide_helper.is_fluorescene is False:
            if colorspace == 1:
                if self.background_image_h is None or not isinstance(self.background_image_h, QPixmap):
                    self.background_image_h = colordeconvolution(self.background_image_pil, colorspace)
                    self.background_image_h = ndarray_to_pixmap(self.background_image_h)
            if colorspace == 2:
                if self.background_image_d is None or not isinstance(self.background_image_d, QPixmap):
                    self.background_image_d = colordeconvolution(self.background_image_pil, colorspace)
                    self.background_image_d = ndarray_to_pixmap(self.background_image_d)
            if colorspace == 3:
                if self.background_stainNorm is None or not isinstance(self.background_stainNorm, QPixmap):
                    self.background_stainNorm = normalizeStaining(self.background_image_pil)
                    self.background_stainNorm = ndarray_to_pixmap(self.background_stainNorm)
        else:
            self.background_image_pil = self.slide_helper.get_overview(self.backgroud_level, self.background_dimension, colorspace)
            self.background_image = ImageQt(self.background_image_pil)
            self.background_image = QPixmap.fromImage(self.background_image)

    # 该操作只有在非热图显示下才会进行
    def change_colorspace(self, colorspace):
        if colorspace != self.colorspace:
            self.colorspace = colorspace
            # H颜色空间
            self.color_transform(colorspace)
            # 若上一个线程还在执行，则停止，重开
            if self.isRunning():
                self.restart = True
            self.restart_load_set()
            self.loaded_tileItem = []
            # 重新加载背景图片
            self.addBackgroundItem()
            if not self.isRunning():
                # 开启线程
                self.start(QThread.NormalPriority)
            else:
                # 重新加载缓存图片，让暂停的线程恢复工作并上面已经设置好新的view
                self.restart = True
                self.condition.wakeOne()

    def change_heatmap_alpha(self, alpha):
        self.heatmap_alpha = alpha
        if self.heatmap is not None and hasattr(self, "heatmap_background"):
            self.heatmap_background_image = get_colormap_background(self.slide_helper, self.heatmap_background, self.heatmap_alpha)
            # 若上一个线程还在执行，则停止，重开
            if self.isRunning():
                self.restart = True
            self.restart_load_set()
            self.loaded_tileItem = []
            # 重新加载背景图片
            self.addBackgroundItem()
            if not self.isRunning():
                # 开启线程
                self.start(QThread.NormalPriority)
            else:
                # 重新加载缓存图片，让暂停的线程恢复工作并上面已经设置好新的view
                self.restart = True
                self.condition.wakeOne()

    def __del__(self):
        print('tileloader is del')
        self.mutex.lock()
        self.abort = True
        self.condition.wakeOne()
        self.mutex.unlock()
        self.wait()
        if hasattr(self, "loaded_tile_rect"):
            del self.loaded_tile_rect
            del self.loaded_tileItem
            del self.loaded_heatmapItem