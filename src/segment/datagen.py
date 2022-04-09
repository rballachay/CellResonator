import glob
import os

import click
import cv2
import numpy as np
from src.extra.reset_coords import BoundingBoxWidget, get_basis_image


@click.command()
@click.option(
    "-i",
    "path_in",
    prompt=False,
    help="Path to folder where videos are located",
)
@click.option(
    "-o",
    "path_out",
    prompt=False,
    help="Path to folder where masks/images are to be stored",
)
def main(path_in: str, path_out: str, take_every=1000):
    mask_path = f"{path_out}/masks"
    img_path = f"{path_out}/images"
    os.makedirs(img_path, exist_ok=1)
    os.makedirs(mask_path, exist_ok=1)
    for video in glob.glob(f"{path_in}/*.mp4"):
        vid_name = video.split(os.sep)[-1][:-4]
        original_image = get_basis_image(video)

        bbx_wid = BoundingBoxWidget(original_image)
        while True:
            cv2.imshow("image", bbx_wid.show_image())
            key = cv2.waitKey(1)

            if key == ord("q"):
                cv2.destroyAllWindows()
                x, y, w, h = bbx_wid.coords()
                break

        # Check to see if the crop region returns nothing
        cap = cv2.VideoCapture(video)

        # get the 5th frame to avoid problems with the first
        i = 0
        while cap.isOpened():
            success, image = cap.read()
            i += 1
            if success:
                if i % take_every == 0:
                    mask = np.zeros_like(image)
                    mask[y : y + h, x : x + w] = 255
                    cv2.imwrite(f"{img_path}/{vid_name}_f{i}.jpg", image)
                    cv2.imwrite(f"{mask_path}/{vid_name}_f{i}.jpg", mask)
                if i == 10000:
                    break
            else:
                break
        cap.release()


if __name__ == "__main__":
    main()
