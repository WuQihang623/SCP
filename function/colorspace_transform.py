import numpy as np
from PyQt5 import QtGui
from skimage.color import rgb2hed, hed2rgb

def ndarray_to_pixmap(array):
    height, width, channel = array.shape
    bytes_per_line = channel * width
    qimage = QtGui.QImage(array.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
    # 将QImage对象转换为QPixmap对象
    pixmap = QtGui.QPixmap.fromImage(qimage)
    return pixmap

def colordeconvolution(image, mode=1):
    image_rgb = np.array(image, dtype=np.uint8)[:, :, :3]
    image_hed = rgb2hed(image_rgb)
    null = np.zeros_like(image_hed[:, :, 0])
    if mode == 1:
        image = hed2rgb(np.stack((image_hed[:, :, 0], null, null), axis=-1)) * 255
    else:
        image = hed2rgb(np.stack((null, null, image_hed[:, :, 2]), axis=-1)) * 255
    image = image.astype(np.uint8)
    return image
