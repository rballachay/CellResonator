import datetime
import threading
import time
from typing import Optional, Tuple

import cv2
import numpy as np
from src.api.gopro import gopro_stream
from src.config import ENV
from src.core.resonator_pipeline import frame_to_slice
from src.extra.reset_coords import BoundingBoxWidget


def analyze_live_video(
    input_source: Optional[str],
    output_file: str,
    calibrate: bool = False,
    buffer: int = 1,
):
    """High-level function for analyzing live video feed. Calls main
    loop, until keyboard exit is pressed, then destroys windows and
    releases video cap.
    """
    # Get gopro mount if using gopro
    _clean_input = {"gopro": gopro_stream()}.get(input_source, input_source)

    # Get config
    config = _get_config()

    # Calibrate ROI if necessary
    if calibrate:
        config = _calibrate(_clean_input, config)

    # Create vidcap object with input source
    vidcap = cv2.VideoCapture(_clean_input)

    # Create object to write output to
    outwriter = _init_vidwriter(vidcap, output_file)

    # Release the video camera when interrupted
    try:
        _main_loop(vidcap, outwriter, _get_config(), buffer)
    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        vidcap.release()
        outwriter.release()


def _main_loop(
    vidcap: cv2.VideoCapture,
    outwriter: cv2.VideoWriter,
    config: Tuple,
    buffer: int,
):
    """Read frames from video, calculate brightness
    and add to buffer. When buffer is full, report
    brightness to stdout.
    """

    # Get time at start of loop
    start = _current_milli_time()

    frame_buffer = []
    while True:
        _success, frame = vidcap.read()
        if _success:
            frame_buffer.append(frame)

            # having video writing and imshow in the same thread caused errors
            vidwrite_thread = threading.Thread(
                target=_vid_thread, name="VidWriter", args=(outwriter, frame)
            )
            vidwrite_thread.start()

            # display video
            _display_frame(frame)

            if len(frame_buffer) == buffer:
                # same logic as with video writer thread, added to avoid errors
                buffer_thread = threading.Thread(
                    target=_clear_framebuffer,
                    name="DisplayData",
                    args=(frame_buffer.copy(), config, start),
                )
                buffer_thread.start()
                frame_buffer.clear()


def _display_frame(frame):
    """Feed frames to imshow to display video"""
    cv2.imshow("OpenCV Live Video Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        raise KeyboardInterrupt()


def _vid_thread(outwriter: cv2.VideoWriter, frame: np.ndarray):
    """Write frame to videowriter object in separate thread"""
    outwriter.write(frame)


def _clear_framebuffer(frame_buffer: list, config: dict, start: float):
    """Process frame buffer in separate thread"""
    _now = (_current_milli_time() - start) / 1000
    raw, cell = _get_data(frame_buffer, config)
    print(
        f"t={_now:.3f}, raw_bri={raw:.3f}, cell_loss={cell:.3f}",
    )


def _init_vidwriter(vidcap: cv2.VideoCapture, output_file: str) -> cv2.VideoWriter:
    """Create object to write to video output using properties
    from video input.
    """
    _output_file = _clean_filename(output_file)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    width = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    return cv2.VideoWriter(
        _output_file,
        fourcc,
        fps,
        (width, height),
    )


def _get_data(frame_buffer: list, config: dict) -> Tuple[float, float]:
    """Calculate brightness and estimated cell count
    from buffer of frames.
    """
    _frame_mean = np.mean(np.stack(frame_buffer, axis=-1), axis=-1)
    raw = _get_brightness(_frame_mean, config) - config["BRIGHTNESS"]
    cell = raw * float(config["ALPHA_BRI"]) + float(config["BETA_BRI"])
    return raw, cell


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


def _clean_filename(output_file: str):
    if not output_file == "MonthDate_Year.mp4":
        return output_file

    mydate = datetime.datetime.now()
    return mydate.strftime("%B%d_%Y.mp4")
