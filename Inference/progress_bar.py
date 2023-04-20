from PyQt5.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QDialog
from PyQt5.QtCore import Qt


class progress_dialog(QDialog):
    def __init__(self, title, text):
        super(progress_dialog, self).__init__()
        self.setWindowTitle(title)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Widget)
        self.label = QLabel(text)
        self.progressBar = QProgressBar()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.progressBar)
        self.value = 0
        self.progressBar.setValue(self.value)
        self.progressBar.setStyleSheet(
            "QProgressBar { font: 75 14pt \"Times New Roman\"; border: 2px solid grey; border-radius: 5px; color: rgb(20,20,20);  background-color: #FFFFFF; text-align: center;}QProgressBar::chunk {background-color: rgb(100,200,200); border-radius: 10px; margin: 0.1px;  width: 1px;}")
        self.progressBar.setStyleSheet(
            "QProgressBar { font: 75 14pt \"Times New Roman\"; border: 2px solid grey; border-radius: 5px; background-color: #FFFFFF; text-align: center;}QProgressBar::chunk {background:QLinearGradient(x1:0,y1:0,x2:2,y2:0,stop:0 #666699,stop:1  #DB7093); }")

    def call_back(self, length, idx, *args):
        idx = int(100/length*(idx+1))
        self.progressBar.setValue(idx)
        if idx == 100:
            self.close()

    def start(self):
        self.show()

# class progress_dialog(QDialog):
#     def __init__(self, title='', text=''):
#         super().__init__()
#         self.setWindowTitle('')
#         # self.setWindowModality(Qt.ApplicationModal)
#         # self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
#         self.setWindowModality(Qt.ApplicationModal)
#         self.setWindowFlags(Qt.Widget)
#         self.label = QLabel('请稍等...')
#         self.progressBar = QProgressBar()
#         self.main_layout = QVBoxLayout(self)
#         self.main_layout.addWidget(self.label)
#         self.main_layout.addWidget(self.progressBar)
#         self.value = 0
#         self.progressBar.setValue(self.value)
#         self.progressBar.setStyleSheet(
#             "QProgressBar { font: 75 14pt \"Times New Roman\"; border: 2px solid grey; border-radius: 5px; color: rgb(20,20,20);  background-color: #FFFFFF; text-align: center;}QProgressBar::chunk {background-color: rgb(100,200,200); border-radius: 10px; margin: 0.1px;  width: 1px;}")
#         self.progressBar.setStyleSheet(
#             "QProgressBar { font: 75 14pt \"Times New Roman\"; border: 2px solid grey; border-radius: 5px; background-color: #FFFFFF; text-align: center;}QProgressBar::chunk {background:QLinearGradient(x1:0,y1:0,x2:2,y2:0,stop:0 #666699,stop:1  #DB7093); }")
#
#
#     def call_back(self, length, idx):
#         idx = int(100/length*(idx+1))
#         self.progressBar.setValue(idx)
#         if idx == 100:
#             self.close()