import click
from src.api.live import analyze_live_video


@click.command()
@click.option(
    "-i",
    "input_source",
    prompt=False,
    default=1,
    help="Source for video feed: 0 for webcam, 1 for usb",
)
@click.option(
    "-o",
    "output_file",
    prompt=False,
    default="MonthDate_Year.mp4",
    help="Source for video feed: 0 for webcam, 1 for usb",
)
@click.option(
    "-c/--nocal",
    "calibrate",
    default=True,
    help="Choose to calibrate online or not",
)
@click.option(
    "-b",
    "buffer",
    prompt=False,
    default=1,
    help="Number of frames to average prior to reporting cell loss",
)
def main(input_source, output_file, calibrate, buffer):
    analyze_live_video(input_source, output_file, calibrate, buffer)


if __name__ == "__main__":
    main()
