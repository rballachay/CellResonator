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
from src.resize import get_downscaled_video
from src.utils import check_dir_make


class ResonatorPipeline:
    def __init__(
        self,
        video_path: str,
        basis_image: str = ENV.BASIS_IMAGE,
        out_folder: str = None,
        dims: dict = {
            "X": int(ENV.X),
            "Y": int(ENV.Y),
            "W": int(ENV.W),
            "H": int(ENV.H),
        },
        filename: str = ENV.SLICED_FILENAME,
        downsize: bool = False,
    ):
        # video is unnecessarily big in native format
        self.video_path = get_downscaled_video(video_path, downsize)

        if out_folder is None:
            out_folder = f"{os.sep.join(video_path.split(os.sep)[:-1])}{os.sep}results"

        self.out_folder = check_dir_make(out_folder)

        self.basis = basis_image
        self.X = dims["X"]
        self.Y = dims["Y"]
        self.W = dims["W"]
        self.H = dims["H"]
        self.filename = filename

    def run(self, cropped_vid: str = ENV.CROPPED_FILENAME):

        # run normalization (register, brightness)
        self.normalize_data()

        # run the pipeline, write output video
        slices = self._pipeline_main(cropped_vid)

        # stack data and save
        slice_path = self._stack_and_save(slices)

        return slice_path

    def normalize_data(self):
        # get the 100 frame for registration and normalization
        frame_100 = self._get_frame_100()

        # change norm to b+w and gaussian blur
        target_norm, basis_norm = self._norm_transform(
            frame_100, cv2.imread(self.basis)
        )

        # get homography for registration
        self._get_homography(target_norm, basis_norm)

        self.X, self.Y, self.W, self.H = self._warp_coordinates()

        # get the brightness ratio between the reference
        # video and the target
        self._set_brightness_ratio(target_norm, basis_norm)

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

    def _norm_transform(
        self, image_new: str, image_basis: str
    ) -> Tuple[np.array, np.array]:
        # Convert images to grayscale
        im1Gray = cv2.GaussianBlur(
            cv2.cvtColor(image_new, cv2.COLOR_BGR2GRAY),
            ksize=(5, 5),
            sigmaX=3,
            sigmaY=3,
        )
        im2Gray = cv2.GaussianBlur(
            cv2.cvtColor(image_basis, cv2.COLOR_RGB2GRAY),
            ksize=(5, 5),
            sigmaX=3,
            sigmaY=3,
        )
        return im1Gray, im2Gray

    def _get_homography(self, image_new: np.array, image_basis: np.array):
        MAX_FEATURES = 2000
        GOOD_MATCH_PERCENT = 0.5

        # Detect ORB features and compute descriptors.
        orb = cv2.ORB_create(MAX_FEATURES)
        keypoints1, descriptors1 = orb.detectAndCompute(image_new, None)
        keypoints2, descriptors2 = orb.detectAndCompute(image_basis, None)

        # Match features.
        matcher = cv2.DescriptorMatcher_create(
            cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING
        )
        matches = list(matcher.match(descriptors1, descriptors2, None))

        # Sort matches by score
        matches.sort(key=lambda x: x.distance, reverse=False)

        # Remove not so good matches
        numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
        matches = matches[:numGoodMatches]

        # Draw top matches
        imMatches = cv2.drawMatches(
            image_new, keypoints1, image_basis, keypoints2, matches, None
        )
        cv2.imwrite(f"{self.out_folder}{os.sep}{ENV.MATCHES_FILENAME}", imMatches)

        # Extract location of good matches
        points1 = np.zeros((len(matches), 2), dtype=np.float32)
        points2 = np.zeros((len(matches), 2), dtype=np.float32)

        for i, match in enumerate(matches):
            points1[i, :] = keypoints1[match.queryIdx].pt
            points2[i, :] = keypoints2[match.trainIdx].pt

        # Find homography
        self.homography, _ = cv2.findHomography(points1, points2, cv2.RANSAC)

    def _warp_coordinates(self) -> Tuple[int, int, int, int]:
        # this is the start, or the upper left corner of the mask
        start = np.matmul(self.homography, np.array((self.Y, self.X, 0)))

        # this is the bottom right corner of the mask
        end = np.matmul(
            self.homography, np.array((self.Y + self.H, self.X + self.W, 0))
        )
        return (
            int(start[1]),
            int(start[0]),
            int(end[1] - start[1]),
            int(end[0] - start[0]),
        )

    def _set_brightness_ratio(
        self, image_new: str, image_basis: str, h_chamber=int(ENV.H_CHAMBER)
    ):
        # get the average chamber brightness
        target_mean = np.mean(
            image_new[self.Y : self.Y + h_chamber, self.X : self.X + self.W]
        )
        basis_mean = np.mean(
            image_basis[
                int(ENV.Y) : int(ENV.Y) + int(ENV.H_CHAMBER),
                int(ENV.X) : int(ENV.X) + int(ENV.W),
            ]
        )
        self.brightness_ratio = basis_mean / target_mean

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

                crop_frame = frame[
                    self.Y : self.Y + self.H, self.X : self.X + self.W, :
                ]
                imageGREY = crop_frame.mean(axis=2)
                image_norm = imageGREY * self.brightness_ratio
                slices.append(image_norm.mean(axis=1))

                out.write(crop_frame)
            else:
                break

        cap.release()
        out.release()

        return slices

    def _stack_and_save(self, slices: List[np.array]) -> str:
        def _grouped_avg(myArray, N=5):
            result = np.cumsum(myArray, 0)[N - 1 :: N] / float(N)
            result[1:] = result[1:] - result[:-1]
            return result

        sliced = np.stack(slices, axis=0)
        sliced = _grouped_avg(sliced)
        np.savetxt(f"{self.out_folder}{os.sep}{self.filename}", sliced, delimiter=",")
        return f"{self.out_folder}{os.sep}{self.filename}"
