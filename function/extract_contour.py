# 提取肿瘤分割结果mask中的轮廓
import cv2
import numpy as np

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

def extract_contour(mask, downsample, color_list, num_classes):
    tissue_contours = []
    colors = []
    types = []
    for class_idx in range(1, num_classes+1):
        sub_mask = mask.copy()
        sub_mask[sub_mask != class_idx] = 0
        try:
            contours, hierarchy = cv2.findContours(np.uint8(sub_mask), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            hierarchy = np.squeeze(hierarchy, axis=(0,))[:, 2:]
            filter_params = {'a_t': 100, 'a_h': 16, 'max_n_holes': 100}
            foreground_contours, hole_contours = filter_contours(contours, hierarchy, filter_params)
        except:
            continue
        for j in range(len(foreground_contours)):
            if cv2.contourArea(foreground_contours[j]) < (256 / downsample) ** 2:
                continue
            # 轮廓近似
            foreground_contours[j] = cv2.approxPolyDP(foreground_contours[j], 1, True)
            foreground_contours[j] *= downsample
            colors.append(color_list[class_idx])
            tissue_contours.append(np.squeeze(foreground_contours[j]))
            types.append(class_idx)
        for j in range(len(hole_contours)):
            if hole_contours[j]:
                for k in range(len(hole_contours[j])):
                    if cv2.contourArea(hole_contours[j][k]) < (256 / downsample) ** 2:
                        continue
                    hole_contours[j][k] *= downsample
                    colors.append(color_list[class_idx])
                    tissue_contours.append(np.squeeze(hole_contours[j][k]))
                    types.append(class_idx)

    return tissue_contours, colors, types