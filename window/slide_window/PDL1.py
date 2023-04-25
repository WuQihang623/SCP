import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from window.UI.UI_PDL1 import UI_PDL1
from window.slide_window.utils.SlideHelper import SlideHelper

class PDL1Widget(UI_PDL1):
    loadPDL1Signal = pyqtSignal(str)
    loadPairedWidowSignal = pyqtSignal(str, int)
    loadPDL1ComparisonSignal = pyqtSignal(str)
    def __init__(self):
        super(PDL1Widget, self).__init__()
        self.file_dir = './'
        self.setEnable()
        self.setConnect()

    def setEnable(self):
        self.param_btn.setEnabled(False)
        # self.pdl1_btn.setEnabled(False)
        # self.loadComparison_btn.setEnabled(False)
        # self.showComparisionCombox.setEnabled(False)

    def setConnect(self):
        self.loadpdl1_btn.clicked.connect(self.load_result)
        self.pdl1_btn.clicked.connect(self.load_result)
        self.loadComparison_btn.clicked.connect(self.load_comparison_result)

    # 载入当前的文件信息，用于设置保存路径
    def set_slide_path(self, slide_path):
        self.slide_path = slide_path
        self.slide_helper = SlideHelper(slide_path)
        self.wsi_path_text.setText(f"  {slide_path}")

    # 载入PDL1分析结果
    def load_result(self, path):
        slide_name, _ = os.path.splitext(os.path.basename(self.slide_path))
        if not os.path.exists(path) or not isinstance(path, str):
            path = os.path.join('results', 'PD-L1', slide_name, f"{slide_name}.pkl")
            if slide_name not in path:
                QMessageBox.warning(self, '警告', '结果文件与图片不匹配！')
                return
            self.file_dir = os.path.dirname(path)
            self.loadPDL1Signal.emit(path)

    # 载入PDL1对比结果
    def load_comparison_result(self):
        slide_name, _ = os.path.splitext(os.path.basename(self.slide_path))
        # 打开对比窗口
        if os.path.exists(self.slide_path):
            self.loadPairedWidowSignal.emit(self.slide_path, 2)
        else:
            return
        # 选取对比结果，并传给slide_viewer_pair
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self, "选择微环境分析结果存放的路径", self.file_dir,
                                              "结果(*.pkl)", options=options)
        if slide_name not in path:
            QMessageBox.warning(self, '警告', '结果文件与图片不匹配！')
            return
        self.file_dir = os.path.dirname(path)

        self.loadPDL1ComparisonSignal.emit(path)

    # 显示细胞核个数信息
    def setNucleiText(self, num_list):
        self.tumorPosNum_label.setText(f"PD-L1阳性肿瘤细胞数量： {num_list[0]}")
        self.tumorNegNum_label.setText(f"PD-L1阴性肿瘤细胞数量： {num_list[1]}")
        self.immuPosNum_label.setText(f"PD-L1阳性免疫细胞数量:  {num_list[2]}")
        self.immuNegNum_label.setText(f"PD-L1阴性免疫细胞数量: {num_list[3]}")
        self.tps_label.setText(f"TPS:       {num_list[0] / (num_list[0] + num_list[1]) * 100:.2f}%")
        self.cps_label.setText(f"CPS:       {(num_list[2] + num_list[0]) / (num_list[0]+num_list[1]) * 100:.2f}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PDL1Widget()
    window.show()
    sys.exit(app.exec_())