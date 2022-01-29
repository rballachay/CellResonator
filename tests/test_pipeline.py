import os
from src.config import ENV
from src.pipeline import pipeline

FOLDER = "tests/data/test_folder_conc"

FOLDER_TOTAL = "tests/data/test_folder_1file"

VID_PATH = f"{FOLDER}/vid_Washing.mp4"


def test_pipeline(cleaning):
    cleaning(FOLDER)
    pipeline(
        FOLDER,
        "1",
        dims={"X": 50, "Y": 50, "W": 50, "H": 50},
    )
    cleaning(FOLDER)


def test_total_video_pipeline(cleaning):
    cleaning(FOLDER_TOTAL)
    pipeline(
        FOLDER_TOTAL,
        "1",
        dims={"X": 50, "Y": 50, "W": 50, "H": 50},
    )
    cleaning(FOLDER_TOTAL)
