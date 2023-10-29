import os.path
import sys
import constants
import openslide
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QPoint, Qt, QEvent, QRectF, pyqtSignal, QPointF, QObject, QSize
from PyQt5.QtGui import QWheelEvent, QMouseEvent, QTransform, QPainter, QPen, QColor, QBrush
from window.slide_window.utils.thumbnail import Thumbnail
from window.slide_window.slider import ZoomSlider

from window.utils.mouseItem import MouseItem
from function.shot_screen import build_screenshot_image
from window.slide_window.utils.SlideHelper import SlideHelper
from window.slide_window.TileLoader.TileLoader import TileManager

class BasicSlideViewer(QFrame):
    updateFOVSignal = pyqtSignal(QRectF, int) # 更新缩略图的矩形框信号
    mousePosSignal = pyqtSignal(QPointF)      # 鼠标位置更新信号
    magnificationSignal = pyqtSignal(bool)   # 视图放大倍数更新信号
    # 同步图像移动发送信号
    moveTogetherSignal = pyqtSignal(list)
    scaleTogetherSignal = pyqtSignal(QPoint, float)
    # 同步图像鼠标信号
    pairMouseSignal = pyqtSignal(QPointF)
    clearMouseSignal = pyqtSignal(bool)
    def __init__(self):
        super(BasicSlideViewer, self).__init__()
        self.init_UI()
        self.init_variable()

    def init_UI(self):
        self.scene = QGraphicsScene()
        self.scene.clear_flag = False
        self.scene.clear_mouse = False
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

        self.mouseItem = MouseItem()
        self.scene.addItem(self.mouseItem)

    def init_variable(self):
        # 鼠标拖动标志，当鼠标点击左键时该标志置为True
        self.move_flag = False
        # 允许鼠标拖动标志
        self.move_allow_flag = True

        # 初始的slider的值
        self.slider_value = -1

        # 初始化配准信息
        transform_matrix = np.array([[1, 0, 0],
                                      [0, 1, 0],
                                      [0, 0, 1]])
        self.init_Registration(transform_matrix)
        # 同步鼠标的信息
        self.mouse_x = 0
        self.mouse_y = 0

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
        self.current_downsample = self.slide_helper.get_downsample_for_level(self.current_level)
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
    # 放大倍数为 40 / (downsample / scale)
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
        # 当鼠标离开视图时，需要将同步的鼠标清除掉
        elif isinstance(event, QEvent.Leave):
            self.leaveEvent(event)
        return event_porcessed

    def leaveEvent(self, event):
        self.clearMouseSignal.emit(True)

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

        # 如果需要配准的话，计算当前视图的中心点，让同步图像通过中心点进行配准
        if self.Registration:
            current_center = QPoint(self.size().width() / 2, self.size().height() / 2)
            current_center = self.view.mapToScene(current_center)
            current_center = [current_center.x() * self.current_downsample,
                              current_center.y() * self.current_downsample]
            self.moveTogetherSignal.emit(current_center)

    # TODO:鼠标滚轮事件
    def processWheelEvent(self, event: QWheelEvent):
        # 计算放大与缩小的比例
        zoom_in = self.zoom_step
        zoom_out = 1 / zoom_in
        zoom = zoom_in if event.angleDelta().y() > 0 else zoom_out
        self.responseWheelEvent(event.pos(), zoom)
        # 图像同步缩放
        if self.Registration:
            pos = self.view.mapToScene(event.pos())
            pos = QPoint(pos.x() * self.current_downsample, pos.y() * self.current_downsample)
            self.scaleTogetherSignal.emit(pos, zoom)
            if self.scene.clear_mouse:
                # 发送鼠标同步信号
                self.pairMouseSignal.emit(self.view.mapToScene(event.pos()))

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

        self.current_downsample = self.slide_helper.get_downsample_for_level(self.current_level)

        if self.current_level != old_level:
            clear_scene_flag = True
        else:
            clear_scene_flag = False

        level_scale_delta = 1 / (self.current_downsample / old_level_downsample)

        # 获取放大后的rect
        r = old_view_scene_rect.topLeft()
        m = old_mouse_pos_scene
        new_view_scene_rect_top_left = (m - (m - r) / zoom) * level_scale_delta
        new_view_scene_rect = QRectF(new_view_scene_rect_top_left,
                                     old_view_scene_rect.size() * level_scale_delta / zoom)

        new_scale = self.get_current_view_scale() * zoom * self.current_downsample / old_level_downsample

        transform = QTransform().scale(new_scale, new_scale).translate(-new_view_scene_rect.x(),
                                                                       -new_view_scene_rect.y())

        self.update_scale_view(self.current_level, new_view_scene_rect, clear_scene_flag, mousePos)
        self.updateFOVSignal.emit(new_view_scene_rect, self.current_level)
        self.reset_view_transform()
        self.view.setTransform(transform, False)
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
            self.scene.clear_mouse = True
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

    # 跳转到当前level下的以pos为中心的区域
    def switch2pos(self, pos):
        self.view.centerOn(pos)
        self.view.update()
        # 获取当前视图在场景中的矩形
        view_scene_rect = self.get_current_view_scene_rect()
        # 加载当前视图内可见的图块
        self.TileLoader.load_tiles_in_view(self.current_level, view_scene_rect, self.heatmap,
                                           self.heatmap_downsample)
        # 发射FOV更新信号
        self.updateFOVSignal.emit(view_scene_rect, self.current_level)
        # 更新状态栏,视图位置
        self.magnificationSignal.emit(True)

    # 用于链接点击缩略图跳转的信号
    def showImageAtThumbnailArea(self, pos, thumbnail_dimension):
        current_dimension = self.slide_helper.get_level_dimension(self.current_level)
        scale = current_dimension[0] / thumbnail_dimension[0]
        pos = QPointF(pos.x() * scale, pos.y() * scale)
        self.switch2pos(pos)
        if self.Registration:
            self.moveTogetherSignal.emit([pos.x() * self.current_downsample, pos.y() * self.current_downsample])

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

            # 图像同步缩放
            if self.Registration:
                pos = self.view.mapToScene(pos)
                pos = QPoint(pos.x() * self.current_downsample, pos.y() * self.current_downsample)
                self.scaleTogetherSignal.emit(pos, zoom)


    # 计算放大倍数
    def get_magnification(self):
        current_scale = self.get_current_view_scale()
        # downsample = self.slide_helper.get_downsample_for_level(self.current_level)
        magnification = 40 / (self.current_downsample * 1.0 / current_scale)
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
            self.scene.clear_mouse = True
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

    # 初始化配准信息
    def init_Registration(self, transform_matrix, match_downsample=1, Registration=False):
        if transform_matrix is not None:
            self.transform_matrix = transform_matrix
        self.match_downsample = match_downsample
        self.Registration = Registration

    # 根据放射变换矩阵，当平移时进行调用
    # 如果只是平移的话，并不需要考虑缩放的问题，因为在一开始的时候就已经进行过了缩放维度的对其
    def move_together(self, center_pos):
        """
        :param center_pos: 在level=0下的要跟随的视图中心点的坐标，除以self.match_downsample
        :return:
        """
        source_points_matrix = np.array([[center_pos[0]], [center_pos[1]], [1]])
        target_points_matrix = np.linalg.inv(self.transform_matrix) @ source_points_matrix
        # 将在levle=0下的坐标转换到当前的level下面
        target_points_matrix = target_points_matrix / self.current_downsample
        pos = QPoint(target_points_matrix[0][0], target_points_matrix[1, 0])
        self.switch2pos(pos)

    # 根据放射变换矩阵，当滚动滚轮时调用, 默认之前二者处于同样的放大倍数下面
    def scale_together(self, pos: QPoint, zoom):
        """
        :param pos: 缩放时鼠标的位置
        :param zoom: 要缩放的背书
        :return:
        """
        source_points_matrix = np.array([[pos.x()], [pos.y()], [1]])
        target_points_matrix = np.linalg.inv(self.transform_matrix) @ source_points_matrix
        pos = QPoint(target_points_matrix[0][0] / self.current_downsample, target_points_matrix[1, 0] / self.current_downsample)
        pos = self.view.mapFromScene(pos)
        self.responseWheelEvent(pos, zoom)

    def send_match(self):
        main_scale = self.get_current_view_scale() / self.current_downsample
        current_center = QPoint(self.size().width() / 2, self.size().height() / 2)
        current_center = self.view.mapToScene(current_center)
        current_center = [current_center.x() * self.current_downsample,
                          current_center.y() * self.current_downsample]
        return main_scale, current_center

    # 第一次匹配时，将同步图像与主窗口对其
    def receive_match(self, main_scale, main_center):
        # 先进行缩放，再
        pair_scale = self.get_current_view_scale() / self.current_downsample
        zoom = main_scale / pair_scale
        pos = QPoint(self.size().width() / 2, self.size().height() / 2)
        self.responseWheelEvent(pos, zoom)
        self.move_together(main_center)

    # 鼠标移动时，在另一个窗口绘制对应的鼠标
    def draw_mouse(self, pos):
        self.mouse_x = pos.x()
        self.mouse_y = pos.y()
        if self.scene.clear_mouse:
            self.mouseItem = MouseItem()
            self.scene.addItem(self.mouseItem)
            self.scene.clear_mouse = False
        self.mouseItem.setPos(self.mouse_x, self.mouse_y)
        self.mouseItem.setZValue(40)

    def remove_mouse(self, *args):
        if self.scene.clear_mouse is False:
            self.mouseItem.clearItem()
            self.scene.clear_mouse = True


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
