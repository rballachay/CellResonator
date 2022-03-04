import os

import cv2
import numpy as np


class BoundingBoxWidget(object):
    """Widget which allows for selection of ROI. ROI select
    records coordinates, and re-writes the environment variables
    that are used to calculate homography and transform the image
    to the reference image
    """

    def __init__(self, video: str):
        # check if video or path to folder with video
        video = self._check_video(video)

        # extract basis image from video
        self.original_image = self._get_basis_image(video)

        # make clone which will be written to
        self.clone = self.original_image.copy()

        cv2.namedWindow("image")
        cv2.setMouseCallback("image", self.extract_coordinates)

        # Bounding box reference points
        self.image_coordinates = []

        # print info about app to console
        self._info()

    def extract_coordinates(self, event, x, y, flags, parameters):
        # Record starting (x,y) coordinates on left mouse button click
        if event == cv2.EVENT_LBUTTONDOWN:
            self.image_coordinates = [(x, y)]

        # Record ending (x,y) coordintes on left mouse button release
        elif event == cv2.EVENT_LBUTTONUP:
            self.image_coordinates.append((x, y))
            print(
                "top left: {}, bottom right: {}".format(
                    self.image_coordinates[0], self.image_coordinates[1]
                )
            )
            print(
                "x,y,w,h : ({}, {}, {}, {})".format(
                    self.image_coordinates[0][0],
                    self.image_coordinates[0][1],
                    self.image_coordinates[1][0] - self.image_coordinates[0][0],
                    self.image_coordinates[1][1] - self.image_coordinates[0][1],
                )
            )

            # Draw rectangle
            cv2.rectangle(
                self.clone,
                self.image_coordinates[0],
                self.image_coordinates[1],
                (36, 255, 12),
                2,
            )
            cv2.imshow("image", self.clone)

        # Clear drawing boxes on right mouse button click
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.clone = self.original_image.copy()

    def show_image(self):
        return self.clone

    def coords(self):
        """After positioning correct ROI, report ROI
        coordinates back so that .env can be reset.
        """
        x = self.image_coordinates[0][0]
        y = self.image_coordinates[0][1]
        w = self.image_coordinates[1][0] - self.image_coordinates[0][0]
        h = self.image_coordinates[1][1] - self.image_coordinates[0][1]
        return x, y, w, h

    def _info(self):
        print("Please draw the ROI for the resonator")
        print(
            "Once the ROI is correct, press q on the keyboard and the .env file will be changed"
        )
        print("In order to clear all ROI's on the image, right click on the mouse")

    def _check_video(self, video):
        """Can input either a path to a video or path to
        folder with video. If folder, first video is selected.
        """
        if video.endswith(".mp4"):
            return video
        elif os.path.isdir(video):
            for file in os.listdir(video):
                if file.endswith(".mp4"):
                    return os.path.join(video, file)
            raise Exception("There are no videos in this folder")
        else:
            raise Exception("Uknown file extention, please use folder or video")

    def _get_basis_image(self, basis_video) -> np.array:
        """Input is video, so need utility to grab a reference
        frame which can be used to replace the basis.
        """
        # Grab the first frame from our reference photo
        vidcap = cv2.VideoCapture(basis_video)
        # take 100th frame to avoid issues with reading
        # first frame
        for _ in range(100):
            success, vid = vidcap.read()
        if not success:
            raise Exception(f"Error reading 10th frame from path {basis_video}")
        return vid


def reset_basis(coords, new_image):
    """Reset the environment variables and
    change the basis image to be used for
    registration in the pipeline.
    """
    _reset_env_coords(*coords)
    _change_basis(new_image)


def _reset_env_coords(x, y, w, h):
    """Open up the environment variable file
    and reset the coordinates after selecting
    with interactive class.
    """
    with open(".env", "r") as file:
        data = file.readlines()
    for i, line in enumerate(data):
        if "X = " in line:
            data[i] = f"X = {x}\n"
        elif "Y = " in line:
            data[i] = f"Y = {y}\n"
        elif "W = " in line:
            data[i] = f"W = {w}\n"
        elif "H = " in line:
            data[i] = f"H = {h}\n"

    # and write everything back
    with open(".env", "w") as file:
        file.writelines(data)


def _change_basis(new_image):
    """Reset the basis image based on the new
    coordinates selected using the interactive
    class.
    """
    num = 0
    while True:
        new = f"data/basis{num}.jpg"
        if os.path.exists(new):
            num += 1
            continue
        else:
            os.rename("data/basis.jpg", f"data/basis{num}.jpg")
            break
    cv2.imwrite("data/basis.jpg", new_image)
