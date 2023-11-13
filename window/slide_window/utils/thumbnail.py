"""
THumbnail用于显示病理图像的总览图
点击总览图可以跳转到对应的区域
显示热力图
"""
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import  QSizePolicy, QFrame
from PyQt5.QtCore import Qt, pyqtSignal, QPointF, QRectF, QRect, QSize, QPoint
from PyQt5.QtGui import QPixmap, QMouseEvent, QPaintEvent, QPen, QPainter, QColor
from window.slide_window.utils.SlideHelper import SlideHelper

class Thumbnail(QFrame):
    thumbnailClickedSignal = pyqtSignal(QPointF, list)
    def __init__(self, base_size=250):
        super(Thumbnail, self).__init__()
        # 表示鼠标左键是否按下并移动了
        self.move_flag = False
        # 鼠标的当前位置
        self.mouse_x = None
        self.mouse_y = None
        # 鼠标按下是的位置
        self.origin_x = None
        self.origin_y = None
        # 当前的视野范围
        self.FOV = QRectF()
        # 框架的基本大小
        self.base_size = base_size

        self.thumbnail = None

        # 设置框架样式与大小策略
        policy = QSizePolicy()
        policy.setHorizontalPolicy(QSizePolicy.Fixed)
        policy.setVerticalPolicy(QSizePolicy.Fixed)
        # 当宽度被改变时，高度也随之改变
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)

        self.setFixedWidth(350)
        self.setFixedHeight(350)
        self.aspectRatio = 1

    # 载入缩略图，如果是热图，则加载热图
    def load_thumbnail(self, slide_helper: SlideHelper, heatmap: QPixmap=None):
        if heatmap is None:
            self.slide_helper = slide_helper
            thumbnail_level = self.slide_helper.level_count - 1
            thumbnail_dimension = self.slide_helper.get_level_dimension(-1)
            thumbnail = self.slide_helper.get_overview(thumbnail_level, thumbnail_dimension, )
            self.aspectRatio = thumbnail_dimension[0] / thumbnail_dimension[1]
            if self.aspectRatio < 1:
                self.thumbnail_dimension = [int(self.base_size * self.aspectRatio), self.base_size]

            else:
                self.thumbnail_dimension = [self.base_size, int(self.base_size / self.aspectRatio)]
            thumbnail = thumbnail.resize(self.thumbnail_dimension)
            thumbnail = ImageQt(thumbnail)
            self.thumbnail = QPixmap.fromImage(thumbnail)
        else:
            heatmap = heatmap.scaled(*self.thumbnail_dimension)
            self.thumbnail = heatmap
        # 设置thumbnail视图的大小
        self.setFixedWidth(self.thumbnail_dimension[0])
        self.setFixedHeight(self.thumbnail_dimension[1])
        return


    # TODO:更新当前视图区域在缩略图上的边界
    def update_FOV(self, rect: QRectF, level):
        dimension = self.slide_helper.get_level_dimension(level)
        scale = dimension[0] / self.thumbnail_dimension[0]
        self.FOV = QRectF(rect.x() / scale,
                          rect.y() / scale,
                          rect.width() / scale,
                          rect.height() / scale)
        self.update()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.begin(self)
        if self.thumbnail:
            painter.drawPixmap(QRect(0, 0, self.width(), self.height()), self.thumbnail)
            painter.setPen(QPen(Qt.black, 1))
            painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
        # 绘制当前视图区域在缩略图上的边界
        if self.FOV:
            blue = QPen(QColor("blue"))
            blue.setWidth(2)
            painter.setPen(blue)
            x = self.width() * (self.FOV.left() / self.thumbnail.width()) + 1
            y = self.height() * (self.FOV.top() / self.thumbnail.height()) + 1
            w = self.width() * (self.FOV.width() / self.thumbnail.width()) - 2
            h = self.height() * (self.FOV.height() / self.thumbnail.height()) - 2
            # 框太小则画十字
            if w < 10:
                painter.drawLine(QPoint(x + w / 2 - 5, y + h / 2), QPoint(x + w / 2 + 5, y + h / 2))
                painter.drawLine(QPoint(x + w / 2, y + h / 2 - 5), QPoint(x + w / 2, y + h / 2 + 5))
                return
            painter.drawRect(x, y, w, h)
        painter.end()

    # 点击缩略图，跳转到相应位置
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            pos_x = event.pos().x()
            pos_y = event.pos().y()
            pos = QPointF(pos_x, pos_y)
            self.thumbnailClickedSignal.emit(pos, [self.thumbnail.width(), self.thumbnail.height()])
