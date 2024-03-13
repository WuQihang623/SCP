from PyQt5.QtGui import  QColor
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from collections import OrderedDict

from PyQt5.QtWidgets import QPushButton, QLabel, QGridLayout, QDialog, QComboBox, QDesktopWidget

class ActivateLabelDialog(QDialog):
    correctAnnotationSignal = pyqtSignal(int, str, list)
    def __init__(self, annotationTypeDict):
        super(ActivateLabelDialog, self).__init__()
        self.annotationTypeDict = OrderedDict(annotationTypeDict)
        self.ordered_labels = list(annotationTypeDict.keys())
        self.init_UI(annotationTypeDict)
        self.next_btn.clicked.connect(self.next)
        self.previous_btn.clicked.connect(self.previous)
        self.exit_btn.clicked.connect(self.reject)
        self.annIdx = 0
        self.center()

    def init_UI(self, annotationTypeDict):
        self.setWindowTitle("主动交互窗口")

        self.main_layout = QGridLayout(self)
        label1 = QLabel("模型的结果为：")
        label2 = QLabel("请您确认！")
        self.combobox = QComboBox(self)
        for idx, label_name in enumerate(self.ordered_labels):
            self.combobox.addItem(label_name)
            pixmap = QPixmap(20, 20)
            pixmap.fill(QColor(*annotationTypeDict[label_name]))
            self.combobox.setItemIcon(idx, QIcon(pixmap))

        self.previous_btn = QPushButton("上一项")
        self.next_btn = QPushButton("下一项")
        self.exit_btn = QPushButton("退出")
        self.main_layout.addWidget(label1, 0, 0, 1, 1)
        self.main_layout.addWidget(self.combobox, 1, 1, 1, 2)
        self.main_layout.addWidget(label2, 2, 1, 1, 1)
        self.main_layout.addWidget(self.previous_btn, 3, 0, 1, 1)
        self.main_layout.addWidget(self.next_btn, 3, 1, 1, 1)
        self.main_layout.addWidget(self.exit_btn, 3, 2, 1, 1)

    def center(self):
        # 获取屏幕尺寸和对话框尺寸
        screen = QDesktopWidget().screenGeometry()
        dialog = self.geometry()

        # 计算对话框的居中位置
        x = (screen.width() - dialog.width()) / 2
        y = (screen.height() - dialog.height()) / 2

        # 将对话框移动到居中位置
        self.move(x, y)

    # 设置combobox未打开时显示的模型的推断结果
    def set_combobox_top(self, label_name):
        idx = self.ordered_labels.index(label_name)
        self.combobox.setCurrentIndex(idx)

    def rectify(self):
        idx = self.combobox.currentIndex()
        label_name = self.combobox.itemText(idx)
        self.correctAnnotationSignal.emit(self.annIdx, label_name, self.annotationTypeDict[label_name])

    def next(self):
        self.rectify()
        self.done(1)

    def previous(self):
        self.rectify()
        self.done(-1)

    def update_annIdx(self, annIdx):
        self.annIdx = annIdx

    def exec_(self):
        reply = super().exec_()
        if reply == QDialog.Rejected:
            return QDialog.Rejected
        else:
            return reply

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    annotationTypeDict = {
        "肿瘤区域": [255, 0, 0, 255],
        "基质区域": [0, 0, 255, 255],
        "其他区域": [142, 255, 111, 255]
    }
    dialog = ActivateLabelDialog(annotationTypeDict)
    while True:
        reply = dialog.exec_()
