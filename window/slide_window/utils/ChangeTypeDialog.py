# 更换类别时的对话框

from PyQt5.QtWidgets import QDialog, QGridLayout, QLineEdit, QPushButton, QColorDialog, QLabel
from PyQt5.QtGui import QColor

class ChangeTypeDialog(QDialog):
    def __init__(self):
        super(ChangeTypeDialog, self).__init__()
        self.setWindowTitle('修改类别')
        self.label = QLabel('请输入类别:')
        self.edit = QLineEdit(self)
        btn_ok = QPushButton(self)
        btn_ok.setText('确定')
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton(self)
        btn_cancel.setText('取消')
        btn_cancel.clicked.connect(self.reject)
        self.main_layout = QGridLayout(self)
        self.main_layout.addWidget(self.label, 1, 1, 1, 2)
        self.main_layout.addWidget(self.edit, 1, 3, 1, 2)
        self.main_layout.addWidget(btn_ok, 2, 2, 1, 1)
        self.main_layout.addWidget(btn_cancel, 2, 4, 1, 1)

    def get_text(self):
        return self.edit.text()

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    dialog = ChangeTypeDialog()
    if dialog.exec_() == QDialog.Accepted:
        text = dialog.get_text()
        print(text)
    app.exit()