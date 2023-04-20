import os
import glob
import datetime
import argparse

import torch
import openslide
from PyQt5.QtCore import QThread, pyqtSignal
from window.MessageBox import CustomMessageBox

from Inference import models
from Inference.Microenvironment.utils.logger import get_logger
from Inference.Microenvironment.SegmentTumor import Segment_Tumor
from Inference.Microenvironment.SegmentNuclei import Segment_Nuclei
from Inference.Microenvironment.utils.data_aug import transforms, ColorDeConv, EnhanceContrast, ToTensor, Normalize

whole_slide_formats = [
            ".svs", ".vms", ".vmu", ".ndpi",
            ".scn", ".mrxs", ".tiff", ".svslide",
            ".tif", ".bif", ".mrxs", ".bif",
            ".dmetrix", ".qptiff"]

MODEL_DICE = {"UNet":
                  {"in_ch": 3, "out_ch": 5,
                   "bilinear": True, "base_c": 64},
              "ResUNet":
                  {
                      "img_channels": 3, "base_channels": 64,
                      "norm": 'bn', "out_ch": 5
                  }
              }

def main(args, slide_path, bar_signal_tumor_seg=None, bar_signal_nuclei_seg=None, completed_signal=None):
    # 读取slide
    results_dir = os.path.join(args.results_dir)
    os.makedirs(results_dir, exist_ok=True)
    slide = openslide.open_slide(slide_path)
    slide_name = os.path.basename(slide_path)
    handle_flag = False
    for format in whole_slide_formats:
        if format in slide_path:
            handle_flag = True
            slide_name = slide_name.replace(format, "")
    if handle_flag is False:
        return

    # 初始化语义分割模型以及数据预处理方法
    device = torch.device(args.device) if torch.cuda.is_available() else torch.device('cpu')
    model = getattr(models, args.tumor_seg_model)(**MODEL_DICE[args.tumor_seg_model]).to(device)
    if os.path.exists(args.SegModelWeightPath):
        try:
            model.load_state_dict(torch.load(args.SegModelWeightPath, map_location=device))
        except:
            message = CustomMessageBox('警告', f"模型参数文件与{args.tumor_seg_model}不匹配")
            message.run()
            return
    else:
        message = CustomMessageBox('警告', "模型参数文件不存在")
        message.run()
        return
    imgtransforms = transforms([
        ToTensor(),
        Normalize(mean=[0.485, 0.456, 0.406], std=[0.229,0.224,0.225])
    ])
    # 语义分割
    model.eval()
    region_info = Segment_Tumor(model=model,
                  num_classes=args.seg_num_classes,
                  slide=slide,
                  slide_name=slide_name,
                  heatmap_level=args.heatmap_level,
                  batch_size=args.seg_tumor_batch_size,
                  dataset_num_workers=args.dataset_num_workers,
                  post_proc_num_workers=args.post_proc_num_workers,
                  patch_size=args.seg_tumor_patch_size,
                  stride=args.seg_tumor_stride,
                  patch_downsample=args.seg_tumor_patch_downsample,
                  mask_level=args.mask_level,
                  tissue_mask_threshold=args.tissue_mask_threshold,
                  transforms = imgtransforms,
                  device=device,
                  results_dir=results_dir,
                  bar_signal_tumor_seg=bar_signal_tumor_seg,
                  mode='HE')

    # 实例分割
    del model
    model = getattr(models, args.nuclei_seg_model)(num_types=args.num_nuclei_types, freeze=True, pretrained_backbone=None).to(device)
    if os.path.exists(args.SegNucleiWeightPath):
        try:
            weight = torch.load(args.SegNucleiWeightPath, map_location=device)
            if 'model' in weight.keys():
                weight = weight['model']
            model.load_state_dict(weight, strict=True)
        except:
            message = CustomMessageBox(f"模型参数文件与{args.tumor_seg_model}不匹配")
            message.run()
            return
    else:
        message = CustomMessageBox("模型参数文件不存在")
        message.run()
        return

    imgtransforms = transforms([
        ToTensor(),
        Normalize(mean=[0.485, 0.456, 0.406], std=[0.229,0.224,0.225])
    ])
    model.eval()
    Segment_Nuclei(model=model,
                   slide=slide,
                   slide_name=slide_name,
                   batch_size=args.seg_nuclei_batch_size,
                   dataset_num_workers=args.dataset_num_workers,
                   post_proc_num_workers=args.post_proc_num_workers,
                   patch_size=args.seg_nuclei_patch_size,
                   stride=args.seg_nuclei_stride,
                   patch_downsample=args.seg_nuclei_patch_downsample,
                   mask_level=args.mask_level,
                   tissue_mask_threshold=args.tissue_mask_threshold,
                   transforms=imgtransforms,
                   device=device,
                   enabel_amp=args.enable_amp,
                   results_dir=results_dir,
                   bar_signal_nuclei_seg=bar_signal_nuclei_seg,
                   mode='HE',
                   region_info=region_info)
    if completed_signal:
        completed_signal.emit(f"{results_dir}/{slide_name}/{slide_name}_nuclei.pkl")


class Microenvironment_Thread(QThread):
    completed_signal = pyqtSignal(str)
    def __init__(self, kwargs):
        super(Microenvironment_Thread, self).__init__()
        self.kwargs = kwargs
        self.kwargs['completed_signal'] = self.completed_signal

    def run(self):
        main(**self.kwargs)