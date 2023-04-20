import math
import os

import json
import cv2
import numpy as np
import argparse
import torch
import torch.nn as nn
import torch.backends.cudnn as cudnn
import torch.nn.functional as F
import time
from PyQt5.QtCore import QThread, pyqtSignal
from window.MessageBox import CustomMessageBox
import torch.utils.data as data
import torchvision.transforms as transforms
from Inference.models.base_model import resnet34
from Inference.models.resnet_custom import resnet50_baseline
from Inference.diagnose.dataset import Dataset, data_prefetcher
import matplotlib.pyplot as plt
from Inference.diagnose.extract_patch import extract_patch_each
import openslide

def get_args():
    parser = argparse.ArgumentParser(description='MIL')
    parser.add_argument('--slide_dir', type=str, default='/mnt/MedImg/Camelyon16/tumor/')
    parser.add_argument('--batch_size', type=int, default=12, help='mini-batch size (default: 512)')
    parser.add_argument('--workers', default=0, type=int, help='number of data loading workers (default: 4)')
    parser.add_argument('--models', type=str, default='/mnt/code1/wzh/camelyon16/40x256/checkpoint_best_40x256', help='path to pretrained models')
    parser.add_argument('--load_model', default=True, action='store_true')
    parser.add_argument('--device', type=int, default=0)
    parser.add_argument('--device_ids', type=int, nargs='+', default=[0])
    args = parser.parse_args()
    return args


device = torch.device(f'cuda' if torch.cuda.is_available() else 'cpu')

class Model(nn.Module):
    def __init__(self, input_dim=1024):
        super(Model, self).__init__()
        self.backbone = resnet50_baseline(True)
        self.backbone.fc = nn.Linear(1024, 2)
        self.fc = nn.Linear(1024, 2)

    def forward(self, x):
        _, feat = self.backbone(x)
        prob = self.fc(feat)
        return prob, feat

def inference(loader, model):
    args = get_args()
    model.eval()
    probs = torch.FloatTensor(len(loader.dataset))
    prefetcher = data_prefetcher(loader)
    features = torch.Tensor()
    with torch.no_grad():
        input = prefetcher.next()
        i = 0
        while input is not None:
            # 训练代码
            if i % 1000 == 999:
                print('Batch: [{}/{}]'.format(i+1, len(loader)))
                #os.system('/home/wzh/release.sh')
            input = input.to(device)
            output, feature = model(input)
            output = F.softmax(output, dim=1)
            probs[i*args.batch_size:i*args.batch_size+input.size(0)] = output.detach()[:,1].clone()
            input = prefetcher.next()
            i += 1
    return probs.cpu().numpy()


def get_draw_coor(grid, size, downsample):
    coor = [grid[0], grid[1], grid[0] + size*2, grid[1] + size*2]
    coor = [int(_coor / downsample) for _coor in coor]
    return coor


def inference_simple(loader, heatmap, size, downsample, model, length=0, signal=None):
    args = get_args()
    model.eval()
    probs = torch.FloatTensor(len(loader.dataset))
    # prefetcher = data_prefetcher(loader)
    # features = torch.Tensor()
    with torch.no_grad():
        for i, data in enumerate(loader):
            input, grid = data
            grid = np.array(grid, dtype=np.int32)
            input = input.to(device)
            output, feature = model(input)
            output = F.softmax(output, dim=1)
            prob = output.detach()[:, 1].cpu()
            probs[i*args.batch_size:i*args.batch_size+input.size(0)] = prob.clone()
            for j in range(output.size(0)):
                coor = get_draw_coor([grid[j, 0], grid[j, 1]], size, downsample)
                heatmap[coor[1]:coor[3], coor[0]:coor[2]] = prob[j].item()
            if signal:
                signal.emit(length, i, '诊断进度')

    return probs.cpu().numpy(), heatmap.cpu().numpy()


def calc_err(pred, real):
    pred = np.array(pred)
    real = np.array(real)
    neq = np.not_equal(pred, real)
    err = float(neq.sum())/pred.shape[0]
    fpr = float(np.logical_and(pred==1,neq).sum())/(real==0).sum()
    fnr = float(np.logical_and(pred==0,neq).sum())/(real==1).sum()
    return err, fpr, fnr


def optimal_thresh(fpr, tpr, thresholds, p=0):
    loss = (fpr - tpr) - p * tpr / (fpr + tpr + 1)
    idx = np.argmin(loss, axis=0)
    return fpr[idx], tpr[idx], thresholds[idx]



def get_mpl_colormap(cmap_name):
    cmap = plt.get_cmap(cmap_name)
    # Initialize the matplotlib color map
    sm = plt.cm.ScalarMappable(cmap=cmap)
    # Obtain linear color range
    color_range = sm.to_rgba(np.linspace(0, 1, 256), bytes=True)[:,2::-1]
    return color_range.reshape(256, 1, 3)


