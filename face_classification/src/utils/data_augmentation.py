import numpy as np
from random import shuffle
from .preprocessor import preprocess_input
from .preprocessor import _imread as imread
from .preprocessor import _imresize as imresize
from .preprocessor import to_categorical
import scipy.ndimage as ndi
import cv2


class ImageGenerator(object):
    """ Image generator with saturation, brightness, lighting, contrast,
    horizontal flip and vertical flip transformations. It supports
    bounding boxes coordinates.

    TODO:
        - Finish support for not using bounding_boxes
            - Random crop
            - Test other transformations
    """
    def __init__(self, ground_truth_data, batch_size, image_size,
                 train_keys, validation_keys,
                 ground_truth_transformer=None,
                 path_prefix=None,
                 saturation_var=0.5,
                 brightness_var=0.5,
                 contrast_var=0.5,
                 lighting_std=0.5,
                 horizontal_flip_probability=0.5,
                 vertical_flip_probability=0.5,
                 do_random_crop=False,
                 grayscale=False,
                 zoom_range=[0.75, 1.25],
                 translation_factor=.3):

        self.ground_truth_data = ground_truth_data
        self.ground_truth_transformer = ground_truth_transformer
        self.batch_size = batch_size
        self.path_prefix = path_prefix
        self.train_keys = train_keys
        self.validation_keys = validation_keys
        self.image_size = image_size
        self.grayscale = grayscale
        self.color_jitter = []
        if saturation_var:
            self.saturation_var = saturation_var
            self.color_jitter.append(self.saturation)
        if brightness_var:
            self.brightness_var = brightness_var
            self.color_jitter.append(self.brightness)
        if contrast_var:
            self.contrast_var = contrast_var
            self.color_jitter.append(self.contrast)
        self.lighting_std = lighting_std
        self.horizontal_flip_probability = horizontal_flip_probability
        self.vertical_flip_probability = vertical_flip_probability
        self.do_random_crop = do_random_crop
        self.zoom_range = zoom_range
        self.translation_factor = translation_factor

    def _gray_scale(self, image_array):
        return image_array.dot([0.299, 0.587, 0.114])

    def saturation(self, image_array):
        gray_scale = self._gray_scale(image_array)
        alpha = 2.0 * np.random.random() * self.brightness_var
        alpha = alpha + 1 - self.saturation_var
        image_array = (alpha * image_array + (1 - alpha) *
                       gray_scale[:, :, None])
        return np.clip(image_array, 0, 255)

    def brightness(self, image_array):
        alpha = 2 * np.random.random() * self.brightness_var
        alpha = alpha + 1 - self.saturation_var
        image_array = alpha * image_array
        return np.clip(image_array, 0, 255)

    def contrast(self, image_array):
        gray_scale = (self._gray_scale(image_array).mean() *
                      np.ones_like(image_array))
        alpha = 2 * np.random.random() * self.contrast_var
        alpha = alpha + 1 - self.contrast_var
        image_array = image_array * alpha + (1 - alpha) * gray_scale
        return np.clip(image_array, 0, 255)



    def horizontal_flip(self, image_array, box_corners=None):
        if np.random.random() < self.horizontal_flip_probability:
            image_array = image_array[:, ::-1]
            if box_corners is not None:
                box_corners[:, [0, 2]] = 1 - box_corners[:, [2, 0]]
        return image_array, box_corners