import glob
import pickle
from function.extract_contour import extract_contour

path_list = glob.glob('results/Microenv/*/*.pkl')
for path in path_list:
    with open(path, 'rb') as f:
        result_info = pickle.load(f)
        f.close()

    color_list = [[0, 0, 0], [255, 0, 0], [255, 255, 78], [0, 255, 0], [0, 0, 255]]
    tissue_contours_microenv, tissue_colors_microenv, tissue_class_microenv = \
                        extract_contour(result_info['mask'],
                                        int(result_info['heatmap_downsample']),
                                        color_list, 4)
    with open(path, 'wb') as f:
        result_info['region_contours'] = tissue_contours_microenv
        result_info['region_colors'] = tissue_colors_microenv
        result_info['region_types'] = tissue_class_microenv
        pickle.dump(result_info, f)
        f.close()