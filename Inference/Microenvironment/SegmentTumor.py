import os
import sys
import time
import tqdm
import math
import pickle
import threading
import openslide

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

from Inference.Microenvironment.datasets.WholeSlideSet_PDL1 import WholeSlideSet as WholeSlideSet_PDL1
from Inference.Microenvironment.datasets.WholeSlideSet_HE import WholeSlideSet as WholeSlideSet_HE

@torch.no_grad()
def Segment_Tumor(model: torch.nn.Module,
                  num_classes: int,
                  slide: openslide.OpenSlide,
                  slide_name: str,
                  heatmap_level: int,
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
                  results_dir='results',
                  bar_signal_tumor_seg=None,
                  mode='HE'):
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

    # 计算heatmap的缩放倍数，heatmap的shape
    if heatmap_level < 0:
        heatmap_level = slide.get_best_level_for_downsample(16)
    heatmap_downsample = slide.level_downsamples[heatmap_level]
    heatmap_dimension = slide.level_dimensions[heatmap_level]
    zoomout = int(heatmap_downsample/patch_downsample)
    assert zoomout > 1

    mask = torch.zeros((num_classes, heatmap_dimension[1], heatmap_dimension[0]), dtype=torch.float16)
    weight = torch.zeros((heatmap_dimension[1], heatmap_dimension[0]), dtype=torch.int8)

    def post_process(preds, coordinates_str):
        for i in range(preds.shape[0]):
            pred = preds[i]
            coordinate = [int(int(p)/heatmap_downsample) for p in coordinates_str[i].split('_')]
            mask[:, coordinate[1]: coordinate[1]+preds.shape[2],
                 coordinate[0]: coordinate[0]+preds.shape[2]] += pred.cpu()
            weight[coordinate[1]: coordinate[1]+preds.shape[2],
                 coordinate[0]: coordinate[0]+preds.shape[2]] += torch.ones((preds.shape[2], preds.shape[2]), dtype=torch.int8)


    dataloader = tqdm.tqdm(dataloader, file=sys.stdout)
    length = len(dataloader)
    for idx, data in enumerate(dataloader):
        img = data["patch"].to(device)
        coordinate_str = data["coordination"]

        preds = model(img)
        preds = torch.softmax(preds, dim=1)
        preds = F.interpolate(preds, (int(patch_size/zoomout), int(patch_size/zoomout)), mode='bilinear')

        t = threading.Thread(target=post_process, args=(preds, coordinate_str))
        t.start()
        if threading.active_count() > post_proc_num_workers:
            t.join()
        if idx > len(dataloader) - 5:
            t.join()
        if bar_signal_tumor_seg:
            bar_signal_tumor_seg.emit(length, idx, '肿瘤区域分割进度：')
    # 存储结果
    os.makedirs(f"{results_dir}/{slide_name}", exist_ok=True)
    weight[weight==0] = 1
    mask = mask / weight.unsqueeze(0)
    mask = torch.argmax(mask, dim=0).numpy().astype("int8")
    print(f"肿瘤区域分割耗费了{time.time()-start:.3f}秒！")

    with open(f"{results_dir}/{slide_name}/{slide_name}_seg.pkl", 'wb') as f:
        pickle.dump({"mask": mask, "heatmap_downsample": heatmap_downsample}, f)
        f.close()
    return {"mask": mask, "heatmap_downsample": heatmap_downsample}

