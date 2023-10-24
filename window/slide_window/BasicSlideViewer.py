import os.path
import sys
import constants
import openslide
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QPoint, Qt, QEvent, QRectF, pyqtSignal, QPointF, QObject, QSize
from PyQt5.QtGui import QWheelEvent, QMouseEvent, QTransform, QPainter
from window.slide_window.utils.thumbnail import Thumbnail
from window.slide_window.slider import ZoomSlider

from function.shot_screen import build_screenshot_image
from window.slide_window.utils.SlideHelper import SlideHelper
from window.slide_window.TileLoader.TileLoader import TileManager

class BasicSlideViewer(QFrame):
    updateFOVSignal = pyqtSignal(QRectF, int) # 更新缩略图的矩形框信号
    mousePosSignal = pyqtSignal(QPointF)      # 鼠标位置更新信号
    magnificationSignal = pyqtSignal(bool)   # 视图放大倍数更新信号
    def __init__(self):
        super(BasicSlideViewer, self).__init__()
        self.init_UI()
        self.init_variable()

    def init_UI(self):
        self.scene = QGraphicsScene()
        self.scene.clear_flag = False
        self.view = QGraphicsView()
        self.view.setScene(self.scene)
        self.thumbnail = Thumbnail()
        self.slider = ZoomSlider()
        self.menu = QMenu()
        self.full_screen_action = QAction("切换全屏模式(Q)")
        # TODO: full screen action 触发会报错
        self.full_screen_action.setEnabled(False)
        self.shot_screen_action = QAction("截图")
        self.shot_screen_action.triggered.connect(self.shotScreen)

        self.view.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.view.viewport().installEventFilter(self)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.view_layout = QHBoxLayout(self.view)
        self.thumbnail_layout = QVBoxLayout()
        self.slider_layout = QVBoxLayout()
        self.slider_layout.addStretch(4)
        self.slider_layout.addWidget(self.slider)
        self.view_layout.addLayout(self.slider_layout)
        self.view_layout.addStretch(4)
        self.view_layout.addLayout(self.thumbnail_layout, 1)
        self.thumbnail_layout.addWidget(self.thumbnail, 1)
        self.thumbnail_layout.addStretch(4)

        self.main_layout = QGridLayout(self)
        self.main_layout.addWidget(self.view, 1, 1)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

    def init_variable(self):
        # 鼠标拖动标志，当鼠标点击左键时该标志置为True
        self.move_flag = False
        # 允许鼠标拖动标志
        self.move_allow_flag = True

        # 初始的slider的值
        self.slider_value = -1

    # 设置右键的菜单栏
    def addAction2Menu(self, action_list):
        for action in action_list:
            if action is None:
                self.menu.addSeparator()
            else:
                self.menu.addAction(action)
        self.menu.addAction(self.full_screen_action)
        self.menu.addAction(self.shot_screen_action)

    # 载入slide,同时初始化缩略图，放大滑块
    def load_slide(self, slide_path, zoom_step=1.25):
        self.slide = openslide.open_slide(slide_path)
        self.slide_helper = SlideHelper(slide_path)
        self.slide_name = os.path.splitext(os.path.basename(slide_path))[0]
        self.zoom_step = zoom_step
        # 初始化heatmap为False
        self.heatmap = None
        self.heatmap_downsample = None

        # 将一个小分辨率的slide载入到window中
        self.TileLoader = TileManager(self.scene, self.slide_helper)
        self.TileLoader.addTileItemSignal.connect(self.addTileItem)
        level = self.slide_helper.get_max_level()
        scene_rect = self.slide_helper.get_rect_for_level(level)
        self.scene.setSceneRect(scene_rect)
        self.scene.addRect(scene_rect, pen=Qt.white, brush=Qt.white)
        rect = self.get_current_view_scene_rect()
        self.TileLoader.load_tiles_in_view(level, rect, self.heatmap, self.heatmap_downsample)
        self.current_level = level
        # 设置右下角的缩略图
        self.thumbnail.load_thumbnail(self.slide_helper)
        self.updateFOVSignal.connect(self.thumbnail.update_FOV)
        self.thumbnail.thumbnailClickedSignal.connect(self.showImageAtThumbnailArea)

        # TODO: 初始化缩放滑块
        self.slider.slider.valueChanged.connect(self.responseSlider)


    # 将线程中想scene增加item的信号链接到这里
    def addTileItem(self, item):
        if item.level != self.current_level:
            return
        self.scene.addItem(item)

    # 将视口矩形映射到场景坐标系中，并返回场景中包含此矩形的最小矩形（边界矩形）
    def get_current_view_scene_rect(self):
        # 获取视图的矩形区域
        view_rect = self.view.viewport().rect()
        # 将视图的矩形区域转换为场景坐标系下的区域
        view_scene_rect = self.view.mapToScene(view_rect).boundingRect()
        return view_scene_rect

    # 当前窗口的缩放倍率
    def get_current_view_scale(self):
        return self.view.transform().m11()

    # 监听所有窗口小部件的事件
    def eventFilter(self, qobj: 'QObject', event: 'QEvent') -> bool:
        # 如果不是鼠标事件或者滚轮事件，则不进行事件的传递
        event_porcessed = False
        # 鼠标事件
        if isinstance(event, QMouseEvent):
            event_porcessed = self.processMouseEvent(event)
        elif isinstance(event, QWheelEvent):
            event_porcessed = self.processWheelEvent(event)
        return event_porcessed

    # TODO: 鼠标事件
    def processMouseEvent(self, event: QMouseEvent):
        if self.slide_helper is None:
            return True
        # 鼠标左键
        if event.button() == Qt.LeftButton:
            if event.type() == QEvent.MouseButtonPress:
                # 设置鼠标拖动视图标志
                self.move_flag = True
                self.start_mouse_pos_x = event.pos().x()
                self.start_mouse_pos_y = event.pos().y()
            elif event.type() == QEvent.MouseButtonRelease:
                self.move_flag = False

        elif event.type() == QEvent.MouseMove:
            # 更新状态栏鼠标位置
            self.mousePosSignal.emit(self.view.mapToScene(event.pos()))

            # 视图移动
            if self.move_flag and self.move_allow_flag:
                self.responseMouseMove(event)
        return True

    # 响应鼠标拖动屏幕
    def responseMouseMove(self, event):
        # 获取视图的水平和垂直滚动条对象
        horizontal_scrollbar = self.view.horizontalScrollBar()
        vertical_scrollbar = self.view.verticalScrollBar()
        # 更新结束鼠标位置
        self.end_mouse_pos_x = event.pos().x()
        self.end_mouse_pos_y = event.pos().y()
        # 计算当前鼠标位置相对于上一个位置的偏移量
        delta_x = self.end_mouse_pos_x - self.start_mouse_pos_x
        delta_y = self.end_mouse_pos_y - self.start_mouse_pos_y
        # 计算新的滚动条值并限制在滚动条的范围内
        new_h_scrollbar_value = horizontal_scrollbar.value() - delta_x
        new_v_scrollbar_value = vertical_scrollbar.value() - delta_y
        new_h_scrollbar_value = max(min(new_h_scrollbar_value, horizontal_scrollbar.maximum()),
                                    horizontal_scrollbar.minimum())
        new_v_scrollbar_value = max(min(new_v_scrollbar_value, vertical_scrollbar.maximum()),
                                    vertical_scrollbar.minimum())
        # 更新滚动条值
        horizontal_scrollbar.setValue(new_h_scrollbar_value)
        vertical_scrollbar.setValue(new_v_scrollbar_value)
        # 更新起始鼠标位置
        self.start_mouse_pos_x = self.end_mouse_pos_x
        self.start_mouse_pos_y = self.end_mouse_pos_y
        # 获取当前视图在场景中的矩形
        view_scene_rect = self.get_current_view_scene_rect()
        # 加载当前视图内可见的图块
        self.TileLoader.load_tiles_in_view(self.current_level, view_scene_rect, self.heatmap,
                                           self.heatmap_downsample)
        # 发射FOV更新信号
        self.updateFOVSignal.emit(view_scene_rect, self.current_level)

        # TODO:更新状态栏,视图位置
        self.magnificationSignal.emit(True)

    # TODO:鼠标滚轮事件
    def processWheelEvent(self, event: QWheelEvent):
        # 计算放大与缩小的比例
        zoom_in = self.zoom_step
        zoom_out = 1 / zoom_in
        zoom = zoom_in if event.angleDelta().y() > 0 else zoom_out

        self.responseWheelEvent(event.pos(), zoom)

        event.accept()
        return True

    # 滚动滚轮事件，调整缩放
    def responseWheelEvent(self, mousePos: QPoint, zoom):
        old_level = self.current_level
        old_level_downsample = self.slide_helper.get_downsample_for_level(old_level)

        # 放大倍数太大与太小都不进行操作
        if old_level == 0:
            scale = self.get_current_view_scale() * zoom
            if 40 / (old_level_downsample / scale) > 120:
                return
        elif old_level == self.slide_helper.get_max_level():
            lowest = 40 / old_level_downsample
            scale = self.get_current_view_scale() * zoom
            if 40 / (old_level_downsample / scale) < 0.2 * lowest:
                return

        # 将在当前视图中的鼠标位置变换到scene下的位置
        old_mouse_pos_scene = self.view.mapToScene(mousePos)
        old_view_scene_rect = self.get_current_view_scene_rect()

        self.current_level = self.get_best_level_for_scale(self.get_current_view_scale() * zoom)
        new_level_downsample = self.slide_helper.get_downsample_for_level(self.current_level)

        if self.current_level != old_level:
            clear_scene_flag = True
        else:
            clear_scene_flag = False

        level_scale_delta = 1 / (new_level_downsample / old_level_downsample)

        # 获取放大后的rect
        r = old_view_scene_rect.topLeft()
        m = old_mouse_pos_scene
        new_view_scene_rect_top_left = (m - (m - r) / zoom) * level_scale_delta
        new_view_scene_rect = QRectF(new_view_scene_rect_top_left,
                                     old_view_scene_rect.size() * level_scale_delta / zoom)

        new_scale = self.get_current_view_scale() * zoom * new_level_downsample / old_level_downsample

        transform = QTransform().scale(new_scale, new_scale).translate(-new_view_scene_rect.x(),
                                                                       -new_view_scene_rect.y())

        self.update_scale_view(self.current_level, new_view_scene_rect, clear_scene_flag, mousePos)
        self.updateFOVSignal.emit(new_view_scene_rect, self.current_level)
        self.reset_view_transform()
        self.view.setTransform(transform, False)

        # TODO:更新状态栏，放大倍数，视图位置
        self.magnificationSignal.emit(True)
        # 更新slider
        self.update_slider()

    # 滚动滚轮时更新视图的方法
    def update_scale_view(self, level, scene_view_rect, clear_scene_flag, mouse_pos):
        """
        :param level: 当前放大倍率下的level
        :param scene_view_rect: 当前视图在level图像上的位置
        :return:
        """
        # 清除掉当前scene中的图片，并重新设定Secne的大小
        new_rect = self.slide_helper.get_rect_for_level(level)
        if clear_scene_flag:
            self.scene.clear()
            self.scene.clear_flag = True
            self.scene.setSceneRect(new_rect)
            self.scene.addRect(new_rect, pen=Qt.white, brush=Qt.white)
            # 清除缓存
            self.TileLoader.restart_load_set()
            # 绘制当前rect的图片
            self.TileLoader.load_tiles_in_view(level, scene_view_rect, self.heatmap, self.heatmap_downsample)
        else:
            self.TileLoader.load_tiles_in_view(level, scene_view_rect, self.heatmap, self.heatmap_downsample)


    # 更新slider的值
    def update_slider(self):
        slider_value = int(self.get_magnification())
        if slider_value < 1:
            slider_value = 1
        elif slider_value > 40:
            slider_value = 40
        self.slider_value = slider_value
        self.slider.slider.blockSignals(True)
        self.slider.slider.setValue(self.slider_value)
        self.slider.slider.blockSignals(False)

    def reset_view_transform(self):
        self.view.resetTransform()
        self.view.horizontalScrollBar().setValue(0)
        self.view.verticalScrollBar().setValue(0)

    # 获取与scale相应的level
    def get_best_level_for_scale(self, scale):
        scene_width = self.scene.sceneRect().size().width() * scale
        slide_dimensions = np.array(self.slide.level_dimensions)
        level = np.argmin(np.abs(slide_dimensions[:, 0] - scene_width))
        return level

    # 用于链接点击缩略图跳转的信号
    def showImageAtThumbnailArea(self, pos, thumbnail_dimension):
        current_dimension = self.slide_helper.get_level_dimension(self.current_level)
        scale = current_dimension[0] / thumbnail_dimension[0]
        pos = QPointF(pos.x() * scale, pos.y() * scale)

        self.view.centerOn(pos)
        self.view.update()

        rect = self.get_current_view_scene_rect()
        self.TileLoader.load_tiles_in_view(self.current_level, rect, self.heatmap, self.heatmap_downsample)
        # 更新缩略图上的区域框
        self.updateFOVSignal.emit(rect, self.current_level)
        # 更新状态栏上的信息
        self.magnificationSignal.emit(True)

    # 调整slider，响应图像缩放
    def responseSlider(self, value):
        # 判断当前slider value 是否与改变过的相同
        if self.slider_value != value:
            # 计算当前的缩放倍数
            current_value = self.get_magnification()
            zoom = value / current_value
            pos = QPoint(self.size().width() / 2, self.size().height() / 2)
            self.responseWheelEvent(pos, zoom)
            self.slider_value = value


    # 计算放大倍数
    def get_magnification(self):
        current_scale = self.get_current_view_scale()
        downsample = self.slide_helper.get_downsample_for_level(self.current_level)
        magnification = 40 / (downsample * 1.0 / current_scale)
        return magnification

    # 设置move allow标志,
    def set_Move_Allow(self, move: bool):
        self.move_allow_flag = move

    # 重新绘制视图
    def reshowView(self, heatmap=None, heatmap_downsample=None):
        if hasattr(self, 'slide_helper'):
            new_rect = self.slide_helper.get_rect_for_level(self.current_level)
            scene_view_rect = self.get_current_view_scene_rect()
            self.scene.clear()
            self.scene.clear_flag = True
            self.scene.setSceneRect(new_rect)
            self.scene.addRect(new_rect, pen=Qt.white, brush=Qt.white)
            # 清除缓存
            self.TileLoader.restart_load_set()
            # 绘制当前rect的图片
            self.TileLoader.load_tiles_in_view(self.current_level, scene_view_rect, heatmap, heatmap_downsample)

    # 截图屏幕
    def shotScreen(self):
        os.makedirs(constants.shot_screen_path, exist_ok=True)
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "保存截图",
                                                   f"{constants.shot_screen_path}/{self.slide_name}.jpg",
                                                   'jpg Files(*.jpg)', options=options)
        image = build_screenshot_image(self.scene, QSize(1024, 1024), self.get_current_view_scene_rect())
        image.save(file_path)

    def closeEvent(self):
        if hasattr(self, "TileLoader"):
            self.scene.clear()
            self.TileLoader.__del__()
            print("closeEvent")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BasicSlideViewer()
    window.show()
    sys.exit(app.exec_())