def diagnosis(slidepath, crop_size=[256, 256], level=1, draw_level=-1, signal=None):
    args = get_args()
    weight_path = "Inference/weights/t3_feature_extractor.pth"
    ## Loading models
    model = Model(input_dim=1024)
    model.fc = nn.Linear(model.fc.in_features, 2)
    if os.path.exists(weight_path):
        ch = torch.load(weight_path, map_location='cpu')
        model.load_state_dict(ch, strict=True)
    else:
        message = CustomMessageBox('警告', "模型参数文件不存在")
        message.run()
        return
    model.to(device)
    model = nn.DataParallel(model, device_ids=args.device_ids)

    cudnn.benchmark = True
    normalize = transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
    trans = transforms.Compose([
        transforms.ToTensor(),
        normalize])

    ## Create Patch and test Data
    begin = time.time()
    test_lib, patch = extract_patch_each(slidepath, crop_size, level)
    seg_end = time.time()
    print("Seg time: ", seg_end - begin)

    ## heatmap
    slide = openslide.OpenSlide(slidepath)
    # downsample = slide.level_dimensions[0][0] / 6000
    output_level = 5
    if output_level > slide.level_count - 1:
        output_level = slide.level_count - 1
    heatmap_downsample = int(slide.level_downsamples[output_level])
    #slidename = os.path.basename(slidepath).split('.')[0]
    size = slide.level_dimensions[output_level]
    downsample = slide.level_downsamples[draw_level]
    draw_size = slide.level_dimensions[draw_level]
    wsi_ori = slide.get_thumbnail(size)
    wsi_ori = wsi_ori.resize(size)
    wsi_ori = np.array(wsi_ori)
    wsi_ori = cv2.cvtColor(wsi_ori, cv2.COLOR_BGR2RGB)
    wsi_mask = cv2.cvtColor(wsi_ori, cv2.COLOR_BGR2GRAY)
    _, wsi_mask = cv2.threshold(wsi_mask, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    wsi_mask = 1 - wsi_mask
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    wsi_mask = cv2.morphologyEx(wsi_mask, cv2.MORPH_CLOSE, kernel)


    ## Testing and output probability
    heatmap = torch.zeros(size=(draw_size[1], draw_size[0]))
    test_dset = Dataset(test_lib, patch_size=crop_size[0], transform=trans)

    test_loader = torch.utils.data.DataLoader(
        test_dset,
        batch_size=args.batch_size, shuffle=False,
        num_workers=args.workers, pin_memory=False)
    length = math.ceil(len(test_dset)/args.batch_size)
    print(length)
    ## Test
    probs, heatmap = inference_simple(test_loader, heatmap, crop_size[0], downsample, model, length=length, signal=signal)
    maxs = np.max(probs)
    if maxs > 0.5:
        print("Positive")
    else:
        print("Negative")
    end = time.time()
    print("Total time: ", end - begin)

    ## Draw heatmap
    mask = heatmap == 0
    heatmap = np.clip(heatmap + 0.2, 0, 1)
    print(heatmap.shape)
    cam_img = np.uint8(255 * heatmap)
    colorheatmap = cv2.applyColorMap(cam_img, get_mpl_colormap('bwr_r'))
    colorheatmap[mask] = np.array([255, 255, 255])
    colorheatmap = cv2.GaussianBlur(colorheatmap, (5, 5), 1.5)
    colorheatmap = cv2.resize(colorheatmap, size)
    colorheatmap[wsi_mask == 0] = np.array([255, 255, 255])
    colorheatmap = cv2.cvtColor(colorheatmap, cv2.COLOR_BGR2RGB)
    #cv2.imwrite('models/test_colormap.jpg', colorheatmap)
    result = 0.3 * colorheatmap + wsi_ori * 0.7
    result = np.uint8(result)

    overview_shape = slide.level_dimensions[-1]
    return result, maxs, colorheatmap, heatmap_downsample, heatmap, overview_shape

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)

class Thread_Diagnose(QThread):
    complete_signal = pyqtSignal(str)
    def __init__(self, kwargs, overview_shape):
        super(Thread_Diagnose, self).__init__()
        self.kwargs = kwargs
        self.overview_shape = overview_shape

    def run(self):
        result, preds, heatmap, downsample, probs, overview_shape = diagnosis(**self.kwargs)
        slide_name = os.path.splitext(os.path.basename(self.kwargs['slidepath']))
        os.makedirs(f'results/{slide_name}', exist_ok=True)
        cv2.imwrite(f'results/{slide_name}/{slide_name}_result.jpg', cv2.resize(result, self.overview_shape))
        preds_down = {'preds': preds, 'down': downsample}
        with open(f"results/{slide_name}/{slide_name}_preds_down.json", 'w') as f:
            f.write(json.dumps(preds_down, indent=2, cls=NpEncoder))
            f.close()
        np.save(f"results/{slide_name}/{slide_name}_heatmap.npy", heatmap)
        np.save(f"results/{slide_name}/{slide_name}_probs.npy", probs)
        self.complete_signal.emit(f'results/{slide_name}/{slide_name}_result.jpg')
