import json
import sys
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import QSize, pyqtSignal
from function import saveResultFileDir, setResultFileDir


class FolderSelector(QWidget):
    changeFileDirSignal = pyqtSignal()
    def __init__(self, annotation=False):
        super().__init__()
        self.annotation_flag = annotation
        # Create text box to display folder path
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        self.text_box = QLineEdit(self)
        self.text_box.setFont(font)
        self.text_box.setReadOnly(True)

        # Create button to select folder
        self.button = QPushButton("", self)
        icon = QIcon("logo/file.png")
        self.button.setIcon(icon)
        self.button.setFixedSize(24, 24)
        self.button.setIconSize(QSize(24, 24))
        self.button.clicked.connect(self.select_folder)

        # Add widgets to layout
        layout = QHBoxLayout()
        layout.addWidget(self.text_box)
        layout.addWidget(self.button)

        # Set the main layout for the window
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(layout)

        # 初始化结果文件存放地址
        self.set_text()

    def select_folder(self):
        # Open a file dialog to select a folder
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_path:
            # If a folder was selected, display its path in the text box
            self.text_box.setText(folder_path)
            saveResultFileDir(folder_path, self.annotation_flag)
            self.changeFileDirSignal.emit()

    def select_annotation_folder(self):
        # Open a file dialog to select a folder
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_path:
            # If a folder was selected, display its path in the text box
            self.text_box.setText(folder_path)
            saveResultFileDir(folder_path, self.annotation_flag)
            self.changeFileDirSignal.emit()

    def set_text(self):
        self.text_box.setText(setResultFileDir(self.annotation_flag))

    def FileDir(self):
        return self.text_box.text()


if __name__ == "__main__":
    # Create an instance of the FolderSelector class and show the window
    app = QApplication(sys.argv)
    folder_selector = FolderSelector()
    print(folder_selector.FileDir())
    folder_selector.show()
    sys.exit(app.exec_())