import cv2
import typing
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmapCache
from PyQt5.QtCore import QRectF, QRect, Qt, QByteArray, QBuffer, QIODevice
from PyQt5.QtWidgets import QGraphicsItem, QWidget, QStyleOptionGraphicsItem

from function.heatmap import viz_tile_heatmap, viz_tile_colormap


class GraphicsTile(QGraphicsItem):
    def __init__(self, slide, x_y_w_h, slide_path, level, downsample, heatmap=None, heatmap_downsample=None):
        super(GraphicsTile, self).__init__()
        """
        :param slide: 要显示的WSI
        :param x_y_w_h: 在当前这个level下的的左上角的坐标
        :param slide_path: WSI的路径，用于构建缓存图片的id
        :param level: 要显示图片的level
        :param downsample: 要显示图片的下采样倍率
        :param heatmap: 肿瘤区域，诊断模式下的热力图
        :param heatmap_downsample: 热力图的下采样倍率
        """
        self.x_y_w_h = x_y_w_h
        # 在level=0下的x,y,w,h
        self.slide_rect_0 = QRect(int(x_y_w_h[0] * downsample), int(self.x_y_w_h[1] * downsample), x_y_w_h[2], x_y_w_h[3])
        self.slide_path = slide_path
        self.level = level
        self.downsample = downsample
        self.heatmap = heatmap
        self.heatmap_downsample = heatmap_downsample
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.setAcceptHoverEvents(True)
        if self.heatmap is not None:
            self.cache_key = slide_path + str(level) + str(self.slide_rect_0) + str(00)
        else:
            self.cache_key = slide_path + str(level) + str(self.slide_rect_0) + str(11)
        self.pixmap = QPixmapCache.find(self.cache_key)
        if not self.pixmap:
            if self.heatmap is not None:
                if len(self.heatmap.shape) == 3:
                    tile_image = viz_tile_colormap(slide, self.heatmap, window_box=x_y_w_h, level=level,
                                                  mask_downsample=self.heatmap_downsample)
                elif len(self.heatmap.shape) == 2:
                    tile_image = viz_tile_heatmap(slide, self.heatmap, window_box=x_y_w_h, level=level,
                                                   mask_downsample=self.heatmap_downsample)
                height, width, channel = tile_image.shape
                bytes_per_line = channel * width
                qimage = QtGui.QImage(tile_image.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
                # 将QImage对象转换为QPixmap对象
                self.pixmap = QtGui.QPixmap.fromImage(qimage)

            else:
                tile_pilimage = slide.read_region((self.slide_rect_0.x(), self.slide_rect_0.y()),
                                                  self.level, (self.slide_rect_0.width(), self.slide_rect_0.height()))
                self.pixmap = self.pilimage_to_pixmap(tile_pilimage)

            QPixmapCache.insert(self.cache_key, self.pixmap)

    # 将PIL的Image对象转换成QPixmap对象
    def pilimage_to_pixmap(self, pilimage):
        qim = ImageQt(pilimage)
        pix = QtGui.QPixmap.fromImage(qim)
        return pix

    # 返回图形项的边界矩形
    def boundingRect(self):
        return QRectF(0, 0, self.slide_rect_0.width(), self.slide_rect_0.height())

    # 将缓存的pixmap绘制在图形项的边界矩形内部
    def paint(self, painter: QtGui.QPainter, option: QStyleOptionGraphicsItem,
              widget: typing.Optional[QWidget] = ...):
        painter.drawPixmap(self.boundingRect().toRect(), self.pixmap)

    def __str__(self) -> str:
        return "{}: slide_path: {}, slide_rect_0: {}".format(self.__class__.__name__, self.slide_path, self.slide_rect_0)