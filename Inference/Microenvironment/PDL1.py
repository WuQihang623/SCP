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
from Inference.Microenvironment.utils.measure import measure_PDL1
from Inference.Microenvironment.utils.data_aug import transforms, ColorDeConv, EnhanceContrast, ToTensor, Normalize

whole_slide_formats = [
            ".svs", ".vms", ".vmu", ".ndpi",
            ".scn", ".mrxs", ".tiff", ".svslide",
            ".tif", ".bif", ".mrxs", ".bif",
            ".dmetrix", ".qptiff"]

MODEL_DICE = {"UNet":
                  {"in_ch": 3, "out_ch": 2,
                   "bilinear": True, "base_c": 64},
              "ResUNet":
                  {
                      "img_channels": 3, "base_channels": 64,
                      "norm": 'bn', "out_ch": 2
                  }
              }

def main(args, slide_path, bar_signal_tumor_seg=None, bar_signal_nuclei_seg=None, bar_signal_pdl1_judge=None, completed_signal=None):
    # 读取slide
    results_dir = os.path.join(args.results_dir)
    os.makedirs(results_dir, exist_ok=True)
    logger = get_logger('pdl1', f'{results_dir}/results.log')
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
    device = torch.device(args.device)
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
                  mode='PDL1')

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
            message = CustomMessageBox("警告", f"模型参数文件与{args.tumor_seg_model}不匹配")
            message.run()
            return
    else:
        message = CustomMessageBox("警告", "模型参数文件不存在")
        message.run()
        return

    imgtransforms = transforms([
        ColorDeConv(),
        EnhanceContrast(),
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
                   mode='PDL1',
                   region_info=region_info)

    # 找到肿瘤区域内的细胞并判断PDL1阳性与阴性，保存成pkl格式,(TPS, CPS)
    tps, cps = measure_PDL1(slide=slide,
                            slide_name=slide_name,
                            type_nuclei_hovernet=args.type_nuclei_hovernet,
                            type_pdl1_nuclei=args.type_pdl1_nuclei,
                            expansion_distance=args.expansion_distance,
                            threshold=args.pdl1_threshold,
                            num_worker=args.measure_pdl1_workers,
                            results_dir=results_dir,
                            bar_signal_pdl1_judge=bar_signal_pdl1_judge)
    # 输出结果
    logger.info(f"{slide_name}'s tps: {tps:.3f} cps:{cps:.3f}!")
    print(f"{slide_name}'s tps: {tps:.3f} cps:{cps:.3f}!")
    if completed_signal:
        completed_signal.emit(f"{results_dir}/{slide_name}/{slide_name}_nuclei_pdl1.pkl")
    return

class PDL1_Thread(QThread):
    completed_signal = pyqtSignal(str)
    def __init__(self, kwargs):
        super(PDL1_Thread, self).__init__()
        self.kwargs = kwargs
        self.kwargs['completed_signal'] = self.completed_signal

    def run(self):
        main(**self.kwargs)

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--tumor_seg_model', type=str, default='ResUNet')
#     parser.add_argument('--nuclei_seg_model', type=str, default='HoVerNetExt')
#     parser.add_argument('--slide_path', type=str, default="/Disk1/PDL1_Zhujiang/Breast/2216657-7k/2216657-7k.dmetrix")
#     # parser.add_argument('--slide_dir', type=str, default="/Disk1/PDL1_Zhujiang/Breast/*/*.dmetrix")
#     parser.add_argument('--slide_dir', type=str, default="")
#     parser.add_argument('--results_dir', type=str, default='results_zhujiang_pdl1')
#     parser.add_argument('--device', type=str, default="cuda")
#     parser.add_argument('--seg_num_classes', type=int, default=2)
#     parser.add_argument('--SegModelWeightPath', type=str, default="weights/ResUNet_0.543.pth")
#     parser.add_argument('--heatmap_level', type=int, default=-1)
#     parser.add_argument('--seg_tumor_batch_size', type=int, default=16)
#     parser.add_argument('--dataset_num_workers', type=int, default=4)
#     parser.add_argument('--post_proc_num_workers', type=int, default=9)
#     parser.add_argument('--seg_tumor_patch_size', type=int, default=512)
#     parser.add_argument('--seg_tumor_stride', type=int, default=256)
#     parser.add_argument('--seg_tumor_patch_downsample', type=int, default=2)
#     parser.add_argument('--mask_level', type=int, default=-1)
#     parser.add_argument('--tissue_mask_threshold', type=float, default=0.01)
#     parser.add_argument('--num_nuclei_types', type=int, default=5)
#     parser.add_argument('--SegNucleiWeightPath', type=str, default="weights/HoVerNetExt_0.547.pth")
#     parser.add_argument('--seg_nuclei_batch_size', type=int, default=12)
#     parser.add_argument('--seg_nuclei_patch_size', type=int, default=512)
#     parser.add_argument('--seg_nuclei_stride', type=int, default=416)
#     parser.add_argument('--seg_nuclei_patch_downsample', type=int, default=1)
#     parser.add_argument('--enable_amp', type=bool, default=True)
#     parser.add_argument('--expansion_distance', type=int, default=2000)
#     parser.add_argument('--pdl1_threshold', type=float, default=0.1)
#     parser.add_argument('--measure_pdl1_workers', type=int, default=1)
#     parser.add_argument('--type_nuclei_hovernet', type=dict, default={"tumor": 1, "lymph": 2, "macrophage": 3, "neutrophils": 4})
#     parser.add_argument('--type_pdl1_nuclei', type=dict, default={"other": 0, "pdl1_positive_tumor": 1, "pdl1_negitive_tumor": 2, "pdl1_positive_immune": 3})
#     args = parser.parse_args()
#
#     if args.slide_dir:
#         slide_list = sorted(glob.glob(args.slide_dir))[1:10]
#     else:
#         slide_list = [args.slide_path]
#     now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
#     for slide_path in slide_list:
#         main(args=args, slide_path=slide_path, now=now)