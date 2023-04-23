import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from window.utils.ComCheckbox import ComboCheckBox
from window.utils.FolderSelector import FolderSelector

class UI_PDL1(QFrame):
    def __init__(self):
        super(UI_PDL1, self).__init__()
        self.init_UI()

    def init_UI(self):
        main_layout = QVBoxLayout(self)

        pdl1Box = QGroupBox(self)
        pdl1Box.setTitle('PD-L1评分')

        box_layout = QGridLayout()
        box_layout.setContentsMargins(10, 0, 20, 0)
        self.folderselector = FolderSelector()
        self.wsi_path_label = QLabel("输入WSI图像")
        self.wsi_path_label.setStyleSheet("font-weight: bold;")
        self.wsi_path_label.setAlignment(Qt.AlignCenter)
        self.wsi_path_text = QLabel("")
        self.param_btn = QPushButton("参数设置")
        self.pdl1_btn = QPushButton("PD-L1评分")
        self.loadpdl1_btn = QPushButton("载入PD-L1分析结果")
        self.showCombox = ComboCheckBox(['显示热图', '显示肿瘤区域轮廓', '显示细胞核轮廓'])
        self.loadComparison_btn = QPushButton("载入对比结果")
        self.showComparisionCombox = ComboCheckBox(['显示热图', '显示肿瘤区域轮廓', '显示细胞核轮廓'])
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)

        showNucleiType_Label = QLabel("细胞核显示：")
        showRegionType_Label = QLabel("肿瘤区域显示：")
        self.showNucleiType_Combox = ComboCheckBox(['背景类别' ,'PD-L1阳性肿瘤细胞', 'PD-L1阴性肿瘤细胞', 'PD-L1阳性免疫细胞', 'PD-L1阴性免疫细胞'],
                                                   [[166, 84, 2], [255, 0, 0], [0, 255, 0], [228, 252, 4], [0, 0, 255]])
        self.showRegionType_Combox = ComboCheckBox(['肿瘤区域'],
                                                   [[0, 0, 255]])

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        label = QLabel("PD-L1评分结果")
        label.setStyleSheet("font-weight: bold;")
        label.setAlignment(Qt.AlignCenter)
        self.tumorPosNum_label = QLabel("PD-L1阳性肿瘤细胞数量：")
        self.tumorNegNum_label = QLabel("PD-L1阴性肿瘤细胞数量：")
        self.immuPosNum_label = QLabel("PD-L1阳性免疫细胞数量：")
        self.immuNegNum_label = QLabel("PD-L1阴性免疫细胞数量：")
        self.tps_label = QLabel("TPS:")
        self.tps_label.setStyleSheet("font-weight: bold;")
        self.cps_label = QLabel("CPS:")
        self.cps_label.setStyleSheet("font-weight: bold;")
        line3 = QFrame()
        line3.setFrameShape(QFrame.HLine)
        line3.setFrameShadow(QFrame.Sunken)
        null = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)



        # box_layout.addWidget(self.folderselector, 0, 0, 1, 2)
        box_layout.addWidget(self.wsi_path_label, 0, 0, 1, 2)
        box_layout.addWidget(self.wsi_path_text, 1, 0, 1, 2)
        # box_layout.addWidget(self.param_btn, 1, 0, 1, 1)
        # box_layout.addWidget(self.pdl1_btn, 1, 1, 1, 1)
        box_layout.addWidget(self.pdl1_btn, 2, 0, 1, 1)
        box_layout.addWidget(self.showCombox, 2, 1, 1, 1)
        box_layout.addWidget(self.loadComparison_btn, 3, 0, 1, 1)
        box_layout.addWidget(self.showComparisionCombox, 3, 1 ,1, 1)
        box_layout.addWidget(line2, 4, 0, 1, 2)
        box_layout.addWidget(label, 5, 0, 1, 2)
        box_layout.addWidget(self.tumorPosNum_label, 6, 0, 1, 2)
        box_layout.addWidget(self.tumorNegNum_label, 7, 0, 1, 2)
        box_layout.addWidget(self.immuPosNum_label, 8, 0, 1, 2)
        box_layout.addWidget(self.immuNegNum_label, 9, 0, 1, 2)
        box_layout.addWidget(self.tps_label, 10, 0, 1, 2)
        box_layout.addWidget(self.cps_label, 11, 0, 1, 2)
        box_layout.addWidget(line3, 12, 0, 1, 2)

        # box_layout.addWidget(line1, 4, 0, 1, 2)
        box_layout.addWidget(showNucleiType_Label, 13, 0, 1, 1)
        box_layout.addWidget(self.showNucleiType_Combox, 13, 1, 1, 1)
        box_layout.addWidget(showRegionType_Label, 14, 0, 1, 1)
        box_layout.addWidget(self.showRegionType_Combox, 14, 1, 1, 1)

        box_layout.addItem(null, 15, 0, 1, 2)
        box_layout.setVerticalSpacing(25)

        pdl1Box.setLayout(box_layout)
        main_layout.addWidget(pdl1Box)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UI_PDL1()
    window.show()
    sys.exit(app.exec_())