import sys
from PyQt5.QtWidgets import QApplication, QDialog, QRadioButton, QVBoxLayout, QDialogButtonBox, QCheckBox, QSlider, QLabel

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
            return 0, None
        elif self.radio2.isChecked():
            return 1, None
        elif self.radio3.isChecked():
            return 2, None
        elif self.radio4.isChecked():
            return 3, None
        else:
            return None, None

class Channel_Dialog(QDialog):
    def __init__(self, selected_channels, num_markers, marker_names=None, intensities=None):
        super().__init__()
        self.selected_channels = selected_channels
        self.num_check_boxes = num_markers
        self.marker_names = marker_names
        self.intensities = intensities
        self.result_channels = []
        self.slider_values = []  # Store slider values
        self.init_UI()

    def init_UI(self):
        self.setWindowTitle("荧光通道选择")
        layout = QVBoxLayout(self)

        for i in range(self.num_check_boxes):
            if self.marker_names is not None and self.marker_names != []:
                checkbox_text = self.marker_names[i]
            else:
                checkbox_text = f"荧光通道{i}"
            check_box = QCheckBox(checkbox_text)
            layout.addWidget(check_box)

            # Add a slider for each checkbox
            slider = QSlider()
            slider.setOrientation(1)  # Vertical orientation
            slider.setRange(0, 50)  # Values from 0 to 5 with steps of 0.1
            if self.intensities is None:
                slider.setValue(10)  # Initial value set to 1
            else:
                slider.setValue(int(self.intensities[i] * 10))
            self.slider_values.append(slider.value() / 10.0)  # Store initial value
            slider_label = QLabel(f"{self.slider_values[i]:.1f}")
            layout.addWidget(slider)
            layout.addWidget(slider_label)

            # Connect slider value change event to update the label and the stored value
            slider.valueChanged.connect(lambda value, label=slider_label, index=i: self.slider_changed(value, label, index))

            if i in self.selected_channels:
                check_box.setChecked(True)

        # 创建按钮组
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(self.button_box)
        # 连接按钮的点击事件
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def slider_changed(self, value, label, index):
        label.setText(f"{value / 10.0:.1f}")
        self.slider_values[index] = value / 10.0

    def get_selected_option(self):
        return self.result_channels, self.slider_values

    def exec_(self):
        super_result = super().exec_()
        for i in range(self.num_check_boxes * 3):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QCheckBox) and widget.isChecked():
                checkbox_index = self.layout().indexOf(widget)
                self.result_channels.append(int(checkbox_index/3))
        return super_result

if __name__ == '__main__':
    app = QApplication(sys.argv)

    dialog = Channel_Dialog([1, 2, 3, 4], 7)
    if dialog.exec_() == QDialog.Accepted:
        selected_option = dialog.result_channels
        print("选择的选项:", selected_option)
        slider_values = dialog.slider_values
        print(slider_values)

    sys.exit(app.exec_())
