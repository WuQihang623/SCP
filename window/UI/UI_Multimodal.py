import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from window.utils.FolderSelector import FolderSelector

class ColorbarLabel(QLabel):
    turnHeatmapSignal = pyqtSignal(int)
    def __init__(self, index):
        super().__init__()
        """
        :param: index, 第几个attention matrix对应的colorbar
        """
        self.index = index

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.turnHeatmapSignal.emit(self.index)

    def set_image(self, numpy_array):
        height, width, channel = numpy_array.shape
        bytes_per_line = 3 * width
        q_image = QImage(numpy_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.setPixmap(pixmap)


class UI_Multimodal(QWidget):
    def __init__(self):
        super(UI_Multimodal, self).__init__()
        self.init_UI()

    def init_UI(self):
        self.mainlayout = QVBoxLayout(self)
        WidgetBox = QGroupBox()
        WidgetBox.setTitle('多模态可视化')
        btn_layout = QGridLayout()
        btn_layout.setVerticalSpacing(25)
        btn_layout.setHorizontalSpacing(20)
        self.wsi_path_text = QLabel()
        self.wsi_path_text.setWordWrap(True)
        self.folderselector = FolderSelector()
        self.load_btn = QPushButton("载入结果")
        self.load_comparison_btn = QPushButton("载入对比结果")
        self.showHeatmap_btn = QPushButton("显示热图")
        self.showHeatmap_btn.setCheckable(True)
        self.showHeatmap_btn.setChecked(False)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        btn_layout.addWidget(self.folderselector, 1, 0, 1, 1)
        btn_layout.addWidget(self.load_btn, 2, 0, 1, 1)
        btn_layout.addWidget(self.showHeatmap_btn, 4, 0, 1, 1)
        btn_layout.addWidget(self.load_comparison_btn, 3, 0, 1, 1)
        btn_layout.addWidget(line, 5, 0, 1, 1)
        null = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn_layout.addItem(null, 6, 0, 1, 1)
        WidgetBox.setLayout(btn_layout)
        self.mainlayout.addWidget(WidgetBox)
        self.label_widgets = []

    def load_colorbar(self, colorbar_list):
        self.clear_colorbar()
        layout = QVBoxLayout()
        for idx, colorbar in enumerate(colorbar_list):
            colorbar_label = ColorbarLabel(idx)
            colorbar_label.set_image(colorbar.astype("uint8"))
            colorbar_label.turnHeatmapSignal.connect(self.turn_heatmap)
            layout.addWidget(colorbar_label)
            self.label_widgets.append(colorbar_label)
        self.mainlayout.addLayout(layout)

    def clear_colorbar(self):
        for colorbar_label in self.label_widgets:
            colorbar_label.setParent(None)
            colorbar_label.deleteLater()

    def turn_heatmap(self, flag):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet())
    window = UI_Multimodal()
    window.show()
    sys.exit(app.exec_())
