import multiprocessing
from typing import Optional

import cv2
import numpy as np
from src.api.utils import GOPRO_HEIGHT, GOPRO_WIDTH, get_brightness
from src.api.video import VideoAnalyzer, VideoDisplay, VideoWriter
from src.config import ENV
from src.extra.reset_coords import BoundingBoxWidget


def analyze_live_video(
    input_source: Optional[int],
    output_file: str,
    calibrate: bool = False,
    buffer: int = 1,
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

    _run_multiprocess(input_source, output_file, config, buffer)


def _run_multiprocess(input_source: int, output_file: str, config: dict, buffer: int):
    """The video display, video writing and video analysis are done in three
    separate processes. This was done to solve problems relating to multi-threading
    the video writing. Note that each cv2.VideoWriter has to be in a separate process,
    because it is not serializable.
    """

    # start the process to display to live output
    vid_display = multiprocessing.Process(target=VideoDisplay(input_source))
    vid_display.start()

    # start the process to write out output video file
    vid_writing = multiprocessing.Process(target=VideoWriter(input_source, output_file))
    vid_writing.start()

    # start the process to read in frames, process, and write to terminal
    vid_analysis = multiprocessing.Process(
        target=VideoAnalyzer(input_source, config, buffer)
    )
    vid_analysis.start()


def _calibrate(input_source: Optional[str], config: dict) -> dict:
    """Custom function for calibrating region of interest
    on camera. Only use if you cannot use src.reset.
    """
    vidcap = cv2.VideoCapture(input_source)

    # take the fifth frame
    for _ in range(100):
        _, _frame = vidcap.read()
    vidcap.release()

    print("Re-calibrating... time will be reset to zero")
    (config["X"], config["Y"], config["W"], config["H"]) = _reset_basis(_frame)
    config["BRIGHTNESS"] = get_brightness(_frame, config)
    return config


def _reset_basis(input_image: np.ndarray):
    """Reset the basis (coordinates of ROI)."""
    bbx_wid = BoundingBoxWidget(input_image)
    while True:
        cv2.imshow("image", bbx_wid.show_image())
        cv2.resizeWindow("image", GOPRO_WIDTH, GOPRO_HEIGHT)
        key = cv2.waitKey(1)

        if key == ord("q"):
            cv2.destroyAllWindows()
            cv2.waitKey(1)
            return bbx_wid.coords()


def _get_config():
    config = ENV._asdict()
    config["BRIGHTNESS"] = 0
    return config
