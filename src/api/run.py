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
def main(input_source):
    analyze_live_video(input_source)


if __name__ == "__main__":
    main()
