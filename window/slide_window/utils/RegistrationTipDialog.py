import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton

class RegistrationTipDialog(QDialog):
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