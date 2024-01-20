# 修改标注类别时的对话框

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtGui import  QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import  QPushButton, QLabel, QGridLayout, QDialog, QComboBox

class ChangeNucleusDiaglog(QDialog):
    def __init__(self, nucleus_info):
        super(ChangeNucleusDiaglog, self).__init__()
        self.setWindowTitle("修改细胞核类别")
        self.nucleus_info = nucleus_info
        self.init_layout()

    def init_layout(self):
        self.text = QLabel("细胞类别：")
        self.combobox = QComboBox(self)
        for i, (name, item) in enumerate(self.nucleus_info.items()):
            self.combobox.addItem(name)
            pixmap = QPixmap(20, 20)
            pixmap.fill(QColor(*item["color"]))
            self.combobox.setItemIcon(i, QIcon(pixmap))

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

    def get_idx(self):
        return self.combobox.currentIndex()

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    dialog = ChangeNucleusDiaglog({
                    "肿瘤细胞": {"type": 1, "color": [255, 0, 0], "number": 1000},
                    "淋巴细胞": {"type": 2, "color": [0, 255, 0], "number": 1000},
                    "中性粒细胞": {"type": 3, "color": [255, 255, 0], "number": 1000},
                    "基质细胞": {"type": 4, "color": [0, 0, 255], "number": 1000},
                })
    if dialog.exec_() == QDialog.Accepted:
        text = dialog.get_text()
        print(text)
    app.exit()