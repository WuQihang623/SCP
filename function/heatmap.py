import cv2
import numpy as np
import openslide
from PyQt5.QtGui import QPixmap, QImage
from window.slide_window.utils.SlideHelper import SlideHelper

def show_cam_on_image(img: np.ndarray,
                      mask: np.ndarray,
                      use_rgb: bool = False,
                      colormap: int = cv2.COLORMAP_JET,
                      image_weight: float = 0.7) -> np.ndarray:
    """ This function overlays the cam mask on the image as an heatmap.
    By default the heatmap is in BGR format.

    :param img: The base image in RGB or BGR format.
    :param mask: The cam mask.
    :param use_rgb: Whether to use an RGB or BGR heatmap, this should be set to True if 'img' is in RGB format.
    :param colormap: The OpenCV colormap to be used.
    :param image_weight: The final result is image_weight * img + (1-image_weight) * mask.
    :returns: The default image with the cam overlay.
    """
    if mask.max() > 1:
        heatmap = cv2.applyColorMap(np.uint8(mask), colormap)
    else:
        heatmap = cv2.applyColorMap(np.uint8(255 * mask), colormap)
    # cv2.imwrite("/mnt/code2/wqh/my project/WSI_Classification/heatmap.jpg", heatmap)
    if use_rgb:
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    heatmap = (np.float32(heatmap) / 255).clip(0.2, 1)

    if np.max(img) > 1:
        raise Exception(
            "The input image should np.float32 in the range [0, 1]")

    if image_weight < 0 or image_weight > 1:
        raise Exception(
            f"image_weight should be in the range [0, 1].\
                Got: {image_weight}")

    cam = (1 - image_weight) * heatmap + image_weight * img
    cam = cam / 1.0
    return np.uint8(255 * cam)

def viz_tile_heatmap(slide, mask: np.ndarray,
                     window_box: list, level: int, mask_downsample: int):
    """
    :param slide: wsi or wsi's path
    :param mask: Predicted probability map, whose resolution has been down sampled
    :param window_box: The currently displayed view position(Under the current image level),
                       [upper left corner x, upper left corner y, width, height]
    :return: The type of heatmap is that you may need to resize it to the same size as the view window when displaying it.
    """
    assert level >= 0
    if isinstance(slide, str):
        slide = openslide.open_slide(slide)
    downsample = slide.level_downsamples[level]

    # Corresponding to the coordinate under level0
    slide_0_x_y = (int(window_box[0] * downsample), int(window_box[1] * downsample))
    wh = (window_box[2], window_box[3])
    tile = slide.read_region(slide_0_x_y, level, wh).convert('RGB')
    tile = np.float32(np.array(tile) / 255.0)

    # Corresponding to x, y, w, h on the heapmap
    mask_x = int(window_box[1] * downsample / mask_downsample)
    mask_y = int(window_box[0] * downsample / mask_downsample)
    mask_x_w = int(window_box[3] * downsample / mask_downsample)
    mask_y_h = int(window_box[2] * downsample / mask_downsample)

    tile_mask = mask[mask_x: mask_x+mask_x_w, mask_y: mask_y+mask_y_h]
    tile_mask = cv2.resize(tile_mask, wh)

    heatmap = show_cam_on_image(tile, tile_mask, use_rgb=True)
    return heatmap


