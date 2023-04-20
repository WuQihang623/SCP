# 增加类别时的对话框

from PyQt5.QtWidgets import QDialog, QGridLayout, QLineEdit, QPushButton, QColorDialog, QLabel
from PyQt5.QtGui import QColor

class ColorChooseDialog(QDialog):
    def __init__(self, parent=None):
        super(ColorChooseDialog, self).__init__()
        self.init_UI()

    def init_UI(self):
        self.setWindowTitle("设置类别以及颜色")
        main_layout = QGridLayout(self)
        main_layout.setSpacing(25)
        self.textbox = QLineEdit()
        self.color_label = QLabel("  ")
        self.color_choose_btn = QPushButton("选择颜色")
        btn_ok = QPushButton("确定")
        btn_cancel = QPushButton("取消")

        main_layout.addWidget(self.textbox, 0, 0, 1, 1)
        main_layout.addWidget(self.color_label, 0, 1, 1, 1)
        main_layout.addWidget(self.color_choose_btn, 1, 0, 1, 2)
        main_layout.addWidget(btn_ok, 2, 0, 1, 1)
        main_layout.addWidget(btn_cancel, 2, 1, 1, 1)

        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        self.color_choose_btn.clicked.connect(self.choose_color)

        # 设置默认颜色为黑色
        self.color = QColor(0, 0, 0)

    def choose_color(self):
        color = QColorDialog.getColor(self.color, self, "选择颜色")
        if color.isValid():
            self.color = color
            self.color_label.setStyleSheet('background-color: %s' % self.color.name())

    def get_text(self):
        return self.textbox.text()

    def get_color(self):
        return self.color


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    dialog = ColorChooseDialog()
    if dialog.exec_() == QDialog.Accepted:
        text = dialog.get_text()
        color = dialog.get_color()
        print(text, color)
    app.exit()
