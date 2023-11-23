import json
import os
import pickle
import sys

import cv2
import constants
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QEvent
from window.UI.UI_Multimodal import UI_Multimodal

class MultimodalWidget(UI_Multimodal):
    heatmapSignal = pyqtSignal(object, object, bool)
    comparison_heatmapSignal = pyqtSignal(object, object, bool)
    # 打开同步窗口信号
    loadPairedWindowSignal = pyqtSignal(str)
    def __init__(self):
        super(UI_Multimodal, self).__init__()
        self.init_UI()
        self.file_dir = self.folderselector.FileDir()
        self.slide_path = None
        self.heatmap_list = []
        self.heatmap_downsample = None

        self.comparison_heatmap_list = []
        self.comparison_heatmap_downsample = None
        # 连接信号
        self.connect_btn()

    def connect_btn(self):
        self.load_btn.clicked.connect(self.load_result)
        self.load_comparison_btn.clicked.connect(self.load_comparison_result)
        self.folderselector.changeFileDirSignal.connect(self.set_file_dir)

    def set_file_dir(self):
        self.file_dir = self.folderselector.FileDir()

    def set_slide_path(self, slide_path):
        self.slide_path = slide_path

    def load_result(self):
        if self.slide_path is None or not os.path.exists(self.slide_path): return
        slide_name = os.path.splitext(os.path.basename(self.slide_path))[0]
        path = os.path.join(self.file_dir, slide_name + '.pkl')
        if not os.path.exists(path):
            options = QFileDialog.Options()
            path, _ = QFileDialog.getOpenFileName(self, "选择多模态可视化热图", self.file_dir,
                                                  "*热图(*.pkl)", options=options)
        if path == '':
            return
        if not os.path.exists(path):
            QMessageBox(self, '警告', "路径不存在！")
            return
        if slide_name not in path:
            QMessageBox.warning(self, '警告', '结果文件与图片不匹配！')
            return

        with open(path, 'rb') as f:
            data = pickle.load(f)
            f.close()
        try:
            """
            data的格式， dict
            key: heatmap heatmap_downsample
            heatmap 中存放的也是一个字典，里面的key是模态名，value是heatmap
            """
            self.heatmap_list = []
            modal_list = []
            heatmap_dict = data["heatmap"]
            self.heatmap_downsample = data["heatmap_downsample"]
            for modal_name, heatmap in heatmap_dict.items():
                modal_list.append(modal_name)
                self.heatmap_list.append(heatmap)
            if len(self.heatmap_list) == 0:
                self.heatmap_list = []
                self.heatmap_downsample = None
                QMessageBox.warning(self, "警告", "文件缺失！")
                return
            self.load_checkbox(modal_list)
            if self.modal_check is not None:
                self.modal_check.checkbox_list[0].setChecked(True)

        except Exception as e:
            self.heatmap_list = []
            self.heatmap_downsample = None
            QMessageBox.warning(self, "警告", str(e))
            return

    def load_comparison_result(self):
        if self.slide_path is None or not os.path.exists(self.slide_path): return
        if os.path.exists(self.slide_path):
            self.loadPairedWindowSignal.emit(self.slide_path)
        if len(self.heatmap_list) == 0:
            QMessageBox.warning(self, "警告", "请先载入结果后再载入对比结果！")
            return
        slide_name = os.path.splitext(os.path.basename(self.slide_path))[0]
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self, "选择多模态可视化热图", self.file_dir,
                                                  "*热图(*.pkl)", options=options)
        if path == '':
            return
        if not os.path.exists(path):
            QMessageBox(self, '警告', "路径不存在！")
            return
        if slide_name not in path:
            QMessageBox.warning(self, '警告', '结果文件与图片不匹配！')
            return

        with open(path, 'rb') as f:
            data = pickle.load(f)
            f.close()
        try:
            """
            data的格式， dict
            key: heatmap heatmap_downsample
            heatmap 中存放的也是一个字典，里面的key是模态名，value是heatmap
            """
            self.comparison_heatmap_list = []
            modal_list = []
            heatmap_dict = data["heatmap"]
            self.comparison_heatmap_downsample = data["heatmap_downsample"]
            for modal_name, heatmap in heatmap_dict.items():
                modal_list.append(modal_name)
                self.comparison_heatmap_list.append(heatmap)
            if len(self.comparison_heatmap_list) == 0:
                self.comparison_heatmap_list = []
                self.comparison_heatmap_downsample = None
                QMessageBox.warning(self, "警告", "文件缺失！")
                return
            self.changeHeatmap(self.modal_check.last_checked_index)
        except Exception as e:
            self.comparison_heatmap_list = []
            self.comparison_heatmap_downsample = None
            QMessageBox.warning(self, "警告", str(e))
            return

    def changeHeatmap(self, index):
        super().changeHeatmap(index)
        if len(self.heatmap_list) > 0:
            if index is None:
                self.heatmapSignal.emit(None, None, False)
            else:
                try:
                    heatmap = self.heatmap_list[index]
                    self.heatmapSignal.emit(heatmap, self.heatmap_downsample, True)
                except Exception as e:
                    QMessageBox.warning(self, "警告", str(e))

        if len(self.comparison_heatmap_list) > 0:
            if index is None:
                self.comparison_heatmapSignal.emit(None, None, False)
            else:
                try:
                    heatmap = self.comparison_heatmap_list[index]
                    self.comparison_heatmapSignal.emit(heatmap, self.comparison_heatmap_downsample, True)
                except Exception as e:
                    QMessageBox.warning(self, "警告", str(e))
