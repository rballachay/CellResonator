#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 13 12:08:37 2021

@author: RileyBallachay
"""
import os

import cv2
import numpy as np

from .config import ENV
from .resize import get_downscaled_video


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
    ):
        # video is unnecessarily big in native format
        self.video_path = get_downscaled_video(video_path)

        if out_folder is None:
            out_folder = os.sep.join(video_path.split(os.sep)[:-1])
        self.out_folder = self.create_outlet(out_folder)
        self.basis = basis_image
        self.X = dims["X"]
        self.Y = dims["Y"]
        self.W = dims["W"]
        self.H = dims["H"]
        self.filename = filename

    def run(self):
        self.prepare_registration()
        sliced = self.pipeline_main()
        return sliced

    def prepare_registration(self):
        # Grab the first frame from our reference photo
        vidcap = cv2.VideoCapture(self.video_path)

        # take 100th frame to avoid issues with reading
        # first frame
        for _ in range(100):
            success, vid = vidcap.read()
        if not success:
            raise Exception(f"Error reading 100th frame from path {self.video_path}")

        self.get_homography(vid, cv2.imread(self.basis))

    def get_homography(self, image_new, image_basis):
        MAX_FEATURES = 500
        GOOD_MATCH_PERCENT = 0.999

        im1 = image_new
        im2 = image_basis

        # Convert images to grayscale
        im1Gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
        im2Gray = cv2.cvtColor(im1, cv2.COLOR_RGB2GRAY)

        # Detect ORB features and compute descriptors.
        orb = cv2.ORB_create(MAX_FEATURES)
        keypoints1, descriptors1 = orb.detectAndCompute(im1Gray, None)
        keypoints2, descriptors2 = orb.detectAndCompute(im2Gray, None)

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
        imMatches = cv2.drawMatches(im1, keypoints1, im2, keypoints2, matches, None)
        cv2.imwrite(f"{self.out_folder}{os.sep}{ENV.MATCHES_FILENAME}", imMatches)

        # Extract location of good matches
        points1 = np.zeros((len(matches), 2), dtype=np.float32)
        points2 = np.zeros((len(matches), 2), dtype=np.float32)

        for i, match in enumerate(matches):
            points1[i, :] = keypoints1[match.queryIdx].pt
            points2[i, :] = keypoints2[match.trainIdx].pt

        # Find homography
        self.homography, _ = cv2.findHomography(points1, points2, cv2.RANSAC)
        return

    def grouped_avg(self, myArray, N=5):
        result = np.cumsum(myArray, 0)[N - 1 :: N] / float(N)
        result[1:] = result[1:] - result[:-1]
        return result

    def create_outlet(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

    def pipeline_main(self):
        cap = cv2.VideoCapture(self.video_path)

        # Some characteristics from the original video
        fps, frames = cap.get(cv2.CAP_PROP_FPS), cap.get(cv2.CAP_PROP_FRAME_COUNT)

        # output
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(
            f"{self.out_folder}{os.sep}{ENV.CROPPED_FILENAME}",
            fourcc,
            fps,
            (self.W, self.H),
        )

        slices = []

        X, Y, W, H = self._warp_coordinates()

        # Now we start
        while cap.isOpened():
            ret, frame = cap.read()

            # Avoid problems when video finish
            if ret:

                crop_frame = frame[Y : Y + H, X : X + W, :]

                imageGREY = crop_frame.mean(axis=2).mean(axis=1)
                slices.append(imageGREY)

                # I see the answer now. Here you save all the video
                out.write(crop_frame)
            else:
                break

        sliced = np.stack(slices, axis=0)
        np.savetxt(f"{self.out_folder}{os.sep}{self.filename}", sliced, delimiter=",")

        cap.release()
        out.release()
        return f"{self.out_folder}{os.sep}{self.filename}"

    def _warp_coordinates(self):
        # this is the start, or the upper left corner of the mask
        start = np.matmul(self.homography, (self.X, self.Y, 0))

        # this is the bottom right corner of the mask
        end = np.matmul(self.homography, (self.X + self.W, self.Y + self.H, 0))
        return (
            int(start[0]),
            int(start[1]),
            int(end[1] - start[1]),
            int(end[0] - start[0]),
        )

    def _hist_normalization(self, img, a=0, b=255):
        c = img.min()
        d = img.max()

        out = img.copy()
        # normalization
        out = (b - a) / (d - c) * (out - c) + a
        out[out < a] = a
        out[out > b] = b

        out = out.astype(np.uint8)
        return out
