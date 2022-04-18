#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 13 12:08:37 2021

@author: RileyBallachay
"""
import os
from typing import List, Tuple

import cv2
import numpy as np
from src.config import ENV
from src.extra.tools import check_dir_make
from src.run.resize import get_downscaled_video
from src.segment.inference import get_resonator_roi


class ResonatorPipeline:
    def __init__(
        self,
        video_path: str,
        basis_image: str = ENV.BASIS_IMAGE,
        out_folder: str = None,
        height: int = int(ENV.H),
        filename: str = ENV.SLICED_FILENAME,
        downsize: bool = False,
        slice_freq: int = int(ENV.SLICE_FREQ),
    ):
        # video is unnecessarily big in native format
        self.video_path = get_downscaled_video(video_path, downsize)

        if out_folder is None:
            out_folder = f"{os.sep.join(video_path.split(os.sep)[:-1])}{os.sep}results"

        self.out_folder = check_dir_make(out_folder)

        self.basis = basis_image
        self.H = height
        self.filename = filename
        self.slice_freq = slice_freq

    def run(self, cropped_vid: str = ENV.CROPPED_FILENAME):

        # run normalization (register, brightness)
        self.normalize_data()

        # check that homography worked
        self._check_crop()

        # run the pipeline, write output video
        slices = self._pipeline_main(cropped_vid)

        # stack data and save
        slice_path = self._stack_and_save(slices)

        return slice_path

    def normalize_data(self):
        # get the 100 frame for registration and normalization
        frame_100 = self._get_frame_100()

        rect = get_resonator_roi(frame_100)

        # keep height as a constant
        self.X, self.Y, self.W, self.H = rect

    def _get_frame_100(self) -> np.array:
        # Grab the first frame from our reference photo
        vidcap = cv2.VideoCapture(self.video_path)

        # take 100th frame to avoid issues with reading
        # first frame
        for _ in range(100):
            success, vid = vidcap.read()
        if not success:
            raise Exception(f"Error reading 10th frame from path {self.video_path}")

        return vid

    def _check_crop(self):
        # Check to see if the crop region returns nothing
        cap = cv2.VideoCapture(self.video_path)

        # get the 5th frame to avoid problems with the first
        for _ in range(5):
            success, image = cap.read()
        cap.release()

        if success:
            crop_frame = image[self.Y : self.Y + self.H, self.X : self.X + self.W, :]
            if np.all((crop_frame == 0)):
                raise Exception(
                    "The crop region is empty - this typically happens when the basis image need to be reset. Please see how to reset basis image in the README."
                )

    def _pipeline_main(self, cropped_vid: str) -> List[np.array]:

        cap = cv2.VideoCapture(self.video_path)

        # Some characteristics from the original video
        self.fps, _ = cap.get(cv2.CAP_PROP_FPS), cap.get(cv2.CAP_PROP_FRAME_COUNT)

        # output
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        out = cv2.VideoWriter(
            f"{self.out_folder}{os.sep}{cropped_vid}",
            fourcc,
            self.fps,
            (self.W, self.H),
        )

        slices = []

        # Now we start
        while cap.isOpened():
            ret, frame = cap.read()

            # Avoid problems when video finish
            if ret:
                crop_frame = self._get_roi(frame)
                slices.append(frame_to_slice(crop_frame))
                out.write(crop_frame)
            else:
                break

        cap.release()
        out.release()

        return slices

    def _get_roi(self, img: np.ndarray):
        return img[self.Y : self.Y + self.H, self.X : self.X + self.W, :]

    def _stack_and_save(self, slices: List[np.array]) -> str:
        sliced = np.stack(slices, axis=0)
        sliced = _grouped_avg(sliced)
        np.savetxt(f"{self.out_folder}{os.sep}{self.filename}", sliced, delimiter=",")
        return f"{self.out_folder}{os.sep}{self.filename}"


def frame_to_slice(frame: np.ndarray) -> np.ndarray:
    _imageGREY = frame.mean(axis=2)
    return _imageGREY.mean(axis=1)


def _grouped_avg(myArray: np.array, slice_freq: int = int(ENV.SLICE_FREQ)) -> np.array:
    N = slice_freq
    result = np.cumsum(myArray, 0)[N - 1 :: N] / float(N)
    result[1:] = result[1:] - result[:-1]
    return result
