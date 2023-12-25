import sys
from PyQt5.QtWidgets import QApplication, QDialog, QRadioButton, QVBoxLayout, QDialogButtonBox, QCheckBox

class ColorSpaceDialog(QDialog):
    def __init__(self, colorspace):
        '''
        :param colorspace: int 当前选择的颜色空间
        '''
        super().__init__()
        self.setWindowTitle("颜色空间选择")
        # 创建选择框
        self.radio1 = QRadioButton("RGB颜色空间")
        self.radio2 = QRadioButton("Hematoxylin颜色空间")
        self.radio3 = QRadioButton("DAB颜色空间")
        self.radio4 = QRadioButton("染色标准化")
        if colorspace == 0:
            self.radio1.setChecked(True)
        elif colorspace == 1:
            self.radio2.setChecked(True)
        elif colorspace == 2:
            self.radio3.setChecked(True)
        else:
            self.radio4.setChecked(True)
        # 创建按钮组
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        # 将选择框和按钮组放入布局
        layout = QVBoxLayout()
        layout.addWidget(self.radio1)
        layout.addWidget(self.radio2)
        layout.addWidget(self.radio3)
        layout.addWidget(self.radio4)
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
        elif self.radio4.isChecked():
            return 3
        else:
            return None


class Channel_Dialog(QDialog):
    four_channel = ["DAPI", "Opal 520", "Opal 570", "Opal 620", "Sample AF"]
    seven_channel = ["DAPI", "CD3 570", "CD66b 520", "LOX-1 690", "FATP2 480", "ACSL4 780", "PanCK 620", "Sample AF"]
    def __init__(self, selected_channels, num_markers):
        super().__init__()
        self.selected_channels = selected_channels
        self.num_check_boxes = num_markers
        self.result_channels = []
        self.init_UI()

    def init_UI(self):
        self.setWindowTitle("荧光通道选择")
        layout = QVBoxLayout(self)
        for i in range(self.num_check_boxes):
            if self.num_check_boxes == 8:
                check_box = QCheckBox(self.seven_channel[i])
            elif self.num_check_boxes == 5:
                check_box = QCheckBox(self.four_channel[i])
            else:
                check_box = QCheckBox(f"荧光通道{i}")
            layout.addWidget(check_box)
            if i in self.selected_channels:
                check_box.setChecked(True)
        # 创建按钮组
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(self.button_box)
        # 连接按钮的点击事件
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def get_selected_option(self):
        return self.result_channels

    def exec_(self):
        super_result = super().exec_()
        for i in range(self.num_check_boxes):
            if self.layout().itemAt(i).widget().isChecked():
                self.result_channels.append(i)
        return super_result

if __name__ == '__main__':
    app = QApplication(sys.argv)

    dialog = Channel_Dialog([1, 2, 3, 4], 7)
    if dialog.exec_() == QDialog.Accepted:
        selected_option = dialog.result_channels
        print("选择的选项:", selected_option)

    sys.exit(app.exec_())
