from PyQt5.QtCore import Qt, QPointF, QPoint, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QStatusBar, QLabel, QMdiArea

class StatusBar(QStatusBar):
    synchronousSignal = pyqtSignal(object, object, object, object, object)
    def __init__(self, mdiArea: QMdiArea):
        super(StatusBar, self).__init__()
        self.mdiArea = mdiArea
        self.slideViewer = None
        self.init_UI()

    def init_UI(self):
        self.magnification_label = QLabel()
        self.magnification_label.setText("当前倍数：")
        self.null1 = QLabel()
        self.null1.setText("      ")
        self.mouse_pos_label = QLabel()
        self.mouse_pos_label.setText("鼠标位置：")
        self.null2 = QLabel()
        self.null2.setText("      ")
        self.slide_dimension_label = QLabel()
        self.slide_dimension_label.setText("图片尺寸：")
        self.null3 = QLabel()
        self.null3.setText("      ")
        self.view_rect_label = QLabel()
        self.view_rect_label.setText("视图位置：")
        self.null4 = QLabel()
        self.null4.setText("      ")

        self.addWidget(self.magnification_label)
        self.addWidget(self.null1)
        self.addWidget(self.mouse_pos_label)
        self.addWidget(self.null2)
        self.addWidget(self.slide_dimension_label)
        self.addWidget(self.null3)
        self.addWidget(self.view_rect_label)
        self.addWidget(self.null4)

        self.mdiArea.subWindowActivated.connect(self.change_SlideViewer)

    def change_SlideViewer(self):
        active_sub = self.mdiArea.activeSubWindow()
        try:
            if hasattr(active_sub.widget(), "mainViewer"):
                self.slideViewer = active_sub.widget().mainViewer
                self.slideViewer.mousePosSignal.connect(self.update_mouse_pos)
                self.slideViewer.magnificationSignal.connect(self.update_magnification)
        except:
            return

    def update_mouse_pos(self, pos: QPointF):
        downsample = int(self.slideViewer.slide_helper.get_downsample_for_level(self.slideViewer.current_level))
        self.mouse_pos_label.setText("鼠标位置: " + self.point_to_str(pos, downsample))

    def update_magnification(self):
        downsample = int(self.slideViewer.slide_helper.get_downsample_for_level(self.slideViewer.current_level))
        max_dimension = self.slideViewer.slide_helper.get_level_dimension(0)
        scale = self.slideViewer.get_current_view_scale()
        self.magnification_label.setText(
            "当前倍数:  {:}".format(int(40 / (downsample / scale) * 10) / 10)
        )
        self.slide_dimension_label.setText(
            "图片尺寸: ({}, {})".format(*max_dimension)
        )
        new_view_scene_rect = self.slideViewer.get_current_view_scene_rect().getRect()
        rect = (int(new_view_scene_rect[0])*downsample, int(new_view_scene_rect[1])*downsample,
                int(new_view_scene_rect[2])*downsample, int(new_view_scene_rect[3])*downsample)
        self.view_rect_label.setText(
            "视图位置: ({:.0f}, {:.0f}, {:.0f}, {:.0f})".format(*rect)
        )

    def point_to_str(self, point: QPoint, downsample: int):
        if isinstance(point, QPointF):
            return "({:.0f}, {:.0f})".format(point.x()*downsample, point.y()*downsample)
        else:
            return "({}, {})".format(point.x()*downsample, point.y()*downsample)