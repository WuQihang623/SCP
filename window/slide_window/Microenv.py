import os.path
import pickle
import sys

import numpy as np
from PyQt5.QtWidgets import *
from window.UI.UI_microenv import UI_Microenv
from window.slide_window.utils.SlideHelper import SlideHelper
from PyQt5.QtCore import pyqtSignal

class MicroenvWidget(UI_Microenv):
    # 载入微环境分析结果信号
    loadMicroenvSignal = pyqtSignal(str)
    # 载入微环境对比结果
    loadMicroenvComparisonSignal = pyqtSignal(str)
    # 打开同步窗口信号
    loadPairedWindowSignal = pyqtSignal(str)
    # 载入配准结果到HE窗口信号
    loadOriginRegSignal = pyqtSignal(dict)
    # 载入配准结果到IHC窗口信号
    loadTransformRegSignal = pyqtSignal(dict)
    # 通知slide_viewer_pair绑定配准结果导入信号
    loadRegistrationSignal = pyqtSignal(bool)
    def __init__(self):
        super(MicroenvWidget, self).__init__()
        self.file_dir = self.folderselector.FileDir()

        self.setEnable()
        self.setConnect()

    def setConnect(self):
        """
            设置界面按键的信号连接
        """
        self.microenv_btn.clicked.connect(self.load_result)
        self.loadMicroenv_btn.clicked.connect(self.load_result)
        self.loadComparison_btn.clicked.connect(self.load_comparison_result)
        self.loadRegistration_btn.clicked.connect(self.load_registration_results)
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
        # 选取对比结果，并传给slide_viewer_pair
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self, "选择微环境分析结果存放的路径", self.file_dir,
                                              "结果(*.pkl)", options=options)
        if slide_name not in path:
            QMessageBox.warning(self, '警告', '结果文件与图片不匹配！')
            return

        # 打开对比窗口
        if os.path.exists(self.slide_path):
            self.loadPairedWindowSignal.emit(self.slide_path)
        else:
            return
        self.loadMicroenvComparisonSignal.emit(path)


    def load_registration_results(self):
        """同时载入HE与IHC或荧光图像的细胞核分割结果，二者公用一个type?

        载入文件的格式:
            {
               哈希值1: {
                   'type': ndarray,
                   'center': ndarray,
                   'contour': ndarray,
                   'grid': ndarray,
                   'ihc_center': ndarray,
                   'ihc_contour': ndarray,
                   'ihc_grid': ndarray,
               },
            }

        """
        slide_name, _ = os.path.splitext(os.path.basename(self.slide_path))
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self, "选择配准结果存放路径", self.file_dir,
                                              "结果(*.pkl)", options=options)
        if slide_name not in path:
            QMessageBox.warning(self, '警告', '结果文件与图片不匹配！')
            return

        with open(path, "rb") as f:
            Reg_data = pickle.load(f)
            f.close()
        # TODO: 由于这并不是一个频繁的信号促发，因此在这里使用信号传递结果文件
        origin_dict = self.get_empty_result_dict()
        transform_dict = self.get_empty_result_dict()
        for hash, patch_item in Reg_data.items():
            origin_dict["center"].extend(patch_item["center"])
            origin_dict["contour"].extend(patch_item["contour"])
            origin_dict["type"].extend(patch_item["type"])
            origin_dict["grid"].append(self.convert_grid_matrix(patch_item["grid"]))
            transform_dict["center"].extend(patch_item["ihc_center"])
            transform_dict["contour"].extend(patch_item["ihc_contour"])
            transform_dict["type"].extend(patch_item["type"])
            transform_dict["grid"].append(self.convert_grid_matrix(patch_item["ihc_grid"]))
        for key, _ in origin_dict.items():
            if key == "contour":
                origin_dict[key] = np.array(origin_dict[key], dtype=object)
            else:
                origin_dict[key] = np.array(origin_dict[key], dtype=np.int32)
        for key, _ in transform_dict.items():
            if key == "contour":
                transform_dict[key] = np.array(transform_dict[key], dtype=object)
            else:
                transform_dict[key] = np.array(transform_dict[key], dtype=np.int32)

        self.loadRegistrationSignal.emit(True)
        self.loadOriginRegSignal.emit(origin_dict)
        self.loadTransformRegSignal.emit(transform_dict)

    # 显示细胞核个数信息
    def setNucleiText(self, num_list):
        self.tumorNum_label.setText(f"肿瘤细胞数量： {num_list[0]}")
        self.lymphNum_label.setText(f"淋巴细胞数量： {num_list[1]}")
        self.neutrophilsNum_label.setText(f"中性粒细胞数量:{num_list[3]}")
        self.stromaNum_label.setText(f"基质细胞数量: {num_list[2]}")

    def set_file_dir(self):
        self.file_dir = self.folderselector.FileDir()

    def convert_grid_matrix(self, grid):
        """
            将一个2*2矩阵（xyxy）转换成4*2矩阵（xyxyxyxy）
        """
        return np.array([
            [grid[0][0], grid[0][1]], # 左上角
            [grid[0][0], grid[1][1]], # 右上角
            [grid[1][0], grid[1][1]], # 右下角
            [grid[1][0], grid[0][1]], # 左下角
        ], dtype=np.int32)

    def get_empty_result_dict(self):
        return {
            "type": [],
            "center": [],
            "contour": [],
            "grid": []
        }

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MicroenvWidget()
    window.show()
    sys.exit(app.exec_())
