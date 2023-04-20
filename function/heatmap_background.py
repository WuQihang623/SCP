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

def numpy_to_pixmap(image: np.ndarray) -> QPixmap:
    """
    Convert a NumPy array to a QPixmap.
    """
    # Convert the image to a QImage.
    height, width, channel = image.shape
    bytes_per_line = channel * width
    qimage = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
    # Convert the QImage to a QPixmap.
    qpixmap = QPixmap.fromImage(qimage)
    return qpixmap

def get_heatmap_background(slide_helper: SlideHelper, heatmap):
    level = slide_helper.get_max_level()
    dimension = slide_helper.get_level_dimension(-1)
    if heatmap.dtype != 'uint8':
        heatmap = np.uint8(heatmap)
    heatmap = cv2.resize(heatmap, dimension, cv2.INTER_NEAREST)
    slide = slide_helper.get_overview(level, dimension).convert('RGB')
    slide = np.array(slide, dtype=np.float32) / 255
    heatmap = show_cam_on_image(slide, heatmap, True)
    heatmap = numpy_to_pixmap(heatmap)
    return heatmap