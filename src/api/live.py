import sys
import time
from typing import Optional, Tuple

import cv2
import numpy as np
from src.config import ENV
from src.extra.reset_coords import BoundingBoxWidget


def analyze_live_video(input_source: Optional[str], cal_time: int = 0.5):
    vidcap = cv2.VideoCapture(input_source)
    _main_loop(vidcap, cal_time, _get_config())


def _get_config():
    config = ENV._asdict()
    config["BRIGHTNESS"] = 0
    return config


def _main_loop(vidcap: cv2.VideoCapture, cal_time: int, config: Tuple):
    # This gives us the frame that we will calibrate on
    _cal = int(vidcap.get(cv2.CAP_PROP_FPS) * cal_time)
    _start = current_milli_time()
    _n_frame = 0
    print(f"Calibration will automatically start after {cal_time} seconds")
    while True:
        _n_frame += 1
        success, _frame = vidcap.read()

        if success:
            if _n_frame == _cal:
                print("Re-calibrating... time will be reset to zero")
                config = _calibrate(_frame, config)
                _start = current_milli_time()
            else:
                _time = (current_milli_time() - _start) / 1000
                _raw = _get_brightness(_frame, config) - config["BRIGHTNESS"]
                _cell = _raw * float(config["ALPHA_BRI"]) + float(config["BETA_BRI"])
                print(
                    f"t={_time}, raw_bri={_raw:.3f}, cell_loss={_cell:.3f}",
                    file=sys.stdout,
                )


def _calibrate(input_image: np.ndarray, config: dict):
    (config["X"], config["Y"], config["W"], config["H"]) = _reset_basis(input_image)
    config["BRIGHTNESS"] = _get_brightness(input_image, config)
    return config


def _reset_basis(input_image: np.ndarray):
    bbx_wid = BoundingBoxWidget(input_image)
    while True:
        cv2.imshow("image", bbx_wid.show_image())
        key = cv2.waitKey(1)

        if key == ord("q"):
            cv2.destroyAllWindows()
            cv2.waitKey(1)
            return bbx_wid.coords()


def _get_brightness(input_image: np.ndarray, config: Tuple):
    crop_frame = input_image[
        int(config["Y"]) : int(config["Y"]) + int(config["H"]),
        int(config["X"]) : int(config["X"]) + int(config["W"]),
        :,
    ]
    _slice = _frame_to_slice(crop_frame, config)
    top, bottom = int(config["WIN_TOP"]), int(config["WIN_BOTTOM"])
    return np.mean(_slice[top:bottom])


def _frame_to_slice(frame: np.ndarray, config: dict) -> np.ndarray:
    _imageGREY = frame.mean(axis=2)
    mean_xaxis = _imageGREY.mean(axis=1)
    return _grouped_avg(mean_xaxis, config)


def _grouped_avg(myArray: np.array, config: dict) -> np.array:
    N = int(config["SLICE_FREQ"])
    result = np.cumsum(myArray, 0)[N - 1 :: N] / float(N)
    result[1:] = result[1:] - result[:-1]
    return result


def current_milli_time():
    return round(time.time() * 1000)
