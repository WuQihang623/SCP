import os.path
import sys
from PyQt5.QtWidgets import *
from window.UI.UI_microenv import UI_Microenv
from window.slide_window.utils.SlideHelper import SlideHelper
from PyQt5.QtCore import pyqtSignal

class MicroenvWidget(UI_Microenv):
    # 载入微环境分析结果信号
    loadMicroenvSignal = pyqtSignal(str)
    # 如在微环境对比结果
    loadMicroenvComparisonSignal = pyqtSignal(str)
    # 打开同步窗口信号
    loadPairedWindowSignal = pyqtSignal(str)
    def __init__(self):
        super(MicroenvWidget, self).__init__()
        self.file_dir = self.folderselector.FileDir()

        self.setEnable()
        self.setConnect()

    def setConnect(self):
        self.microenv_btn.clicked.connect(self.load_result)
        self.loadMicroenv_btn.clicked.connect(self.load_result)
        self.loadComparison_btn.clicked.connect(self.load_comparison_result)
        self.folderselector.changeFileDirSignal.connect(self.set_file_dir)

    # 设置按键使能
    def setEnable(self):
        self.param_btn.setEnabled(False)

    # 载入当前的文件信息，用于设置保存路径
    def set_slide_path(self, slide_path):
        self.slide_path = slide_path
        self.slide_helper = SlideHelper(slide_path)
        # self.wsi_path_text.setText(f"  {slide_path}")

    # 载入微环境分析结果
    def load_result(self, path):
        slide_name, _ = os.path.splitext(os.path.basename(self.slide_path))
        # 如果是自己点击加载结果，则执行下面的操作
        if not os.path.exists(path) or not isinstance(path, str):
            path = os.path.join(self.file_dir, slide_name+'.pkl')
            if not os.path.exists(path):
                path = os.path.join(self.file_dir, slide_name, slide_name+'.pkl')
            if not os.path.exists(path) or self.pathchooseBox.isChecked() is False:
                options = QFileDialog.Options()
                path, _ = QFileDialog.getOpenFileName(self, "选择为环境分析结果存放的路径", self.file_dir,
                                                      "结果(*.pkl)", options=options)
        if path == '':
            return
        if not os.path.exists(path):
            QMessageBox.warning(self, '警告', '路径不存在！')
            return
        if slide_name not in path:
            QMessageBox.warning(self, '警告', '结果文件与图片不匹配！')
            return
        self.loadMicroenvSignal.emit(path)

    # 载入对比结果
    def load_comparison_result(self):
        slide_name, _ = os.path.splitext(os.path.basename(self.slide_path))
        # 打开对比窗口
        if os.path.exists(self.slide_path):
            self.loadPairedWindowSignal.emit(self.slide_path)
        else:
            return
        # 选取对比结果，并传给slide_viewer_pair
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self, "选择微环境分析结果存放的路径", self.file_dir,
                                              "结果(*.pkl)", options=options)
        if slide_name not in path:
            QMessageBox.warning(self, '警告', '结果文件与图片不匹配！')
            return
        self.loadMicroenvComparisonSignal.emit(path)

    # 显示细胞核个数信息
    def setNucleiText(self, num_list):
        self.tumorNum_label.setText(f"肿瘤细胞数量： {num_list[0]}")
        self.lymphNum_label.setText(f"淋巴细胞数量： {num_list[1]}")
        self.neutrophilsNum_label.setText(f"中性粒细胞数量:{num_list[3]}")
        self.stromaNum_label.setText(f"基质细胞数量: {num_list[2]}")

    def set_file_dir(self):
        self.file_dir = self.folderselector.FileDir()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MicroenvWidget()
    window.show()
    sys.exit(app.exec_())
