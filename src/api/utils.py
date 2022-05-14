from typing import Tuple

import numpy as np
from src.core.resonator_pipeline import frame_to_slice

# HARD DEFINE CONSTANTS TO BE USED FOR GOPRO CAMERA
# I AM UNABLE TO GET THE GOPRO FRAME ATTRIBUTES USING OPENCV
GOPRO_FPS = 30
GOPRO_WIDTH = 1920
GOPRO_HEIGHT = 1080


def get_brightness(input_image: np.ndarray, config: Tuple) -> float:
    """Calculate brightness of ROI"""
    crop_frame = input_image[
        int(config["Y"]) : int(config["Y"]) + int(config["H"]),
        int(config["X"]) : int(config["X"]) + int(config["W"]),
        :,
    ]
    _slice = frame_to_slice(crop_frame)
    top, bottom = int(config["WIN_TOP"]), int(config["WIN_BOTTOM"])
    return np.mean(_slice[top:bottom])
