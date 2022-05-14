import datetime
import time
from typing import Tuple

import cv2
import numpy as np
from src.api.utils import GOPRO_FPS, GOPRO_HEIGHT, GOPRO_WIDTH, get_brightness


class VideoDisplay:
    def __init__(self, input_source:int):
        self.input_source = input_source

    def __call__(self):
        vidcap = cv2.VideoCapture(self.input_source)

        try:
            self._main_loop(vidcap)
        except KeyboardInterrupt:
            cv2.destroyAllWindows()
            vidcap.release()

    def _main_loop(self, vidcap:cv2.VideoWriter):
        while True:
            _success, frame = vidcap.read()
            if _success:
                """Feed frames to imshow to display video"""
                cv2.namedWindow("OpenCV Live Video Feed", cv2.WINDOW_NORMAL)
                cv2.imshow("OpenCV Live Video Feed", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    raise KeyboardInterrupt()


class VideoWriter:
    def __init__(self, input_source:int, output_file:str):
        self.input_source = input_source
        self.output_file = output_file

    def __call__(self):
        vidcap = cv2.VideoCapture(self.input_source)
        outwriter = self._init_vidwriter(self.output_file)

        try:
            self._main_loop(vidcap, outwriter)
        except KeyboardInterrupt:
            cv2.destroyAllWindows()
            vidcap.release()
            outwriter.release()

    def _main_loop(self, vidcap: cv2.VideoCapture, outwriter: cv2.VideoWriter):
        while True:
            _success, frame = vidcap.read()
            if _success:
                outwriter.write(frame)

    def _init_vidwriter(self, output_file: str) -> cv2.VideoWriter:
        """Create object to write to video output using properties
        from video input.
        """
        _output_file = _clean_filename(output_file)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        return cv2.VideoWriter(
            _output_file,
            fourcc,
            GOPRO_FPS,
            (GOPRO_WIDTH, GOPRO_HEIGHT),
        )


class VideoAnalyzer:
    def __init__(self, input_source: int, config: dict, buffer: int):
        self.input_source = input_source
        self.config = config
        self.buffer = buffer

    def __call__(self):
        vidcap = cv2.VideoCapture(self.input_source)

        try:
            self._main_loop(vidcap)
        except KeyboardInterrupt:
            cv2.destroyAllWindows()
            vidcap.release()

    def _main_loop(self, vidcap: cv2.VideoCapture):
        # Get time at start of loop
        start = _current_milli_time()

        # frame buffer is the number of frames to average
        # before writing to the terminal
        frame_buffer = []
        while True:
            _success, frame = vidcap.read()
            if _success:
                frame_buffer.append(frame)
                if len(frame_buffer) == self.buffer:
                    self._clear_framebuffer(frame_buffer.copy(), self.config, start)
                    frame_buffer.clear()

    def _clear_framebuffer(self, frame_buffer: list, config: dict, start: float):
        """Process frame buffer in separate process"""
        _now = (_current_milli_time() - start) / 1000
        raw, cell = _get_data(frame_buffer, config)
        print(
            f"t={_now:.3f}, raw_bri={raw:.3f}, cell_loss={cell:.3f}",
        )


def _get_data(frame_buffer: list, config: dict) -> Tuple[float, float]:
    """Calculate brightness and estimated cell count
    from buffer of frames.
    """
    _frame_mean = np.mean(np.stack(frame_buffer, axis=-1), axis=-1)
    raw = get_brightness(_frame_mean, config) - config["BRIGHTNESS"]
    cell = raw * float(config["ALPHA_BRI"]) + float(config["BETA_BRI"])
    return raw, cell


def _clean_filename(output_file: str):
    if not output_file == "MonthDate_Year.mp4":
        return output_file

    mydate = datetime.datetime.now()
    return mydate.strftime("%B%d_%Y.mp4")


def _current_milli_time():
    return round(time.time() * 1000)
