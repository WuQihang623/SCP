import pickle
import sys

import cv2
import threading
import openslide
import pyclipper
import numpy as np
import tqdm
from PIL import Image
from skimage import morphology, color


def get_roi_region(slide, mask_level, sthresh=250, close=0):
    if mask_level == -1:
        mask_level = slide.get_best_level_for_downsample(64)
    thumbnail = slide.get_thumbnail(slide.level_dimensions[mask_level])
    thum = np.array(thumbnail, dtype=np.uint8)
    wsi_mask = cv2.cvtColor(thum, cv2.COLOR_BGR2GRAY)

    gray_thresh, thresh_img = cv2.threshold(wsi_mask, sthresh, 255, cv2.THRESH_BINARY)
    img_otsu = 255 - thresh_img
    downsample = slide.level_downsamples[mask_level]

    # Morphological closing
    if close > 0:
        kernel = np.ones((close, close), np.uint8)
        img_otsu = cv2.morphologyEx(img_otsu, cv2.MORPH_CLOSE, kernel)

    img_otsu = morphology.remove_small_holes(img_otsu, area_threshold=(400 // downsample) ** 2)
    img_otsu = morphology.remove_small_holes(img_otsu, area_threshold=(400 // downsample) ** 2)
    return img_otsu

def equidistant_zoom_contour(contour, margin, skip=10):
    """
    等距离缩放多边形轮廓点
    :param contour: 一个图形的轮廓格式[[[x1, x2]],...],shape是(-1, 1, 2)
    :param margin: 轮廓外扩的像素距离，margin正数是外扩，负数是缩小
    :return: 外扩后的轮廓点
    """
    margin = int(margin)
    pco = pyclipper.PyclipperOffset()
    ##### 参数限制，默认成2这里设置大一些，主要是用于多边形的尖角是否用圆角代替
    pco.MiterLimit = 10
    contour = contour[::skip, :]
    pco.AddPath(contour, pyclipper.JT_MITER, pyclipper.ET_CLOSEDPOLYGON)
    solutions = pco.Execute(margin)
    contour = []
    try:
        for i in range(len(solutions)):
            contour.append(np.array(solutions[i]).reshape(-1, 1, 2).astype(int))
    except:
        contour = np.array([])
    return contour

def color_deconv_DAB(image: Image.Image):
    """
    :param image: 0~255
    :return: 0~255
    """
    image = np.array(image) / 255
    null = np.zeros_like(image[:, :, 0])
    image_hed = color.rgb2hed(image)
    image_DAB = color.hed2rgb(np.stack((null, null, image_hed[:, :, 2]), axis=-1))
    image_DAB = cv2.cvtColor(np.uint8(image_DAB * 255), cv2.COLOR_BGR2GRAY)
    image_DAB = 255 - image_DAB
    return image_DAB / 255.0


def split_region(slide, slide_mpp, expansion_distance, mask, mask_downsample):
    def filter_contours(contours, hierarchy, filter_params: dict):
        """
                        Filter contours by: area.
                    """
        filtered = []
        # find indices of foreground contours (parent == -1)
        hierarchy_1 = np.flatnonzero(hierarchy[:, 1] == -1)
        all_holes = []
        # loop through foreground contour indices
        for cont_idx in hierarchy_1:
            # actual contour
            cont = contours[cont_idx]
            # indices of holes contained in this contour (children of parent contour)
            holes = np.flatnonzero(hierarchy[:, 1] == cont_idx)
            # take contour area (includes holes)
            a = cv2.contourArea(cont)
            # calculate the contour area of each hole
            hole_areas = [cv2.contourArea(contours[hole_idx]) for hole_idx in holes]
            # actual area of foreground contour region
            a = a - np.array(hole_areas).sum()
            if a == 0: continue
            if tuple((filter_params['a_t'],)) < tuple((a,)):
                filtered.append(cont_idx)
                all_holes.append(holes)
        foreground_contours = [contours[cont_idx] for cont_idx in filtered]
        hole_contours = []
        for hole_ids in all_holes:
            unfiltered_holes = [contours[idx] for idx in hole_ids]
            unfilered_holes = sorted(unfiltered_holes, key=cv2.contourArea, reverse=True)
            # take max_n_holes largest holes by area
            unfilered_holes = unfilered_holes[:filter_params['max_n_holes']]
            filtered_holes = []
            # filter these holes
            for hole in unfilered_holes:
                if cv2.contourArea(hole) > filter_params['a_h']:
                    filtered_holes.append(hole)
            hole_contours.append(filtered_holes)
        return foreground_contours, hole_contours

    tissue_mask = get_roi_region(slide=slide, mask_level=-1)
    tissue_mask = np.uint8(tissue_mask * 1)
    tissue_mask = cv2.resize(tissue_mask, (mask.shape[1], mask.shape[0]), cv2.INTER_NEAREST)
    mask_tumor = np.uint8((mask==1)*255)
    mask_tumor = cv2.GaussianBlur(mask_tumor, (45, 45), 0)
    mask_tumor = (mask_tumor>128)*255
    # 过滤掉比较小的区域
    mask_tumor = morphology.remove_small_objects(mask_tumor == 255,
                                                 min_size=(256 / mask_downsample) ** 2, connectivity=2)
    mask_tumor = morphology.remove_small_holes(mask_tumor, area_threshold=(256 / mask_downsample) ** 2)
    mask_tumor = np.array(mask_tumor * 255, dtype=np.uint8)

    # # 获取肿瘤边界
    # contours, hierarchy = cv2.findContours(mask_tumor, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # hierarchy = np.squeeze(hierarchy, axis=(0,))[:, 2:]
    # filter_params = {'a_t': 100, 'a_h': 16, 'max_n_holes': 100}
    # foreground_contours, hole_contours = filter_contours(contours, hierarchy, filter_params)
    #
    # mask_stroma = np.zeros_like(mask_tumor, dtype=np.uint8)
    # for i in range(len(foreground_contours)):
    #     contour = equidistant_zoom_contour(np.squeeze(foreground_contours[i]), int(expansion_distance/slide_mpp/mask_downsample))
    #     try:
    #         cv2.drawContours(mask_stroma, contour, -1, 255, -1)
    #     except:
    #         pass
    # for i in range(len(hole_contours)):
    #     if hole_contours[i] == []:
    #         continue
    #     for j in range(len(hole_contours[i])):
    #         contour = equidistant_zoom_contour(np.squeeze(hole_contours[i][j]), int(expansion_distance/slide_mpp/mask_downsample))
    #         try:
    #             cv2.drawContours(mask_stroma, contour, -1, 0, -1)
    #         except:
    #             pass
    # mask_stroma = np.logical_xor(mask_tumor, mask_stroma)
    # mask_stroma = np.logical_and(mask_stroma, tissue_mask)
    # mask_stroma = np.array(mask_stroma*255, dtype=np.uint8)
    # mask_other = np.uint8((np.ones_like(mask_tumor) - np.logical_or(mask_tumor, mask_stroma) * 1) * 255)

    mask_stroma = np.ones_like(mask_tumor) * 255 - mask_tumor
    mask_stroma = np.logical_and(mask_stroma, tissue_mask)
    mask_stroma = np.array(mask_stroma * 255, dtype=np.uint8)
    mask_other = np.uint8((np.ones_like(mask_tumor) - np.logical_or(mask_tumor, mask_stroma) * 1) * 255)
    return mask_tumor, mask_stroma, mask_other

def get_bounding_box(contour):
    contour1 = contour.copy()
    x_min = contour1[:, 0].min()
    y_min = contour1[:, 1].min()
    x_max = contour1[:, 0].max()
    y_max = contour1[:, 1].max()
    x_min = x_min - 2 if x_min > 1 else x_min
    y_min = y_min - 2 if y_min > 1 else y_min
    x_max += 2
    y_max += 2
    w = x_max - x_min
    h = y_max - y_min
    return [x_min, y_min, w, h]


def measure_PDL1(slide: openslide.OpenSlide,
                 slide_name: str,
                 type_nuclei_hovernet: dict,
                 type_pdl1_nuclei: dict,
                 expansion_distance: int,
                 threshold: float,
                 num_worker: int,
                 results_dir: str,
                 bar_signal_pdl1_judge=None):
    with open(f"{results_dir}/{slide_name}/{slide_name}_seg.pkl", 'rb') as f:
        region_info = pickle.load(f)
        f.close()
    with open(f"{results_dir}/{slide_name}/{slide_name}_nuclei.pkl", 'rb') as f:
        inst_info = pickle.load(f)
        f.close()

    mask = region_info["mask"]
    mask_downsample = region_info["heatmap_downsample"]
    type_arr = inst_info["type"]
    center_arr = inst_info["center"]
    contour_arr = inst_info["contour"]

    try:
        slide_mpp = float(slide.properties['openslide.mpp-x'])
    except:
        slide_mpp = 0.24
    mask_tumor, mask_stroma, mask_other = split_region(slide=slide,
                                           slide_mpp=slide_mpp,
                                           expansion_distance=expansion_distance,
                                           mask=mask,
                                           mask_downsample=mask_downsample)

    tumor_idx = type_nuclei_hovernet["tumor"]
    lymph_idx = type_nuclei_hovernet['lymph']
    macrophage_idx = type_nuclei_hovernet['macrophage']
    neutrophils_idx = type_nuclei_hovernet['neutrophils']
    pdl1_positive_tumor_idx = type_pdl1_nuclei['pdl1_positive_tumor']
    pdl1_negitive_tumor_idx = type_pdl1_nuclei['pdl1_negitive_tumor']
    pdl1_positive_immune_idx = type_pdl1_nuclei['pdl1_positive_immune']
    other_idx = type_pdl1_nuclei["other"]

    def Judge_PDL1(types, centers, contours, start_idx):
        if start_idx == 0:
            types = tqdm.tqdm(types, file=sys.stdout)
            length = len(types)
        for idx, (type, center, contour) in enumerate(zip(types, centers, contours)):
            contour_copy = contour.copy()
            if mask_other[int(center[1]/mask_downsample), int(center[0]/mask_downsample)] != 0:
                type_arr[start_idx + idx] = other_idx
                continue
            [x, y, w, h] = get_bounding_box(contour_copy)
            patch = slide.read_region((x, y), 0, (w, h)).convert('RGB')
            patch_DAB = color_deconv_DAB(patch)
            contour_copy[:, 0] = contour_copy[:, 0] - x
            contour_copy[:, 1] = contour_copy[:, 1] - y
            edge_mask = np.zeros_like(patch_DAB, dtype=np.uint8)
            outward_contour = equidistant_zoom_contour(contour_copy, 2, skip=2)
            inward_contour = equidistant_zoom_contour(contour_copy, -2, skip=2)
            cv2.drawContours(edge_mask, outward_contour, -1, 1, -1)
            cv2.drawContours(edge_mask, inward_contour, -1, 0, -1)
            if edge_mask.sum() == 0:
                ratio = 0
            else:
                ratio = (edge_mask * patch_DAB).sum() / edge_mask.sum()
            # 阳性
            if ratio > threshold:
                if mask_tumor[int(center[1]/mask_downsample), int(center[0]/mask_downsample)] != 0:
                    if type == tumor_idx:
                        type_arr[start_idx + idx] = pdl1_positive_tumor_idx
                    else:
                        type_arr[start_idx + idx] = pdl1_positive_immune_idx
                else:
                    if type == tumor_idx:
                        type_arr[start_idx + idx] = other_idx
                    else:
                        type_arr[start_idx + idx] = pdl1_positive_immune_idx
            else:
                if mask_tumor[int(center[1]/mask_downsample), int(center[0]/mask_downsample)] != 0:
                    if type == tumor_idx:
                        type_arr[start_idx + idx] = pdl1_negitive_tumor_idx
                    else:
                        type_arr[start_idx + idx] =  other_idx
                else:
                    type_arr[start_idx + idx] = other_idx
            if start_idx == 0 and bar_signal_pdl1_judge:
                bar_signal_pdl1_judge.emit(length, idx, 'PD-L1阳性判别进度：')

    batch_num = int(type_arr.shape[0] / num_worker)
    thread_list = []
    for worker_idx in range(num_worker):
        start_idx = worker_idx * batch_num
        t = threading.Thread(target=Judge_PDL1, args=(
            type_arr[start_idx: start_idx+batch_num], center_arr[start_idx: start_idx+batch_num],
            contour_arr[start_idx: start_idx+batch_num], start_idx
        ))
        thread_list.append(t)
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()

    # Judge_PDL1(type_arr, center_arr, contour_arr, 0)

    num_pdl1_positive_tumor = np.sum(type_arr==pdl1_positive_tumor_idx)
    num_pdl1_nagitice_tumor = np.sum(type_arr==pdl1_negitive_tumor_idx)
    num_pdl1_positive_immune = np.sum(type_arr==pdl1_positive_immune_idx)

    save_info = {"type": np.int8(type_arr), "center": np.int32(center_arr),
                "contour": np.array(contour_arr, dtype=object), "grid": {"x": [0], "y": [0]}}
    save_info.update(region_info)
    with open(f"{results_dir}/{slide_name}/{slide_name}_nuclei_pdl1.pkl", 'wb') as f:
        pickle.dump(save_info, f)
        f.close()

    return (num_pdl1_positive_tumor / (num_pdl1_nagitice_tumor + num_pdl1_positive_tumor) * 100), \
           ((num_pdl1_positive_immune + num_pdl1_positive_immune) / (num_pdl1_nagitice_tumor + num_pdl1_positive_tumor) * 100)
