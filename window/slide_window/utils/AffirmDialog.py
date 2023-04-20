# 弹出是或否的对话框

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtGui import QPainterPath, QPen, QBrush, QColor, QFont
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QGroupBox, QPushButton, QLabel, QGridLayout, QDialog, QComboBox

class AffirmDialog(QDialog):
    def __init__(self, text):
        super(AffirmDialog, self).__init__()

        label = QLabel(text)
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.close)

        main_layout = QGridLayout(self)
        main_layout.addWidget(label, 1, 0)
        main_layout.addWidget(ok_btn, 2, 0)
        main_layout.addWidget(cancel_btn, 2, 1)