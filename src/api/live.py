import sys
import time
from typing import Optional, Tuple

import cv2
import numpy as np
from src.config import ENV
from src.core.resonator_pipeline import frame_to_slice
from src.extra.reset_coords import BoundingBoxWidget


def analyze_live_video(
    input_source: Optional[str], calibrate: bool = False, buffer: int = 1
):
    """High-level function for analyzing live video feed. Calls main
    loop, until keyboard exit is pressed, then destroys windows and
    releases video cap.
    """

    # Get config
    config = _get_config()

    # Calibrate ROI if necessary
    if calibrate:
        config = _calibrate(input_source, config)

    # Create vidcap object with input source
    vidcap = cv2.VideoCapture(input_source)

    # Release the video camera when interrupted
    try:
        _main_loop(vidcap, _get_config(), buffer)
    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        vidcap.release()


def _main_loop(
    vidcap: cv2.VideoCapture,
    config: Tuple,
    buffer: int,
):
    """Read frames from video, calculate brightness
    and add to buffer. When buffer is full, report
    brightness to stdout.
    """

    # Get time at start of loop
    _start = _current_milli_time()

    frame_buffer = []
    while True:
        _success, _frame = vidcap.read()
        if _success:
            frame_buffer.append(_frame)
            if len(frame_buffer) == buffer:
                _now = (_current_milli_time() - _start) / 1000
                raw, cell = _get_data(frame_buffer, config)
                print(
                    f"t={_now:.3f}, raw_bri={raw:.3f}, cell_loss={cell:.3f}",
                )
                frame_buffer.clear()


def _get_data(frame_buffer, config):
    """Calculate brightness and estimated cell count
    from buffer of frames.
    """
    _frame_mean = np.mean(np.stack(frame_buffer, axis=-1), axis=-1)
    raw = _get_brightness(_frame_mean, config) - config["BRIGHTNESS"]
    cell = raw * float(config["ALPHA_BRI"]) + float(config["BETA_BRI"])
    return raw, cell


def _calibrate(input_source: Optional[str], config: dict):
    """Custom function for calibrating region of interest
    on camera. Only use if you cannot use src.reset.
    """
    vidcap = cv2.VideoCapture(input_source)

    # take the fifth frame
    for _ in range(5):
        _, _frame = vidcap.read()
    vidcap.release()

    print("Re-calibrating... time will be reset to zero")
    (config["X"], config["Y"], config["W"], config["H"]) = _reset_basis(_frame)
    config["BRIGHTNESS"] = _get_brightness(_frame, config)
    return config


def _reset_basis(input_image: np.ndarray):
    """Reset the basis (coordinates of ROI)."""
    bbx_wid = BoundingBoxWidget(input_image)
    while True:
        cv2.imshow("image", bbx_wid.show_image())
        key = cv2.waitKey(1)

        if key == ord("q"):
            cv2.destroyAllWindows()
            cv2.waitKey(1)
            return bbx_wid.coords()


def _get_brightness(input_image: np.ndarray, config: Tuple):
    """Calculate brightness of ROI"""
    crop_frame = input_image[
        int(config["Y"]) : int(config["Y"]) + int(config["H"]),
        int(config["X"]) : int(config["X"]) + int(config["W"]),
        :,
    ]
    _slice = frame_to_slice(crop_frame)
    top, bottom = int(config["WIN_TOP"]), int(config["WIN_BOTTOM"])
    return np.mean(_slice[top:bottom])


def _current_milli_time():
    return round(time.time() * 1000)


def _get_config():
    config = ENV._asdict()
    config["BRIGHTNESS"] = 0
    return config
