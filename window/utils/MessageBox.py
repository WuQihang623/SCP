from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton


class CustomMessageBox(QDialog):
    def __init__(self, title, message):
        super().__init__()
        # 设置窗口标题
        self.setWindowTitle(title)
        ico = QIcon("logo/logo.ico")
        self.setWindowIcon(ico)

        # 创建垂直布局
        layout = QVBoxLayout(self)
        message_label = QLabel(self)
        message_label.setText(message)
        message_label.setAlignment(Qt.AlignCenter)  # 居中对齐
        layout.addWidget(message_label)

        # 获取标签内容大小，并设置为窗口大小
        self.setFixedSize(message_label.sizeHint().width() + 100,
                          message_label.sizeHint().height() + 100)
        # 创建按钮，关闭窗口
        ok_button = QPushButton('确定', self)
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

    def run(self):
        # 显示消息框，并等待关闭
        return self.exec_()


if __name__ == '__main__':
    app = QApplication([])
    message_box = CustomMessageBox('警告', '参数设置错误！')
    message_box.run()
