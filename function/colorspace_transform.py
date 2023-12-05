import numpy as np
from PyQt5 import QtGui
from skimage.color import rgb2hed, hed2rgb

# import cv2
# import torchstain
# from torchvision import transforms
# target = cv2.cvtColor(cv2.imread("./logo/stain.png"), cv2.COLOR_BGR2RGB)
# T = transforms.Compose([
#     transforms.ToTensor(),
#     transforms.Lambda(lambda x: x*255)
# ])
#
# torch_normalizer = torchstain.normalizers.MacenkoNormalizer(backend='torch')
# torch_normalizer.fit(T(target))


def ndarray_to_pixmap(array):
    height, width, channel = array.shape
    bytes_per_line = channel * width
    qimage = QtGui.QImage(array.copy().data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
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

# def normalizeStaining(img):
#     t_to_transform = T(img.convert("RGB"))
#     norm, H, E = torch_normalizer.normalize(I=t_to_transform, stains=True)
#     norm = norm.numpy().astype(np.uint8)
#     return norm

def normalizeStaining(img, Io=240, alpha=1, beta=0.15):
    ''' Normalize staining appearence of H&E stained images

    Example use:
        see test.py

    Input:
        I: RGB input image
        Io: (optional) transmitted light intensity

    Output:
        Inorm: normalized image
        H: hematoxylin image
        E: eosin image

    Reference:
        A method for normalizing histology slides for quantitative analysis. M.
        Macenko et al., ISBI 2009
    '''
    img = np.array(img, dtype=np.uint8)[:, :, :3]

    HERef = np.array([[0.5626, 0.2159],
                      [0.7201, 0.8012],
                      [0.4062, 0.5581]])

    maxCRef = np.array([1.9705, 1.0308])

    # define height and width of image
    h, w, c = img.shape

    # reshape image
    img = img.reshape((-1, 3))

    # calculate optical density
    OD = -np.log((img.astype(np.float32) + 1) / Io)

    # remove transparent pixels
    ODhat = OD[~np.any(OD < beta, axis=1)]
    if ODhat.shape[0] == 0:
        return img.reshape((h, w, 3))
    # compute eigenvectors
    eigvals, eigvecs = np.linalg.eigh(np.cov(ODhat.T))

    # eigvecs *= -1

    # project on the plane spanned by the eigenvectors corresponding to the two
    # largest eigenvalues
    That = ODhat.dot(eigvecs[:, 1:3])

    phi = np.arctan2(That[:, 1], That[:, 0])

    minPhi = np.percentile(phi, alpha)
    maxPhi = np.percentile(phi, 100 - alpha)

    vMin = eigvecs[:, 1:3].dot(np.array([(np.cos(minPhi), np.sin(minPhi))]).T)
    vMax = eigvecs[:, 1:3].dot(np.array([(np.cos(maxPhi), np.sin(maxPhi))]).T)

    # a heuristic to make the vector corresponding to hematoxylin first and the
    # one corresponding to eosin second
    if vMin[0] > vMax[0]:
        HE = np.array((vMin[:, 0], vMax[:, 0])).T
    else:
        HE = np.array((vMax[:, 0], vMin[:, 0])).T

    # rows correspond to channels (RGB), columns to OD values
    Y = np.reshape(OD, (-1, 3)).T

    # determine concentrations of the individual stains
    C = np.linalg.lstsq(HE, Y, rcond=None)[0]

    # normalize stain concentrations
    maxC = np.array([np.percentile(C[0, :], 99), np.percentile(C[1, :], 99)])
    tmp = np.divide(maxC, maxCRef)
    C2 = np.divide(C, tmp[:, np.newaxis])

    # recreate the image using reference mixing matrix
    Inorm = np.multiply(Io, np.exp(-HERef.dot(C2)))
    Inorm[Inorm > 255] = 254
    Inorm = np.reshape(Inorm.T, (h, w, 3)).astype(np.uint8)

    # # unmix hematoxylin and eosin
    # H = np.multiply(Io, np.exp(np.expand_dims(-HERef[:, 0], axis=1).dot(np.expand_dims(C2[0, :], axis=0))))
    # H[H > 255] = 254
    # H = np.reshape(H.T, (h, w, 3)).astype(np.uint8)
    #
    # E = np.multiply(Io, np.exp(np.expand_dims(-HERef[:, 1], axis=1).dot(np.expand_dims(C2[1, :], axis=0))))
    # E[E > 255] = 254
    # E = np.reshape(E.T, (h, w, 3)).astype(np.uint8)

    # return Inorm, H, E

    return Inorm
