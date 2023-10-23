import os
import pickle
import sys
import time
import glob
import tqdm
import math
import threading
from collections import OrderedDict

import torch
import openslide
import numpy as np
import constants
from torch.cuda import amp
import torch.nn.functional as F
from torch.utils.data import DataLoader

from Inference.models.hovernet.post_proc_hovernet import process
from Inference.Microenvironment.utils.post_proc_nuclei import convert_format
from Inference.Microenvironment.datasets.WholeSlideSet_PDL1 import WholeSlideSet as WholeSlideSet_PDL1
from Inference.Microenvironment.datasets.WholeSlideSet_HE import WholeSlideSet as WholeSlideSet_HE

@torch.no_grad()
def Segment_Nuclei(model: torch.nn.Module,
                   slide: openslide.OpenSlide,
                   slide_name: str,
                   batch_size: int,
                   dataset_num_workers: int,
                   post_proc_num_workers: int,
                   patch_size: int = 512,
                   stride: int = 416,
                   patch_downsample: int = 1,
                   mask_level: int = -1,
                   tissue_mask_threshold: float = 0,
                   transforms=None,
                   device="cuda",
                   enabel_amp=True,
                   results_dir='results',
                   bar_signal_nuclei_seg=None,
                   mode='HE',
                   region_info=None):
    results_dir = os.path.join(constants.micro_path, results_dir)
    start = time.time()
    if mode == 'HE':
        dataset = WholeSlideSet_HE(slide=slide,
                                   patch_size=patch_size,
                                   stride=stride,
                                   patch_downsample=patch_downsample,
                                   mask_level=mask_level,
                                   tissue_mask_threshold=tissue_mask_threshold,
                                   transforms=transforms)
    else:
        dataset = WholeSlideSet_PDL1(slide=slide,
                                     patch_size=patch_size,
                                     stride=stride,
                                     patch_downsample=patch_downsample,
                                     mask_level=mask_level,
                                     tissue_mask_threshold=tissue_mask_threshold,
                                     transforms=transforms)
    dataloader = DataLoader(dataset=dataset,
                            batch_size=batch_size,
                            shuffle=False,
                            pin_memory=True,
                            num_workers=dataset_num_workers)

    os.makedirs(f"{results_dir}/cache", exist_ok=True)
    # 清空cache文件夹
    cache_path_list = glob.glob(f"{results_dir}/cache/*.pkl")
    for cache_path in cache_path_list:
        os.remove(cache_path)

    # enable_amp = enabel_amp if "cuda" in device else False
    dataloader = tqdm.tqdm(dataloader, file=sys.stdout)

    def post_process(pred_dict, coordinates_str, type_maps_clone=None):
        preds_map = torch.cat(list(pred_dict.values()), -1)
        preds_map = preds_map.cpu().numpy()
        if type_maps_clone is not None:
            type_maps_clone = type_maps_clone.cpu().numpy()
        for i in range(preds_map.shape[0]):
            pred_map = preds_map[i]
            if type_maps_clone is not None:
                type_map_clone = type_maps_clone[i]
            else:
                type_map_clone = None
            coordinate_str = coordinates_str[i]
            pred_inst, inst_info_dict = process(pred_map, model.num_types, True, type_map_clone)

            with open(f'{results_dir}/cache/{coordinate_str}.pkl', 'wb') as f:
                pickle.dump({coordinate_str: inst_info_dict}, f)
                f.close()

    length = len(dataloader)
    for idx, data in enumerate(dataloader):
        imgs = data["patch"].to(device)
        coordinates_str = data["coordination"]

        with amp.autocast(enabel_amp):
            pred_dict = model(imgs)
        pred_dict = OrderedDict(
            [[k, v.permute(0, 2, 3, 1).contiguous()] for k, v in pred_dict.items()]
        )
        pred_dict["np"] = F.softmax(pred_dict["np"], dim=-1)[..., 1:]

        type_maps_clone = None
        if "tp" in pred_dict.keys():
            type_map = F.softmax(pred_dict["tp"], dim=-1)
            type_maps_clone = type_map.clone()
            type_map = torch.argmax(type_map, dim=-1, keepdim=True).type(torch.float32)
            pred_dict["tp"] = type_map
        t = threading.Thread(target=post_process, args=(pred_dict, coordinates_str, type_maps_clone))
        t.start()
        if threading.active_count() > post_proc_num_workers:
            t.join()
        if idx > len(dataloader) - 5:
            t.join()
        if bar_signal_nuclei_seg:
            bar_signal_nuclei_seg.emit(length, idx, '细胞分割进度：')

    # 处理边界的细胞
    inst_info_dict = {}
    cache_path_list = glob.glob(f"{results_dir}/cache/*.pkl")
    for cache_path in cache_path_list:
        with open(cache_path, 'rb') as f:
            inst_info_dict.update(pickle.load(f))
            f.close()
    for cache_path in cache_path_list:
        os.remove(cache_path)

    type, center, contour = convert_format(inst_info_dict, patch_size, stride, patch_downsample)
    os.makedirs(f"{results_dir}/{slide_name}", exist_ok=True)
    inst_info = {"type": np.int8(type), "center": np.int32(center),
                     "contour": np.array(contour, dtype=object), "grid": {"x": [0], "y": [0]}}
    inst_info.update(region_info)
    with open(f"{results_dir}/{slide_name}/{slide_name}_nuclei.pkl", 'wb') as f:
        pickle.dump(inst_info, f)
        f.close()

    print(f"细胞核分割耗费了{time.time()-start}秒！")
    return
