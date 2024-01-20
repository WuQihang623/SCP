# 弹出是或否的对话框

from PyQt5.QtWidgets import QPushButton, QLabel, QGridLayout, QDialog

class AffirmDialog(QDialog):
    def __init__(self, text):
        super(AffirmDialog, self).__init__()
        self.setWindowTitle("确认")
        label = QLabel(text)
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.close)

        main_layout = QGridLayout(self)
        main_layout.addWidget(label, 1, 0)
        main_layout.addWidget(ok_btn, 2, 0)
        main_layout.addWidget(cancel_btn, 2, 1)

class CloseDialog(QDialog):
    def __init__(self, text):
        super(CloseDialog, self).__init__()
        self.setWindowTitle("保存标注")
        label = QLabel(text)
        ok_btn = QPushButton("保存")
        no_btn = QPushButton("不保存")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.ok)
        no_btn.clicked.connect(self.no)
        cancel_btn.clicked.connect(self.reject)

        main_layout = QGridLayout(self)
        main_layout.addWidget(label, 1, 0, 1, 3)
        main_layout.addWidget(ok_btn, 2, 0)
        main_layout.addWidget(no_btn, 2, 1)
        main_layout.addWidget(cancel_btn, 2, 2)

    def ok(self):
        self.text = '保存'
        self.accept()

    def no(self):
        self.text = '不保存'
        self.reject()