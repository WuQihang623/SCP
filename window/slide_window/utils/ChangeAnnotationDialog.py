# 修改标注类别时的对话框

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtGui import QPainterPath, QPen, QBrush, QColor, QFont
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QGroupBox, QPushButton, QLabel, QGridLayout, QDialog, QComboBox

class ChangeAnnotationDiaglog(QDialog):
    def __init__(self, AnnotationTypes, current_type):
        super(ChangeAnnotationDiaglog, self).__init__()
        self.setWindowTitle("修改标注类别")
        self.AnnotationTypes = AnnotationTypes
        self.current_type = current_type
        self.init_layout()

    def init_layout(self):
        self.text = QLabel("细胞类别：")
        self.combobox = QComboBox(self)
        for i, (name, color) in enumerate(self.AnnotationTypes.items()):
            self.combobox.addItem(name)
            pixmap = QPixmap(20, 20)
            pixmap.fill(QColor(*color))
            self.combobox.setItemIcon(i, QIcon(pixmap))
        self.combobox.setCurrentText(self.current_type)

        self.cancel_btn = QPushButton("取消")
        self.sure_btn = QPushButton("确认")
        self.sure_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.close)

        main_layout = QGridLayout(self)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setVerticalSpacing(20)
        main_layout.addWidget(self.text, 1, 1)
        main_layout.addWidget(self.combobox, 1, 2)
        main_layout.addWidget(self.sure_btn, 2, 1)
        main_layout.addWidget(self.cancel_btn, 2, 2)

    def get_text(self):
        return self.combobox.currentText()
