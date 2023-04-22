import cv2
import numpy as np
from PIL import Image

def sample_from_porbmap(probmap, distance=4, num_points=50):
    #
    num = 0
    all_coords = []
    kernel = np.ones((3, 3), np.uint8)
    thresholds = [1, 0.9, 0.7, 0.5, 0.2]
    for i in range(1, len(thresholds)):
        threshold_max = thresholds[i-1]
        threshold_min = thresholds[i]

        binary_map = np.logical_and(probmap <= threshold_max, probmap > threshold_min).astype('uint8')
        binary_map = cv2.erode(binary_map, kernel, iterations=1)
        coords = np.argwhere(binary_map==1)

        n_samples = int(binary_map.sum() / (distance**2))
        if num + n_samples > num_points:
            n_samples = num_points - num
        sample_coords = coords[np.random.choice(coords.shape[0], n_samples, replace=False)]
        all_coords.extend(sample_coords.tolist())
        num += n_samples
        if num > num_points:
            return all_coords
    return all_coords


if __name__ == '__main__':
    path = '../results/Diagnose/H1503537/H1503537_probs.npy'
    probmap = np.load(path)
    sample_from_porbmap(probmap)