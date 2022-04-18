from typing import Tuple

import cv2
import numpy as np
from skimage import measure
from tensorflow import keras
from tensorflow.keras.models import load_model

from .utils import jaccard_index, rescale_image, upscale_mask


def get_resonator_roi(
    img: np.ndarray,
    model_path: str = "/Users/RileyBallachay/Desktop/training_vids/logging/model_v1.0.hdf5",
):
    model = _load_model(model_path)
    _mask = _predict(model, img)
    _clean_mask = _remove_mask_objs(_mask)
    _rect = _fit_rectangle(_clean_mask)
    return upscale_mask(img, _rect)


def _predict(model: keras.Model, img: np.ndarray):
    _img = np.expand_dims(rescale_image(img), 0)
    return np.where(np.squeeze(model.predict(_img)) > 0.5, 255, 0)


def _load_model(model_path: str):
    return load_model(model_path, custom_objects={"jaccard_index": jaccard_index})


def _remove_mask_objs(img: np.ndarray):
    labels_mask = measure.label(img)
    regions = measure.regionprops(labels_mask)
    regions.sort(key=lambda x: x.area, reverse=True)
    if len(regions) > 1:
        for rg in regions[1:]:
            labels_mask[rg.coords[:, 0], rg.coords[:, 1]] = 0
    labels_mask[labels_mask != 0] = 255
    return np.array(labels_mask).astype(np.uint8)


def _fit_rectangle(mask: np.ndarray):
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return cv2.minAreaRect(contours[0])


def test():
    path = "/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/data/basis/basis0.jpg"
    img = cv2.imread(path)
    rect = get_resonator_roi(img)
    x, y, w, h = upscale_mask(img, rect)
    rect2 = img[y : y + h, x : x + w, :]
    cv2.imshow("img", rect2)
    cv2.waitKey(0)


if __name__ == "__main__":
    test()
