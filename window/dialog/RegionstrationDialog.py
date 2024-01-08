from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class RegistrationTipDialog(QDialog):
    """
        手工配准时的对话框
    """
    def __init__(self):
        super(RegistrationTipDialog, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("手动配准")
        layout = QVBoxLayout()
        label = QLabel("请在两个视图中双击选择配准点", self)
        layout.addWidget(label)
        yes_button = QPushButton("确定", self)
        layout.addWidget(yes_button)
        yes_button.clicked.connect(self.accept)
        cancel_button = QPushButton("取消", self)
        layout.addWidget(cancel_button)
        cancel_button.clicked.connect(self.reject)
        self.setLayout(layout)

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
        self.mode = "manual"
        self.accept()

    def sameImageRegistration(self):
        self.mode = "same"
        self.accept()
    def loadMatrix(self):
        self.mode = "load"
        self.accept()

    def get_mode(self):
        return self.mode