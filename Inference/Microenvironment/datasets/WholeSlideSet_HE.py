import cv2
import time
import openslide
import numpy as np
from PIL import Image
from skimage import morphology

from torch.utils.data import Dataset

class WholeSlideSet(Dataset):
    def __init__(self, slide: openslide.OpenSlide,
                 patch_size: int=512,
                 stride: int=416,
                 patch_downsample: int=1,
                 mask_level: int=-1,
                 tissue_mask_threshold: float=0,
                 transforms=None):
        """
        :param patch_downsample: 提取哪个尺度的patch
        :param tissue_mask_threshold: 提取patch时，组织区域最小面积的比例
        :param transforms: 默认为ToTensor+Normalize，可能再加一些ColorDeconv
        """
        # self.patch_downsample是切的patch的倍率
        # self.slide_downsample表示在哪个倍率下切patch
        # self.slide_level表示在哪个倍率下切patch的slide的level
        self.slide = slide
        self.patch_size = patch_size
        self.stride = stride
        self.patch_downsample = patch_downsample
        self.tissue_mask_threshold = tissue_mask_threshold
        self.transforms = transforms
        assert mask_level < slide.level_count, f"mask_level的数据超出了限制"
        if mask_level < 0:
            mask_level = self.slide.get_best_level_for_downsample(32)
        self.mask_level = mask_level
        best_patch_level = self.slide.get_best_level_for_downsample(patch_downsample)
        best_patch_downsample = self.slide.level_downsamples[best_patch_level]
        # 判断从哪一个level的图像上切patch
        if int(best_patch_downsample) != patch_downsample:
            self.slide_level = best_patch_level - 1
        else:
            self.slide_level = best_patch_level
        self.slide_downsample = self.slide.level_downsamples[self.slide_level]
        # 如果self.magnification为2，则在提取patch是，patch_size要*2，在resize回patch_size
        # 在提取组织区域时，mask_stride为patch_stride/mask_downsample*patch_downsample
        # 而在提取坐标的时候使用的是level=0时的坐标
        self.magnification = int(self.patch_downsample / self.slide_downsample)
        self.ExtractTissueCoordinates()

    def get_roi_region(self, mask_level, mthresh=7, use_otsu=False, sthresh=20, sthresh_up=255, close=0):
        img = np.array(
            self.slide.read_region((0, 0), mask_level, self.slide.level_dimensions[mask_level]).convert('RGB'))
        img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)  # Convert to HSV space
        img_med = cv2.medianBlur(img_hsv[:, :, 1], mthresh)  # Apply median blurring

        # Thresholding
        if use_otsu:
            _, img_otsu = cv2.threshold(img_med, 0, sthresh_up, cv2.THRESH_OTSU + cv2.THRESH_BINARY)
        else:
            _, img_otsu = cv2.threshold(img_med, sthresh, sthresh_up, cv2.THRESH_BINARY)

        # Morphological closing
        if close > 0:
            kernel = np.ones((close, close), np.uint8)
            img_otsu = cv2.morphologyEx(img_otsu, cv2.MORPH_CLOSE, kernel)

        img_otsu = morphology.remove_small_objects(
            img_otsu == 255, min_size=16 * 16, connectivity=2
        )
        img_otsu = morphology.remove_small_holes(img_otsu, area_threshold=200 * 200)
        return img_otsu

    def ExtractTissueCoordinates(self):
        self.Coordinate_list = []
        tissue_mask = self.get_roi_region(self.mask_level)
        tissue_mask_downsample = int(self.slide.level_downsamples[self.mask_level])
        tissue_mask = tissue_mask * 1
        mask_sH, mask_sW = tissue_mask.shape

        mask_patch_size = int(self.patch_size/tissue_mask_downsample*self.patch_downsample)
        mask_stride = int(self.stride/tissue_mask_downsample*self.patch_downsample)
        mask_patch_area = mask_patch_size**2
        print(f"mask level dimensions {self.slide.level_dimensions[self.mask_level]}, mask patch size {mask_patch_size}, mask stride: {mask_stride}")
        print(f"patch downsample {self.patch_downsample}, slide downsample {self.slide_downsample}")

        for iw in range(int(mask_sW // mask_stride)):
            for ih in range(int(mask_sH // mask_stride)):
                mask_w = iw * mask_stride
                mask_h = ih * mask_stride
                if (mask_w + mask_patch_size) < mask_sW and (mask_h + mask_patch_size) < mask_sH:
                    tmask = tissue_mask[mask_h: mask_h+mask_patch_size, mask_w: mask_w+mask_patch_size]
                    mRatio = float(np.sum(tmask>0)) / mask_patch_area
                    if mRatio > self.tissue_mask_threshold:
                        ww = mask_w * tissue_mask_downsample
                        hh = mask_h * tissue_mask_downsample
                        self.Coordinate_list.append((ww, hh))

    def __getitem__(self, idx):
        coordinate = self.Coordinate_list[idx]
        if self.magnification != 1:
            patch = self.slide.read_region(coordinate, self.slide_level, (self.patch_size*2, self.patch_size*2)).convert('RGB')
            patch = patch.resize((self.patch_size, self.patch_size))
        else:
            patch = self.slide.read_region(coordinate, self.slide_level, (self.patch_size, self.patch_size)).convert('RGB')
        coordinate_str = f"{coordinate[0]}_{coordinate[1]}"
        patch = self.transforms(patch)
        return {"coordination": coordinate_str, "patch": patch}

    def __len__(self):
        return len(self.Coordinate_list)