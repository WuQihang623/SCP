import os
import json
import argparse
import time

import cv2
import openslide
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition, QRectF
from PyQt5.QtWidgets import *

import constants
import numpy as np
from function.utils import NpEncoder
from Inference.diagnose.diagnose import diagnosis
from Inference.Microenvironment.PDL1 import main as PDL1
from Inference.Microenvironment.Microenviroment import main as microenv
from function.utils import is_file_copy_finished

class BatchProcessThread(QThread):
    diagnose_signal = pyqtSignal(int, int, str)
    tumor_segment_signal = pyqtSignal(int, int, str)
    nuclei_segment_signal = pyqtSignal(int, int, str)
    pdl1_judge_signal = pyqtSignal(int, int, str)
    BatchProcessPath = os.path.join(constants.cache_path, "batch_process.json")
    def __init__(self, file_watcher:QWidget, mode, path):
        super(BatchProcessThread, self).__init__()
        self.file_watcher = file_watcher
        self.mode = mode
        self.results_dir = 'results'
        self.path = path
        self.row = 0

        self.batch_flag = True

    def param_diagnose(self, slide_path):
        kwargs = {'slidepath': slide_path,
                  'signal': self.diagnose_signal}
        self.diagnose_signal.connect(self.set_bar)
        # self.progress_diagnose.exec_()
        return kwargs

    def param_micro(self, slide_path):
        kwargs = {}

        parser = argparse.ArgumentParser()
        parser.add_argument('--tumor_seg_model', type=str, default='UNet')
        parser.add_argument('--nuclei_seg_model', type=str, default='HoVerNetExt')
        parser.add_argument('--results_dir', type=str, default=self.results_dir)
        parser.add_argument('--device', type=str, default="cuda")
        parser.add_argument('--seg_num_classes', type=int, default=5)
        parser.add_argument('--SegModelWeightPath', type=str,
                            default="Inference/Microenvironment/weights/UNet_tcga_0.965.pth")
        parser.add_argument('--heatmap_level', type=int, default=-1)
        parser.add_argument('--seg_tumor_batch_size', type=int, default=4)
        parser.add_argument('--dataset_num_workers', type=int, default=0)
        parser.add_argument('--post_proc_num_workers', type=int, default=9)
        parser.add_argument('--seg_tumor_patch_size', type=int, default=512)
        parser.add_argument('--seg_tumor_stride', type=int, default=256)
        parser.add_argument('--seg_tumor_patch_downsample', type=int, default=2)
        parser.add_argument('--mask_level', type=int, default=-1)
        parser.add_argument('--tissue_mask_threshold', type=float, default=0.01)
        parser.add_argument('--num_nuclei_types', type=int, default=5)
        parser.add_argument('--SegNucleiWeightPath', type=str,
                            default="Inference/Microenvironment/weights/model_retrain_round2_tcga.pth")
        parser.add_argument('--seg_nuclei_batch_size', type=int, default=1)
        parser.add_argument('--seg_nuclei_patch_size', type=int, default=512)
        parser.add_argument('--seg_nuclei_stride', type=int, default=416)
        parser.add_argument('--seg_nuclei_patch_downsample', type=int, default=1)
        parser.add_argument('--enable_amp', type=bool, default=True)
        parser.add_argument('--expansion_distance', type=int, default=2000)
        parser.add_argument('--pdl1_threshold', type=float, default=0.1)
        parser.add_argument('--measure_pdl1_workers', type=int, default=1)
        parser.add_argument('--type_nuclei_hovernet', type=dict,
                            default={"tumor": 1, "lymph": 2, "macrophage": 3, "neutrophils": 4})
        parser.add_argument('--type_pdl1_nuclei', type=dict,
                            default={"other": 0, "pdl1_positive_tumor": 1, "pdl1_negitive_tumor": 2,
                                     "pdl1_positive_immune": 3})
        args = parser.parse_args()

        kwargs['slide_path'] = slide_path
        kwargs['args'] = args
        kwargs['bar_signal_tumor_seg'] = self.tumor_segment_signal
        kwargs['bar_signal_nuclei_seg'] = self.nuclei_segment_signal
        self.tumor_segment_signal.connect(self.set_bar)
        self.nuclei_segment_signal.connect(self.set_bar)
        return kwargs

    def param_pdl1(self, slide_path):
        kwargs = {}
        parser = argparse.ArgumentParser()
        parser.add_argument('--tumor_seg_model', type=str, default='ResUNet')
        parser.add_argument('--nuclei_seg_model', type=str, default='HoVerNetExt')
        parser.add_argument('--results_dir', type=str, default=self.results_dir)
        parser.add_argument('--device', type=str, default="cuda")
        parser.add_argument('--seg_num_classes', type=int, default=2)
        parser.add_argument('--SegModelWeightPath', type=str,
                            default="Inference/Microenvironment/weights/ResUNet_pdl1_0.554.pth")
        parser.add_argument('--heatmap_level', type=int, default=-1)
        parser.add_argument('--seg_tumor_batch_size', type=int, default=1)
        parser.add_argument('--dataset_num_workers', type=int, default=0)
        parser.add_argument('--post_proc_num_workers', type=int, default=10)
        parser.add_argument('--seg_tumor_patch_size', type=int, default=512)
        parser.add_argument('--seg_tumor_stride', type=int, default=416)
        parser.add_argument('--seg_tumor_patch_downsample', type=int, default=2)
        parser.add_argument('--mask_level', type=int, default=-1)
        parser.add_argument('--tissue_mask_threshold', type=float, default=0.01)
        parser.add_argument('--num_nuclei_types', type=int, default=5)
        parser.add_argument('--SegNucleiWeightPath', type=str,
                            default="Inference/Microenvironment/weights/Hovernet_pdl1_0.547.pth")
        parser.add_argument('--seg_nuclei_batch_size', type=int, default=1)
        parser.add_argument('--seg_nuclei_patch_size', type=int, default=512)
        parser.add_argument('--seg_nuclei_stride', type=int, default=416)
        parser.add_argument('--seg_nuclei_patch_downsample', type=int, default=1)
        parser.add_argument('--enable_amp', type=bool, default=True)
        parser.add_argument('--expansion_distance', type=int, default=2000)
        parser.add_argument('--pdl1_threshold', type=float, default=0.1)
        parser.add_argument('--measure_pdl1_workers', type=int, default=1)
        parser.add_argument('--type_nuclei_hovernet', type=dict,
                            default={"tumor": 1, "lymph": 2, "macrophage": 3, "neutrophils": 4})
        parser.add_argument('--type_pdl1_nuclei', type=dict,
                            default={"other": 0, "pdl1_positive_tumor": 1, "pdl1_negitive_tumor": 2,
                                     "pdl1_positive_immune": 3})
        args = parser.parse_args()

        kwargs['slide_path'] = slide_path
        kwargs['args'] = args
        kwargs['bar_signal_tumor_seg'] = self.tumor_segment_signal
        kwargs['bar_signal_nuclei_seg'] = self.nuclei_segment_signal
        kwargs['bar_signal_pdl1_judge'] = self.pdl1_judge_signal

        self.bar_signal_tumor_seg.connect(self.set_bar)
        self.bar_signal_nuclei_seg.connect(self.set_bar)
        self.bar_signal_pdl1_judge.connect(self.set_bar)
        return kwargs

    def run(self):
        while self.batch_flag:
            time.sleep(1)
            self.file_watcher.update()
            row_count = self.file_watcher.table_widget.rowCount()
            for row in range(row_count):
                if self.batch_flag is False:
                    break
                if self.file_watcher.table_widget.item(row, 4).text() == "传输完成" and \
                        self.file_watcher.table_widget.item(row, 5).text() == '等待分析':
                    self.file_watcher.table_widget.setItem(row, 5, QTableWidgetItem('正在分析'))
                    self.file_watcher.table_widget.viewport().update()
                    self.row = row
                    slide_path = self.file_watcher.files[row]
                    if not os.path.exists(slide_path):
                        continue
                    try:
                        if is_file_copy_finished(slide_path) is False:
                            continue
                        slide = openslide.open_slide(slide_path)
                    except:
                        continue
                    if self.mode == '诊断':
                        self.kwargs = self.param_diagnose(slide_path)
                        result, preds, heatmap, downsample, probs, overview_shape = diagnosis(**self.kwargs)
                        slide_name, _ = os.path.splitext(os.path.basename(self.kwargs['slidepath']))
                        os.makedirs(f'results/Diagnose/{slide_name}', exist_ok=True)
                        cv2.imwrite(f'results/Diagnose/{slide_name}/{slide_name}_result.jpg',
                                    cv2.resize(result, overview_shape))
                        preds_down = {'preds': preds, 'down': downsample}
                        with open(f"results/Diagnose/{slide_name}/{slide_name}_preds_down.json", 'w') as f:
                            f.write(json.dumps(preds_down, indent=2, cls=NpEncoder))
                            f.close()
                        np.save(f"results/Diagnose/{slide_name}/{slide_name}_heatmap.npy", heatmap)
                        np.save(f"results/Diagnose/{slide_name}/{slide_name}_probs.npy", probs)

                    elif self.mode == '微环境分析':
                        kwargs = self.param_micro(slide_path)
                        microenv(**kwargs)
                    elif self.mode == 'PD-L1测量':
                        kwargs = self.param_pdl1(slide_path)
                        PDL1(**kwargs)
                    else:
                        continue
                    self.file_watcher.table_widget.setItem(row, 5, QTableWidgetItem(f'{self.mode}完成'))
                    self.file_watcher.table_widget.viewport().update()

                    # 将这个信息保存下来
                    processed_list = []
                    if os.path.exists(self.BatchProcessPath):
                        with open(self.BatchProcessPath, 'r') as f:
                            processed_list = json.load(f)
                            f.close()
                    processed_list.append(os.path.basename(slide_path))
                    with open(self.BatchProcessPath, 'w') as f:
                        f.write(json.dumps(processed_list, indent=2))
                        f.close()

    def set_bar(self, length, idx, text):
        self.file_watcher.table_widget.setItem(self.row, 5, QTableWidgetItem(f'{text}：{int(idx/length*100)}%'))
        self.file_watcher.table_widget.viewport().update()
