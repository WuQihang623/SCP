from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QDialogButtonBox, QVBoxLayout


class SizeInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ROI的尺寸设置")

        # 创建标签和文本框用于输入宽度
        self.width_label = QLabel("宽度:")
        self.width_line_edit = QLineEdit()
        self.width_line_edit.setText("512")

        # 创建标签和文本框用于输入高度
        self.height_label = QLabel("高度:")
        self.height_line_edit = QLineEdit()
        self.height_line_edit.setText("512")

        # 创建按钮布局
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # 创建主布局并将部件添加到主布局中
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.width_label)
        main_layout.addWidget(self.width_line_edit)
        main_layout.addWidget(self.height_label)
        main_layout.addWidget(self.height_line_edit)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

    def get_size(self):
        """获取用户输入的宽度和高度"""
        try:
            width = int(self.width_line_edit.text())
            height = int(self.height_line_edit.text())
        except:
            width = None
            height = None
        return width, height

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    dialog = SizeInputDialog()
    if dialog.exec_() == QDialog.Accepted:
        width, height = dialog.get_size()
        print("宽度:", width)
        print("高度:", height)
