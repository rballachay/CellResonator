import click
import cv2

from src.extra.reset_coords import BoundingBoxWidget, change_basis, reset_env_coords


@click.command()
@click.option(
    "-b",
    "basis_image",
    prompt=False,
    help="image to use to reset environment variables",
)
def main(basis_image):
    bbx_wid = BoundingBoxWidget(basis_image)
    while True:
        cv2.imshow("image", bbx_wid.show_image())
        key = cv2.waitKey(1)

        if key == ord("q"):
            cv2.destroyAllWindows()
            reset_env_coords(*bbx_wid.coords())
            change_basis(basis_image)
            exit(1)


if __name__ == "__main__":
    main()
