"""
ZoomSlider定义了一个滑块部件
用于调节图像窗口的缩放
连接了鼠标滚轮
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class ZoomSlider(QWidget):
    def __init__(self):
        super().__init__()
        self.slider = QSlider(Qt.Vertical)
        self.slider.setRange(1, 40)
        self.slider.setSingleStep(1)
        self.init_label()
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.addLayout(self.label_layout)
        self.main_layout.addWidget(self.slider)

    def init_label(self):
        self.label_0 = QLabel()
        self.label_0.setWordWrap(True)
        self.label_0.setText('  1×')
        self.label_1 = QLabel()
        self.label_1.setWordWrap(True)
        self.label_1.setText('  2×')
        self.label_2 = QLabel()
        self.label_2.setWordWrap(True)
        self.label_2.setText('  4×')
        self.label_3 = QLabel()
        self.label_3.setWordWrap(True)
        self.label_3.setText('10×')
        self.label_4 = QLabel()
        self.label_4.setWordWrap(True)
        self.label_4.setText('20×')
        self.label_5 = QLabel()
        self.label_5.setWordWrap(True)
        self.label_5.setText('40×')
        self.label_layout = QVBoxLayout()
        self.label_layout.setSpacing(0)
        self.label_layout.addWidget(self.label_5)
        self.label_layout.addWidget(self.label_4)
        self.label_layout.addWidget(self.label_3)
        self.label_layout.addWidget(self.label_2)
        self.label_layout.addWidget(self.label_1)
        self.label_layout.addWidget(self.label_0)
        self.set_style()

    def set_style(self):
        self.setStyleSheet("QLabel{font-family:微软雅黑; font: bold 12px;}")