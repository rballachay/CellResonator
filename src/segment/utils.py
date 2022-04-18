from typing import Tuple

import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras

IMG_SCALE = 320


def jaccard_index(y_true: tf.Tensor, y_pred: tf.Tensor):
    y_true_f = keras.layers.Flatten()(y_true)
    y_pred_f = keras.layers.Flatten()(y_pred)
    intersection = keras.backend.sum(y_true_f * y_pred_f)
    return (intersection + 1.0) / (
        keras.backend.sum(y_true_f) + keras.backend.sum(y_pred_f) - intersection + 1.0
    )


def rescale_image(img: np.ndarray, scale: int = IMG_SCALE) -> np.ndarray:
    h, w, _ = img.shape
    gap = int((w - h) / 2)
    return cv2.resize(img[:, gap:-gap], (scale, scale), interpolation=cv2.INTER_LINEAR)


def upscale_mask(
    img_org: np.ndarray, coords: tuple, scale: int = IMG_SCALE
) -> Tuple[float, float, float, float]:
    # note that open cv considers x to be different than this package, thus x=y, w=h
    _h, _w, _ = img_org.shape
    _minside = min((_h, _w))
    gap = int(abs(_w - _h) / 2)
    _scale_factor = _minside / scale
    (x, y), (w, h), _ = coords
    x = (x - w / 2) * _scale_factor
    y = (y - h / 2) * _scale_factor
    w = w * _scale_factor
    h = h * _scale_factor
    x = x + gap
    return int(x), int(y), int(w), int(h)
