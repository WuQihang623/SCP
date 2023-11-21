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
    heatmapSignal = pyqtSignal(np.ndarray, np.ndarray, int, bool)
    comparison_heatmapSignal = pyqtSignal(np.ndarray, np.ndarray, int, bool)
    def __init__(self):
        super(UI_Multimodal, self).__init__()
        self.init_UI()
        self.file_dir = self.folderselector.FileDir()
        self.slide_path = None
        self.heatmap_idx = -1
        self.heatmap_list = []
        self.overview_list = []
        self.heatmap_downsamples = []

        self.comparison_heatmap_list = []
        self.comparison_overview_list = []
        self.comparison_heatmap_downsamples = []
        # 连接信号
        self.connect_btn()

    def connect_btn(self):
        self.showHeatmap_btn.setChecked(True)
        self.showHeatmap_btn.setEnabled(False)
        self.showHeatmap_btn.clicked.connect(self.turn_heatmap)
        self.load_btn.clicked.connect(self.load_result)

    def set_slide_path(self, slide_path):
        self.slide_path = slide_path

    def load_result(self):
        if self.slide_path is None: return
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
            key: 基因 or 临床
            value: {"colorbar": ndarray, "overview": ndarray, "heatmap": ndarray, "downsample": int}
            """
            colorbar_list = []
            self.heatmap_list = []
            self.overview_list = []
            self.heatmap_downsamples = []
            for modal, modal_info in data.items():
                colorbar_list.append(modal_info["colorbar"])
                self.heatmap_list.append(modal_info["heatmap"])
                self.overview_list.append(modal_info["overview"])
                self.heatmap_downsamples.append(modal_info["downsample"])
            if len(colorbar_list) == 0:
                QMessageBox.warning(self, "警告", "文件缺失！")
                return
            self.load_colorbar(colorbar_list)
            self.heatmap_idx = 0
            self.changeHeatmap(self.heatmap_idx)
            self.showHeatmap_btn.setEnabled(True)
        except Exception as e:
            self.heatmap_list = []
            self.heatmap_downsamples = []
            self.heatmap_idx = -1
            QMessageBox.warning(self, "警告", str(e))
            return

    def load_comparison_result(self):
        if self.slide_path is None: return
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
            key: 基因 or 临床
            value: {"colorbar": ndarray, "overview": ndarray, "heatmap": ndarray, "downsample": int}
            """
            colorbar_list = []
            self.comparison_heatmap_list = []
            self.comparison_overview_list = []
            self.comparison_heatmap_downsamples = []
            for modal, modal_info in data.items():
                colorbar_list.append(modal_info["colorbar"])
                self.comparison_heatmap_list.append(modal_info["heatmap"])
                self.comparison_overview_list.append(modal_info["overview"])
                self.comparison_heatmap_downsamples.append(modal_info["downsample"])
            if len(colorbar_list) == 0:
                QMessageBox.warning(self, "警告", "文件缺失！")
                return
            self.changeHeatmap(self.heatmap_idx)
            self.showHeatmap_btn.setEnabled(True)
        except Exception as e:
            self.comparison_heatmap_list = []
            self.comparison_overview_list = []
            self.comparison_heatmap_downsamples = []
            QMessageBox.warning(self, "警告", str(e))
            return

    def turn_heatmap(self, flag):
        super().turn_heatmap(flag)
        if flag:
            self.changeHeatmap(0)
        else:
            self.changeHeatmap(-1)

    def changeHeatmap(self, index):
        if self.heatmap_idx != index and len(self.heatmap_list) > 0:
            self.heatmap_idx = index
            if self.heatmap_idx < 0:
                self.heatmapSignal.emit(None, None, None, False)
            else:
                try:
                    overview = self.overview_list[self.heatmap_idx]
                    heatmap = self.heatmap_list[self.heatmap_idx]
                    downsample = self.heatmap_downsamples[self.heatmap_idx]
                    self.heatmapSignal.emit(overview, heatmap, downsample, True)
                except Exception as e:
                    QMessageBox.warning(self, "警告", str(e))

            # 显示对比窗口
            if len(self.comparison_heatmap_list) > 0:
                if self.heatmap_idx < 0:
                    self.comparison_heatmapSignal.emit(None, None, None, False)
                else:
                    try:
                        overview = self.comparison_overview_list[self.heatmap_idx]
                        heatmap = self.comparison_heatmap_list[self.heatmap_idx]
                        downsample = self.comparison_heatmap_downsamples[self.heatmap_idx]
                        self.comparison_heatmapSignal.emit(overview, heatmap, downsample, True)
                    except Exception as e:
                        QMessageBox.warning(self, "警告", str(e))
