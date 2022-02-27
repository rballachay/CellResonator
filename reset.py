import click
import cv2

from src.extra.reset_coords import BoundingBoxWidget, reset_basis


@click.command()
@click.option(
    "-b",
    "basis_video",
    prompt=False,
    help="video to use to reset environment variables, or folder with video",
)
def main(basis_video):
    bbx_wid = BoundingBoxWidget(basis_video)
    while True:
        cv2.imshow("image", bbx_wid.show_image())
        key = cv2.waitKey(1)

        if key == ord("q"):
            cv2.destroyAllWindows()
            reset_basis(bbx_wid.coords(), bbx_wid.original_image)
            exit(1)


if __name__ == "__main__":
    main()
