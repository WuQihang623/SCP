import sys
from PyQt5.QtWidgets import QApplication, QDialog, QRadioButton, QVBoxLayout, QDialogButtonBox

class ColorSpaceDialog(QDialog):
    def __init__(self, colorspace):
        super().__init__()

        self.setWindowTitle("颜色空间选择")

        # 创建选择框
        self.radio1 = QRadioButton("RGB颜色空间")
        self.radio2 = QRadioButton("Hematoxylin颜色空间")
        self.radio3 = QRadioButton("DAB颜色空间")
        if colorspace == 0:
            self.radio1.setChecked(True)
        elif colorspace == 1:
            self.radio2.setChecked(True)
        else:
            self.radio3.setChecked(True)

        # 创建按钮组
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        # 将选择框和按钮组放入布局
        layout = QVBoxLayout()
        layout.addWidget(self.radio1)
        layout.addWidget(self.radio2)
        layout.addWidget(self.radio3)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        # 连接按钮的点击事件
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def get_selected_option(self):
        if self.radio1.isChecked():
            return 0
        elif self.radio2.isChecked():
            return 1
        elif self.radio3.isChecked():
            return 2
        else:
            return None


if __name__ == '__main__':
    app = QApplication(sys.argv)

    dialog = ColorSpaceDialog(0)
    if dialog.exec_() == QDialog.Accepted:
        selected_option = dialog.get_selected_option()
        print("选择的选项:", selected_option)

    sys.exit(app.exec_())
