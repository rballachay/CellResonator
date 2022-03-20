from pathlib import Path

import click

from src.extra.calibright import calibrate_brightness


@click.command()
@click.option(
    "-i",
    "input_data",
    prompt=False,
    help="folder with data to use for calibration",
    type=click.Path(exists=True)
)
def main(input_data):
    calibrate_brightness(Path(input_data))


if __name__ == "__main__":
    main()
