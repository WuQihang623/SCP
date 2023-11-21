import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont

class RegistrationDialog(QDialog):
    def __init__(self):
        super(RegistrationDialog, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("配准方式选择")
        layout = QVBoxLayout()
        label = QLabel("请选择配准方式", self)
        font = QFont("宋体", 12)
        label.setFont(font)
        layout.addWidget(label)
        manual_button = QPushButton("手动取点", self)
        # 使用样式表设置按键的字体
        manual_button.setFont(font)
        layout.addWidget(manual_button)
        manual_button.clicked.connect(self.manualRegistration)
        same_image_button = QPushButton("相同的图像", self)
        # 使用样式表设置按键的字体
        same_image_button.setFont(font)
        layout.addWidget(same_image_button)
        same_image_button.clicked.connect(self.sameImageRegistration)
        load_matrix_button = QPushButton("载入变换矩阵", self)
        load_matrix_button.clicked.connect(self.loadMatrix)
        load_matrix_button.setFont(font)
        layout.addWidget(load_matrix_button)
        cancel_button = QPushButton("取消", self)
        cancel_button.setFont(font)
        layout.addWidget(cancel_button)
        cancel_button.clicked.connect(self.reject)
        self.setLayout(layout)

    def manualRegistration(self):
        self.match_by_hand = 1
        self.accept()

    def sameImageRegistration(self):
        self.match_by_hand = 2
        self.accept()
    def loadMatrix(self):
        self.match_by_hand = 3
        self.accept()

    def get_flag(self):
        return self.match_by_hand

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = RegistrationDialog()
    dialog.exec()
    sys.exit(app.exec_())
