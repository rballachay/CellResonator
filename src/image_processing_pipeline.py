#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 13 12:08:37 2021

@author: RileyBallachay
"""
import datetime
import os

import cv2
import numpy as np

from .config import ENV


class ResonatorPipeline:
    def __init__(
        self,
        video_path: str,
        basis_video: str = ENV.BASIS_VIDEO,
        out_folder: str = None,
        dims: dict = {
            "X": int(ENV.X),
            "Y": int(ENV.Y),
            "W": int(ENV.W),
            "H": int(ENV.H),
        },
        filename: str = ENV.SLICED_FILENAME,
    ):
        self.video_path = video_path
        if out_folder is None:
            out_folder = os.sep.join(video_path.split(os.sep)[:-1])
        self.out_folder = self.create_outlet(out_folder)
        self.basis = basis_video
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
        vid_paths = {"video": self.video_path, "basis video": self.basis}
        vids = {}
        for vid_name in vid_paths:
            vid_path = vid_paths[vid_name]
            vidcap = cv2.VideoCapture(vid_path)
            success, vid = vidcap.read()
            if success:
                vids[vid_name] = vid
            else:
                raise Exception(f"Error reading {vid_name} from path {vid_path}")

        self.get_homography(vids["video"], vids["basis video"])

    def get_homography(self, image_new, image_basis):
        MAX_FEATURES = 500
        GOOD_MATCH_PERCENT = 0.99

        im1 = image_new
        im2 = image_basis
        # Convert images to grayscale
        im1Gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
        im2Gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

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
        h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)

        # Use homography
        self.height, self.width, channels = im2.shape
        im1Reg = cv2.warpPerspective(im1, h, (self.width, self.height))

        self.homography = h
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
        # Initialize frame counter
        cnt = 0
        cap = cv2.VideoCapture(self.video_path)
        # Some characteristics from the original video
        w_frame, h_frame = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(
            cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )
        fps, frames = cap.get(cv2.CAP_PROP_FPS), cap.get(cv2.CAP_PROP_FRAME_COUNT)

        time_per_frame = 1 / fps

        # output
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(
            f"{self.out_folder}{os.sep}{ENV.CROPPED_FILENAME}",
            fourcc,
            fps,
            (self.W, self.H),
        )

        time = 0
        slices = []

        # Now we start
        while cap.isOpened():
            ret, frame = cap.read()

            cnt += 1  # Counting frames

            # Avoid problems when video finish
            if ret:
                time = time + time_per_frame
                printtime = str(datetime.timedelta(seconds=time))

                # Croping the frame
                # frame = self._hist_normalization(frame)
                # frame = cv2.subtract(frame,self.back_to_sub)
                frame = cv2.warpPerspective(
                    frame, self.homography, (self.width, self.height)
                )
                crop_frame = frame[self.Y : self.Y + self.H, self.X : self.X + self.W]

                # Percentage
                xx = cnt * 100 / frames
                print((xx), "%")

                imageGREY = crop_frame.mean(axis=2)
                imageGREY = imageGREY.mean(axis=1)
                slices.append(imageGREY)

                """
                font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
                crop_frame = cv2.putText(crop_frame, printtime,
                                    (10, 50),
                                    font, 1,
                                    (255, 255, 255), 
                                    2, cv2.LINE_8)
                """

                # I see the answer now. Here you save all the video
                out.write(crop_frame)
            else:
                break

        sliced = np.stack(slices, axis=0)
        np.savetxt(f"{self.out_folder}{os.sep}{self.filename}", sliced, delimiter=",")

        cap.release()
        out.release()
        return f"{self.out_folder}{os.sep}{self.filename}"

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
