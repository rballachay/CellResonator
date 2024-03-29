import click
import cv2

from src.extra.reset_coords import (
    BoundingBoxWidget,
    check_video,
    get_basis_image,
    reset_basis,
)


@click.command()
@click.option(
    "-i",
    "input_video",
    prompt=False,
    help="video to use to reset environment variables, or folder with video",
)
def main(input_video):
    # check if video or path to folder with video
    video = check_video(input_video)
    # extract basis image from video
    original_image = get_basis_image(video)

    bbx_wid = BoundingBoxWidget(original_image)
    while True:
        cv2.imshow("image", bbx_wid.show_image())
        key = cv2.waitKey(1)

        if key == ord("q"):
            cv2.destroyAllWindows()
            reset_basis(bbx_wid.coords(), bbx_wid.original_image)
            exit(1)


if __name__ == "__main__":
    main()
