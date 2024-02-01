import sys
from PyQt5.QtWidgets import *

class UI_Diagnose(QWidget):
    def __init__(self):
        super(UI_Diagnose, self).__init__()
        self.init_UI()

    def init_UI(self):
        self.main_layout = QVBoxLayout(self)

        self.label = QLabel("高置信区域")
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.view.viewport().installEventFilter(self)
        policy = QSizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Policy.Expanding)
        policy.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        self.view.setSizePolicy(policy)
        self.report_btn = QPushButton("生成诊断报告")

        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.view)
        self.main_layout.addWidget(self.report_btn)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UI_Diagnose()
    window.show()
    sys.exit(app.exec_())