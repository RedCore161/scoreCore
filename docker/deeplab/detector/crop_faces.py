"""
    @author Niek Andresen
    @date Mar 2021

    Just a bit of code to crop a box out of an image and store the cropped image.
"""

from skimage.io import imread, imsave


def crop_image_internal(img, bbox):
    """ Returns the croped image using bbox.
    Image smaller than bbox if bbox not fully within image shape.

    Args:
      img: numpy array
      bbox: tuple (r_min, r_max, c_min, c_max)

    Returns:
      img: numpy array
    """
    shape = img.shape
    r_min, r_max, c_min, c_max = bbox
    r_min, r_max, c_min, c_max = max(r_min, 0), min(r_max, shape[0]), max(c_min, 0), min(c_max, shape[1])
    return img[r_min:r_max, c_min:c_max, :]


def crop(impath, bbox, respath):
    img = imread(impath)
    imsave(respath, crop_image_internal(img, bbox))
