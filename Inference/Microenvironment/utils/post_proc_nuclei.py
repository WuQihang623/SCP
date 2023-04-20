import cv2
import numpy as np
import time
from scipy.spatial import KDTree, distance_matrix


def convert_format(inst_info_dict, patch_size, patch_stride, downsample):
    # Extract cells from the overlay area and classify them
    def classify_x(patch_info, psize=256, edge=224):
        overlap_info = {1: {}}
        for idx, inst_info in patch_info.items():
            # if inst_info['bbox'][1, 0] > edge and inst_info['type'] > 0:
            if inst_info['bbox'][1, 0] > edge:
                overlap_info[1][idx] = inst_info
        return overlap_info

    def classify_y(patch_info, psize=256, edge=224):
        overlap_info = {1: {}}
        for idx, inst_info in patch_info.items():
            # if inst_info['bbox'][1, 1] > edge and inst_info['type'] > 0:
            if inst_info['bbox'][1, 1] > edge:
                overlap_info[1][idx] = inst_info
        return overlap_info

    def classify_right_patch(patch_info, edge=32):
        overlap_info = {1: {}}
        for idx, inst_info in patch_info.items():
            # if inst_info['bbox'][0, 0] < edge and inst_info['type'] > 0:
            if inst_info['bbox'][0, 0] < edge:
                overlap_info[1][idx] = inst_info
        return overlap_info

    def classify_bottom_patch(patch_info, edge=32):
        overlap_info = {1: {}}
        for idx, inst_info in patch_info.items():
            # if inst_info['bbox'][0, 1] < edge and inst_info['type'] > 0:
            if inst_info['bbox'][0, 1] < edge:
                overlap_info[1][idx] = inst_info
        return overlap_info

    def compute_iou(rec1, rec2):
        """
        computing IoU
        :param rec1: (y0, x0, y1, x1), which reflects
                (top, left, bottom, right)
        :param rec2: (y0, x0, y1, x1)
        :return: scala value of IoU
        """
        # computing area of each rectangles
        rec1 = [rec1[0, 1], rec1[0, 0], rec1[1, 1], rec1[1, 0]]
        rec2 = [rec2[0, 1], rec2[0, 0], rec2[1, 1], rec2[1, 0]]
        S_rec1 = (rec1[2] - rec1[0]) * (rec1[3] - rec1[1])
        S_rec2 = (rec2[2] - rec2[0]) * (rec2[3] - rec2[1])

        # computing the sum_area
        sum_area = S_rec1 + S_rec2

        # find the each edge of intersect rectangle
        left_line = max(rec1[1], rec2[1])
        right_line = min(rec1[3], rec2[3])
        top_line = max(rec1[0], rec2[0])
        bottom_line = min(rec1[2], rec2[2])

        # judge if there is an intersect
        if left_line >= right_line or top_line >= bottom_line:
            return 0, 0
        else:
            intersect = (right_line - left_line) * (bottom_line - top_line)
            return (intersect / (sum_area - intersect)) * 1.0, intersect

    def compute_area(bbox1, bbox2):
        area1 = (bbox1[1, 0] - bbox1[0, 0]) * (bbox1[1, 1] - bbox1[0, 1])
        area2 = (bbox2[1, 0] - bbox2[0, 0]) * (bbox2[1, 1] - bbox2[0, 1])
        return area1, area2

    def get_point_idx(num, i=3):
        i = int(num / i)
        j = num % i
        return [i, j]

    def mindistance(contour1, contour2):
        dis_matrix = distance_matrix(contour1, contour2)
        if dis_matrix.min() < 4:
            return True
        else:
            return False

    start = time.time()
    overlap = patch_size - patch_stride
    stride = int(patch_stride * downsample)
    i = 0
    inst_info_dict_raw = inst_info_dict.copy()
    for position_str, patch_info in inst_info_dict.items():
        position = [int(x) for x in position_str.split('_')]
        right_patch_info = inst_info_dict.get(f"{position[0] + stride}_{position[1]}")
        patch_deleted_idxs = []
        right_patch_deleted_idxs = []
        bottom_patch_deleted_idxs = []

        # If the right patch exists, delete the duplicate cells
        if right_patch_info:
            patch_info_X = classify_x(patch_info, patch_size, edge=patch_stride)
            right_patch_overlap_info = classify_right_patch(right_patch_info, edge=overlap)
            # Discuss the three situations respectively
            for category in [1]:
                for patch_cell_idx, patch_cell_info in patch_info_X[category].items():
                    patch_cell_bbox = patch_cell_info['bbox']
                    # Record the cell index of the right patch with the maximum intersection and union ratio with the cell's external rectangle
                    candidate_idx_list = []
                    candidate_intersect_list = []
                    for right_patch_cell_idx, right_patch_cell_info in right_patch_overlap_info[
                        category].items():
                        convert_right_cell_bbox = right_patch_cell_info['bbox'] + np.array(
                            [[patch_stride, 0]])
                        iou, intersect = compute_iou(patch_cell_bbox, convert_right_cell_bbox)
                        if iou > 0.05:
                            candidate_idx_list.append(right_patch_cell_idx)
                            candidate_intersect_list.append(intersect)
                    # Delete the information of the cell with smaller area
                    if candidate_idx_list:
                        for candidate_idx, candidate_intersect in zip(candidate_idx_list, candidate_intersect_list):
                            candidate_right_cell = right_patch_overlap_info[category][candidate_idx]
                            patch_cell_area, candidate_cell_area = compute_area(patch_cell_bbox,
                                                                                candidate_right_cell['bbox'])
                            if candidate_intersect / patch_cell_area > 0.3 or candidate_intersect / candidate_cell_area > 0.3:
                                if patch_cell_area > candidate_cell_area:
                                    right_patch_deleted_idxs.append(candidate_idx)
                                else:
                                    patch_deleted_idxs.append(patch_cell_idx)

        bottom_patch_info = inst_info_dict.get(f"{position[0]}_{position[1] + stride}")
        # If the bottom patch exists, delete the duplicate cells
        if bottom_patch_info:
            patch_info_Y = classify_y(patch_info, patch_size, patch_stride)
            bottom_patch_overlap_info = classify_bottom_patch(bottom_patch_info, overlap)
            # Discuss the three situations respectively
            for category in [1]:
                for patch_cell_idx, patch_cell_info in patch_info_Y[category].items():
                    patch_cell_bbox = patch_cell_info['bbox']
                    # Record the cell index of the bottom patch with the maximum intersection and union ratio with the cell's external rectangle
                    candidate_idx_list = []
                    candidate_intersect_list = []
                    for bottom_patch_cell_idx, bottom_patch_cell_info in bottom_patch_overlap_info[
                        category].items():
                        convert_bottom_cell_bbox = bottom_patch_cell_info['bbox'] + np.array([[0, patch_stride]])
                        iou, intersect = compute_iou(patch_cell_bbox, convert_bottom_cell_bbox)
                        if iou > 0.05:
                            candidate_idx_list.append(bottom_patch_cell_idx)
                            candidate_intersect_list.append(intersect)
                    # Delete the information of the cell with smaller area
                    if candidate_idx_list:
                        for candidate_idx, candidate_intersect in zip(candidate_idx_list, candidate_intersect_list):
                            candidate_bottom_cell = bottom_patch_overlap_info[category][candidate_idx]
                            patch_cell_area, candidate_cell_area = compute_area(patch_cell_bbox,
                                                                                candidate_bottom_cell['bbox'])
                            if candidate_intersect / patch_cell_area > 0.3 or candidate_intersect / candidate_cell_area > 0.3:
                                if patch_cell_area > candidate_cell_area:
                                    bottom_patch_deleted_idxs.append(candidate_idx)
                                else:
                                    patch_deleted_idxs.append(patch_cell_idx)

        # Remove duplicate indexes
        patch_deleted_idxs = list(set(patch_deleted_idxs))
        right_patch_deleted_idxs = list(set(right_patch_deleted_idxs))
        bottom_patch_deleted_idxs = list(set(bottom_patch_deleted_idxs))
        for idx in patch_deleted_idxs:
            try:
                inst_info_dict_raw[position_str].pop(idx)
            except:
                pass
        for idx in bottom_patch_deleted_idxs:
            try:
                inst_info_dict_raw[f"{position[0]}_{position[1] + stride}"].pop(idx)
            except:
                pass
        for idx in right_patch_deleted_idxs:
            try:
                inst_info_dict_raw[f"{position[0] + stride}_{position[1]}"].pop(idx)
            except:
                pass
        i += len(patch_deleted_idxs) + len(right_patch_deleted_idxs) + len(bottom_patch_deleted_idxs)
    print(f'重叠的细胞有{i}个')

    center_list = []
    type_list = []
    contour_list = []
    num_nucleus = [0, 0, 0, 0, 0, 0, 0, 0]
    for position_str, patch_info in inst_info_dict_raw.items():
        position = [int(x) for x in position_str.split('_')]
        position = np.array(position)
        for idx, inst in patch_info.items():
            # 不显示被判定为背景的细胞
            # if inst['type'] == 0:
            #     continue
            type = inst['type']
            num_nucleus[type] += 1
            type_list.append(inst['type'])
            center_list.append(inst['centroid'] * downsample + position)
            contour_list.append(np.int32(inst['contour'] * downsample + np.expand_dims(position, axis=0)))
    print(f"细胞总量: {num_nucleus}")
    print(f"统计所有细胞并删除重叠的细胞耗费了{time.time() - start:.3f}秒")
    return np.array(type_list, dtype=np.int8), np.array(center_list, dtype=np.int32), np.array(contour_list, dtype=object)