import time
import argparse
import os.path as osp

import openslide
import cv2 as cv2
import numpy as np
from skimage.filters import threshold_otsu


parser = argparse.ArgumentParser(description='Extracting patch')
parser.add_argument('--tumor_slide_path', type=str, default='/mnt/MedImg/CAMELYON16/tumor/')
parser.add_argument('--normal_slide_path', type=str, default='/mnt/MedImg/CAMELYON16/normal/')
parser.add_argument('--test_slide_path', type=str, default='/mnt/MedImg/CAMELYON16/test/')
parser.add_argument('--train_anno_path', type=str, default='/mnt/MedImg/CAMELYON16/lesion_annotations/')
parser.add_argument('--test_anno_path', type=str, default='/mnt/MedImg/CAMELYON16/lesion_annotations_test/')
parser.add_argument('--overlap', type=int, default=0)
parser.add_argument('--patch_size', type=int, default=256)
parser.add_argument('--save_dir', type=str, default='/mnt/MedImg/CAMELYON16/patch/20x256/clean/')


def extract_patch_each(slide_path, crop_size, level):
    slides = []
    targets = []
    grids = []
    wsi_name = osp.basename(slide_path).split('.')[0]
    print(wsi_name)
    with openslide.open_slide(slide_path) as slide:
        thumb_size = (int(slide.level_dimensions[level][0] / crop_size[0]),
                      int(slide.level_dimensions[level][1] / crop_size[1]))
        downsample = slide.level_downsamples[level]
        try:
            thumbnail = slide.get_thumbnail(slide.level_dimensions[-1])
        except:
            print("false")
            return 0
        else:
            print("true")
            slides.append(slide_path)
            thumbnail = thumbnail.resize(thumb_size)
            thum = np.array(thumbnail)
            wsi_mask = cv2.cvtColor(thum, cv2.COLOR_BGR2GRAY)
            gray_thresh, thresh_img = cv2.threshold(wsi_mask, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            thresh_img = 255 - thresh_img
            #cv2.imwrite('test_thresh.png', thresh_img)

            # convert to HSV space
            hsv_image = cv2.cvtColor(thum, cv2.COLOR_RGB2HSV)
            h, s, v = cv2.split(hsv_image)
            hthresh = threshold_otsu(h)
            sthresh = threshold_otsu(s)
            vthresh = threshold_otsu(v)
            # be min value for v can be changed later
            minhsv = np.array([hthresh, sthresh, 70], np.uint8)
            maxhsv = np.array([180, 255, vthresh], np.uint8)
            thresh = [minhsv, maxhsv]

            # find the bounding box of tissue
            rgbbinary = cv2.inRange(hsv_image, thresh[0], thresh[1])
            idxs = np.nonzero(rgbbinary)

            idxs = np.nonzero(thresh_img)
            grid = []
            patches = np.zeros(shape=(0,crop_size[0],crop_size[0],3))
            idh = idxs[0]
            idw = idxs[1]
            for j in range(len(idh)):
                height = idh[j]
                width = idw[j]
                height = int(height*crop_size[0]*downsample)
                width = int(width*crop_size[0]*downsample)
                patch = slide.read_region((width, height), level, (crop_size[0], crop_size[1])).convert('RGB')
                patcharr = np.array(patch)
                mask = cv2.cvtColor(patcharr, cv2.COLOR_RGB2GRAY)
                #cv2.imwrite('./mask.png', mask)
                _, thresh_img = cv2.threshold(mask, gray_thresh, 255, cv2.THRESH_BINARY)
                #c = cv2.countNonZero(thresh_img)
                #tissue -> 0 , background -> 255
                if cv2.countNonZero(thresh_img) < crop_size[0] * crop_size[1] * 0.6:
                    grid.append((width, height))
                    #patch = patch.resize((512, 512))
                    #patches = np.append(patches, np.expand_dims(patch, 0), 0)
            grids.append(grid)
            #grids[33] = grid
            lib = {
                'slides': slides,
                'grid': grids,
                'mult': 1,
                'level': level}
            return lib, patches


if __name__ == '__main__':
    global args
    args = parser.parse_args()
    level = 0  # 20x magnification
    mult = 1  # rescale by factor 2, so 20x magnification
    # 1024x1024 in 20x magnification, so crop 2048x2048 in 40x magnification then rescale.
    args.patch_size = 1024
    crop_size = [args.patch_size, args.patch_size]
    stride = args.patch_size - args.overlap

    print('Hi, patch extraction can take a while, please be patient...')
    ## Testing
    #slidepath = "/mnt/MedImg/CAMELYON16/tumor/tumor_002.tif"
    slidepath = "/mnt/MedImg/SLN/珠江医院病理图像1_阳性/H1312367/H1312367.dmetrix"
    crop_size = [256, 256]
    level = 1
    begin = time.time()
    test_lib, patch = extract_patch_each(slidepath, crop_size, level)
    end = time.time()
    print("Use time: ",  end-begin)

