import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QSlider, QPushButton, QLabel
from PyQt5.QtCore import Qt


class heatmap_alpha_Dialog(QDialog):
    def __init__(self, initial_value=0.5):
        super().__init__()

        # 设置对话框的标题
        self.setWindowTitle("滑块对话框")

        # 固定窗口大小
        self.setFixedSize(300, 150)

        # 垂直布局
        layout = QVBoxLayout()

        # 创建滑块并设置范围和分辨率
        self.slider = QSlider()
        self.slider.setOrientation(1)  # 设置为垂直滑块
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setSingleStep(1)

        # 设置初始值
        self.slider.setValue(int(initial_value * 100))

        # 添加滑块到布局
        layout.addWidget(self.slider)

        # 添加刻度标签
        self.label0 = QLabel("0")
        self.label0.setAlignment(Qt.AlignCenter)  # 居中对齐
        layout.addWidget(self.label0)

        # 创建确定按钮
        self.button_ok = QPushButton("确定")
        self.button_ok.clicked.connect(self.accept)

        # 添加按钮到布局
        layout.addWidget(self.button_ok)

        # 设置布局
        self.setLayout(layout)

        # 为滑块数值变化信号连接更新刻度标签的槽函数
        self.slider.valueChanged.connect(self.update_labels)

        # 更新刻度标签
        self.update_labels()

    def update_labels(self):
        # 获取滑块的值，转换为0到1的范围
        value = self.slider.value() / 100
        self.label0.setText(f"{value:.2f}")

    def get_slider_value(self):
        value = self.slider.value() / 100
        return value

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 传入初始值（0.5为默认值）
    dialog = heatmap_alpha_Dialog(initial_value=0.3)

    # 显示对话框
    result = dialog.exec_()

    # 在确定按钮点击后，输出滑块的值
    if result == QDialog.Accepted:
        print("滑块的值为:", dialog.get_slider_value())
