import glob
import random
from re import L

import albumentations as A
import cv2
import numpy as np
from src.segment.utils import rescale_image


def load_dataset(image_path: str, mask_path: str):
    dataset = {"images": [], "masks": []}
    for key, path in zip(dataset, (image_path, mask_path)):
        for _path in glob.glob(f"{path}/*.jpg"):
            _img_0 = cv2.imread(_path)
            _img = rescale_image(_img_0)
            dataset[key].append(_img)
    dataset["masks"] = _convert_masks(dataset["masks"])
    return dataset


def split_dataset(dataset: dict, train_split: float = 0.7):
    l_dataset = len(dataset["images"])
    n_train = int(train_split * l_dataset)
    indices = range(l_dataset)
    train = random.sample(indices, n_train)
    test = list(set(indices) - set(train))

    X_train, y_train = zip(
        *[(dataset["images"][i], dataset["masks"][i]) for i in train]
    )
    X_test, y_test = zip(*[(dataset["images"][i], dataset["masks"][i]) for i in test])
    X_train, y_train, X_test, y_test = map(np.stack, (X_train, y_train, X_test, y_test))
    return X_train, y_train, X_test, y_test


def augment_dataset(dataset: dict):
    _dataset = {"images": [], "masks": []}
    transformations = _get_transformations(dataset["images"][0].shape)
    for _img, _mask in zip(dataset["images"], dataset["masks"]):
        _img = _img.astype(np.uint8)
        _mask = _mask.astype(np.uint8)
        _dataset["images"].append(_img)
        _dataset["masks"].append(_mask)
        for _trans in transformations:
            _aug = _trans(image=_img, mask=_mask)
            _dataset["images"].append(_aug["image"])
            _dataset["masks"].append(_aug["mask"])
    return _dataset


def _convert_masks(masks: list):
    masks_out = []
    for mask in masks:
        _mask = mask[..., 0]
        _mask[_mask > 0] = 1
        masks_out.append(_mask)
    return masks_out


def _get_transformations(img_shape: tuple):
    original_height, original_width, _ = img_shape
    return (
        A.Compose(
            [
                A.RandomCrop(width=original_height, height=original_width),
                A.HorizontalFlip(p=0.5),
                A.RandomBrightnessContrast(p=0.2),
            ]
        ),
        A.Compose(
            [
                A.ElasticTransform(
                    p=1, alpha=120, sigma=120 * 0.05, alpha_affine=120 * 0.03
                ),
                A.RandomRotate90(p=1),
            ]
        ),
        A.Compose(
            [
                A.OneOf(
                    [
                        A.RandomSizedCrop(
                            min_max_height=(50, 101),
                            height=original_height,
                            width=original_width,
                            p=0.5,
                        ),
                        A.PadIfNeeded(
                            min_height=original_height, min_width=original_width, p=0.5
                        ),
                    ],
                    p=1,
                ),
                A.VerticalFlip(p=0.5),
                A.RandomRotate90(p=0.5),
                A.OneOf(
                    [
                        A.ElasticTransform(
                            p=0.5, alpha=120, sigma=120 * 0.05, alpha_affine=120 * 0.03
                        ),
                        A.GridDistortion(p=0.5),
                        A.OpticalDistortion(distort_limit=1, shift_limit=0.5, p=1),
                    ],
                    p=0.8,
                ),
            ]
        ),
        A.Compose(
            [
                A.VerticalFlip(p=0.5),
                A.RandomRotate90(p=0.5),
                A.CLAHE(p=0.8),
                A.RandomBrightnessContrast(p=0.8),
                A.RandomGamma(p=0.8),
            ]
        ),
    )
