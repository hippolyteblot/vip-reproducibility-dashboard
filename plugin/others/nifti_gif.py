import numpy as np
from PIL import Image, ImageSequence
import imageio


def gif_compare(image1: np.ndarray, image2: np.ndarray, fps: int = 100, duration: float = 0.1, filename: str = None) -> None or list:
    """
    Creates a gif from two images that are the same size. The first image is displayed at the beginning of the gif and will fade into the second image.
    :param image1: First image
    :param image2: Second image
    :param fps: Frames per second
    :param duration: Duration of the gif
    :param filename: Name of the gif
    :return: None
    """

    # assert that the images are the same size
    if not (len(image1.shape) == 2 and len(image2.shape) == 2):
        raise ValueError("Images must be the same size with two dimensions. Dimensions are: {} and {}".format(len(image1.shape), len(image2.shape)))

    # Create a list of frames
    frames = []
    for i in range(0, int(fps * duration)):
        # Create a new image that is a weighted average of the two images
        print(image1)
        new_image = image1 * (1 - (i / (fps * duration))) + image2 * (i / (fps * duration))
        # Convert the image to PIL
        new_image = Image.fromarray(new_image)
        frames.append(new_image)

    if filename is not None:
        # Save the gif
        imageio.mimsave(filename, frames)
    else:
        return frames

def volumes_to_gif(vol1, vol2, slice, axis=0):
    """
    Creates a gif from two volumes that are the same size on the wanted slice. The first volume is displayed at the beginning of the gif and will fade into the second volume.
    :param vol1: First volume
    :param vol2: Second volume
    :param slice: Slice to use
    :return: None
    """
    slice1 = vol1.take(slice, axis=axis)
    slice2 = vol2.take(slice, axis=axis)
    gif_compare(slice1, slice2, filename='test.gif')


vol1 = imageio.volread("T2_to_SRI_brain-1.nii")
vol2 = imageio.volread("T2_to_SRI_brain-2.nii")
slice = 100
axis = 0
volumes_to_gif(vol1, vol2, slice, axis=axis)

