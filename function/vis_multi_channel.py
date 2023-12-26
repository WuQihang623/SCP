import numpy as np
from PIL import Image

def display_composite(img, choosed_channel: list = None, channel_intensities=None):
    """
    Display composite view of multi-channel image.
    Background is black. Each stain is rendered with a different colour.
    The stain's intensity controls colour transparency.
    Parameters:
    -----------
    img: np.array, shape(n_channels, rows, cols), np.float
        A multi-channel image - all intensities are positive
        floats
    colours: np.array(dtype = int), shape(n_channels, 3)
        The RGB colour selected for each stain [0,255].
        If unspecified, default colours are provided for up to
        7 stains.
    Returns:
    --------
    composite_image: PIL Image
    """
    colours = np.array(([
        [0, 0, 255], # DAPI
        [255, 255, 0], # 570
        [255, 0, 0], # 690
        [0, 255, 255], # 480
        [255, 128, 0], # 620
        [255, 255, 255], # 780
        [0, 255, 0], # 520
        [0, 0, 0] # Sample AF
    ]))

    if choosed_channel is None:
        choosed_channel = [i for i in range(img.shape[0])]
    if channel_intensities is None:
        channel_intensities = np.array([1 for i in range(img.shape[0])])
    else:
        channel_intensities = np.array(channel_intensities)
        channel_intensities = channel_intensities[choosed_channel]

    colours = colours[choosed_channel]
    back = np.zeros((img.shape[1], img.shape[2], 4)).astype(np.uint8)
    composite = Image.fromarray(back, 'RGBA')
    back_alpha = Image.new('L', (img.shape[2], img.shape[1]), 255)
    composite.putalpha(back_alpha)

    for i in range(len(choosed_channel)):
        channel_image = np.zeros((img.shape[1], img.shape[2], 4))
        channel_image[..., 0:-1] = colours[i]
        channel_image = Image.fromarray(channel_image.astype(np.uint8), 'RGBA')
        c = Image.fromarray(np.clip(img[i] * channel_intensities[i], 0, 255).astype(np.uint8))
        c.convert('L')
        channel_image.putalpha(c)
        composite = Image.alpha_composite(composite, channel_image)

    return composite