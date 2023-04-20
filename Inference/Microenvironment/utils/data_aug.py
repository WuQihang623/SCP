import torch
import numpy as np
from skimage import color
from PIL import Image, ImageEnhance
from torchvision import transforms as T

class ColorDeConv:
    def __call__(self, img):
        img = np.array(img, dtype=np.uint8)
        assert img.shape[2] == 3
        img = img / 255.0
        null = np.zeros_like(img[:, :, 0])
        img_hed = color.rgb2hed(img)
        img_h = color.hed2rgb(np.stack((img_hed[:, :, 0], null, null), axis=-1))
        return Image.fromarray(np.array(img_h * 255, dtype=np.uint8))

class EnhanceContrast:
    def __init__(self, constrast=2):
        self.constrast = constrast

    def __call__(self, img):
        assert isinstance(img, Image.Image)
        img_en = ImageEnhance.Contrast(img)
        return img_en.enhance(self.constrast)

class ToTensor:
    def __init__(self):
        self.func = T.ToTensor()

    def __call__(self, img):
        img = self.func(img)
        return img

class Normalize:
    def __init__(self, mean, std):
        self.func = T.Normalize(mean=mean, std=std)

    def __call__(self, img):
        img = self.func(img)
        return img

class transforms:
    def __init__(self, transforms: list):
        self.trans = transforms

    def __call__(self, img):
        for tran in self.trans:
            img = tran(img)
        return img