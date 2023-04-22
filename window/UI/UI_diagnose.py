import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from window.utils.FolderSelector import FolderSelector


class UI_Diagnose(QWidget):
    def __init__(self):
        super(UI_Diagnose, self).__init__()
        self.init_UI()

    def init_UI(self):
        mainlayout = QVBoxLayout(self)
        diagnoseBox = QGroupBox()
        diagnoseBox.setTitle('前哨淋巴结转移诊断')

        btn_layout = QGridLayout()
        btn_layout.setVerticalSpacing(25)
        btn_layout.setHorizontalSpacing(20)
        self.folderselector = FolderSelector()
        self.diagnose_btn = QPushButton("诊断")
        self.loadDiagnoseResults_btn = QPushButton("载入诊断结果")
        self.showHeatmap_btn = QPushButton("显示热图")
        self.showHeatmap_btn.setCheckable(True)
        self.showHeatmap_btn.setChecked(False)
        self.diagnoseConclusion_label = QLabel("诊断结果：")
        self.diagnoseProb_label = QLabel("置信度：")


        # 用于显示置信度高的区域patch的图像
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.view.viewport().installEventFilter(self)
        policy = QSizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Policy.Expanding)
        policy.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        self.view.setSizePolicy(policy)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        btn_layout.addWidget(self.folderselector, 0, 0, 1, 1)
        btn_layout.addWidget(self.diagnose_btn, 1, 0, 1, 1)
        btn_layout.addWidget(self.loadDiagnoseResults_btn, 2, 0, 1, 1)
        btn_layout.addWidget(self.showHeatmap_btn, 3, 0, 1, 1)
        btn_layout.addWidget(self.diagnoseConclusion_label, 4, 0, 1, 1)
        btn_layout.addWidget(self.diagnoseProb_label, 5, 0, 1, 1)
        btn_layout.addWidget(line, 6, 0, 1, 1)

        diagnoseBox.setLayout(btn_layout)
        mainlayout.addWidget(diagnoseBox)
        mainlayout.addWidget(self.view)

        self.show_report_btn = QPushButton("生成诊断报告")
        mainlayout.addWidget(self.show_report_btn)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet())
    window = UI_Diagnose()
    window.show()
    sys.exit(app.exec_())
