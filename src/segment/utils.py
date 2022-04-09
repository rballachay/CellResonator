import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras


def jaccard_index(y_true: tf.Tensor, y_pred: tf.Tensor):
    y_true_f = keras.layers.Flatten()(y_true)
    y_pred_f = keras.layers.Flatten()(y_pred)
    intersection = keras.backend.sum(y_true_f * y_pred_f)
    return (intersection + 1.0) / (
        keras.backend.sum(y_true_f) + keras.backend.sum(y_pred_f) - intersection + 1.0
    )


def rescale_image(img: np.ndarray):
    h, w, _ = img.shape
    gap = int((w - h) / 2)
    return cv2.resize(img[:, gap:-gap], (320, 320), interpolation=cv2.INTER_LINEAR)
