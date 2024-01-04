import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from window.utils.ComCheckbox import ComboCheckBox
from window.utils.FolderSelector import FolderSelector

class UI_Microenv(QFrame):
    def __init__(self):
        super(UI_Microenv, self).__init__()
        self.init_UI()

    def init_UI(self):
        main_layout = QVBoxLayout(self)

        microenvBox = QGroupBox(self)
        microenvBox.setTitle('肿瘤微环境分析')

        box_layout = QGridLayout()
        box_layout.setContentsMargins(10, 0, 20, 0)
        self.folderselector = FolderSelector()
        self.pathchooseBox = QCheckBox("是否自动选择路径")
        self.pathchooseBox.setChecked(True)
        self.param_btn = QPushButton("参数设置")
        self.microenv_btn = QPushButton("微环境分析")
        self.loadMicroenv_btn = QPushButton("载入微环境分析结果")
        show_label = QLabel("显示内容：")
        self.showCombox = ComboCheckBox(['显示热图', '显示肿瘤区域轮廓', '显示细胞核轮廓'])
        self.loadComparison_btn = QPushButton("载入对比结果")
        self.loadRegistration_btn = QPushButton("载入配准结果")
        self.showComparisionCombox = ComboCheckBox(['显示热图', '显示肿瘤区域轮廓', '显示细胞核轮廓'])
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)

        showNucleiType_Label = QLabel("细胞核显示：")
        showRegionType_Label = QLabel("肿瘤区域显示：")
        self.showNucleiType_Combox = ComboCheckBox(['背景类别', '表皮细胞', '淋巴细胞', '中性粒细胞', '基质细胞'],
                                                    [[166, 84, 2], [255, 0, 0], [0, 255, 0], [0, 0, 255], [228, 252, 4]])
        self.showRegionType_Combox = ComboCheckBox(['肿瘤区域', '基质区域', '坏死区域', '无关区域', "图像块"],
                                                   [[255, 0, 0], [0, 0, 255], [0, 255, 0], [255, 255, 255], [0, 0, 0]])
        self.show_hierarchy_mask_checkbox = QCheckBox("显示层级区域")
        self.show_hierarchy_mask_checkbox.setChecked(False)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        label = QLabel("肿瘤微环境分析结果")
        # label.setStyleSheet("font-weight: bold;")
        label.setAlignment(Qt.AlignCenter)
        self.tumorNum_label = QLabel("肿瘤细胞数量：")
        self.lymphNum_label = QLabel("淋巴细胞数量：")
        self.neutrophilsNum_label = QLabel("中性粒细胞数量：")
        self.stromaNum_label = QLabel("基质细胞数量：")
        line3 = QFrame()
        line3.setFrameShape(QFrame.HLine)
        line3.setFrameShadow(QFrame.Sunken)
        null = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)

        box_layout.addWidget(self.folderselector, 1, 0, 1, 2)
        box_layout.addWidget(self.pathchooseBox, 2, 0, 1, 2)
        box_layout.addWidget(self.microenv_btn, 3, 0, 1, 2)
        box_layout.addWidget(self.loadComparison_btn, 4, 0, 1, 2)
        box_layout.addWidget(self.loadRegistration_btn, 5, 0, 1, 2)
        box_layout.addWidget(line2, 6, 0, 1, 2)
        box_layout.addWidget(label, 7, 0, 1, 2)
        box_layout.addWidget(self.tumorNum_label, 8, 0, 1, 2)
        box_layout.addWidget(self.lymphNum_label, 9, 0, 1, 2)
        box_layout.addWidget(self.neutrophilsNum_label, 10, 0, 1, 2)
        box_layout.addWidget(self.stromaNum_label, 11, 0, 1, 2)
        box_layout.addWidget(line3, 12, 0, 1, 2)

        box_layout.addWidget(show_label, 13, 0, 1, 1)
        box_layout.addWidget(self.showCombox, 13, 1, 1, 1)
        box_layout.addWidget(showNucleiType_Label, 14, 0, 1, 1)
        box_layout.addWidget(self.showNucleiType_Combox, 14, 1, 1, 1)
        box_layout.addWidget(showRegionType_Label, 15, 0, 1, 1)
        box_layout.addWidget(self.showRegionType_Combox, 15, 1, 1, 1)
        box_layout.addWidget(self.show_hierarchy_mask_checkbox, 16, 0, 1, 1)

        box_layout.addItem(null, 17, 0, 1, 2)
        box_layout.setVerticalSpacing(15)

        microenvBox.setLayout(box_layout)
        main_layout.addWidget(microenvBox)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UI_Microenv()
    window.show()
    sys.exit(app.exec_())
