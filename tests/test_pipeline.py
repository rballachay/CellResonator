import os
from src.config import ENV
from src.pipeline import pipeline

FOLDER = "tests/data/test_folder_conc"

FOLDER_TOTAL = "tests/data/test_folder_1file"

VID_PATH = f"{FOLDER}/vid_Washing.mp4"
TEST_BASIS = f"{FOLDER}/vid_Concentration.mp4"

FILES_MADE = (
    f"concentration_{ENV.SLICED_FILENAME}",
    ENV.CROPPED_FILENAME,
    ENV.MATCHES_FILENAME,
    f"concentration_{ENV.HIST_PLOT}",
    "washing_vid.mp4",
    "concentration_vid.mp4",
)


def _cleaning(folder):
    for file in FILES_MADE:
        path = f"{folder}/{file}"
        if os.path.exists(path):
            os.remove(path)


def test_pipeline():
    _cleaning(FOLDER)

    pipeline(
        FOLDER,
        "1",
        basis_video=TEST_BASIS,
        dims={"X": 50, "Y": 50, "W": 50, "H": 50},
    )

    _cleaning(FOLDER)


def test_total_video_pipeline():
    _cleaning(FOLDER_TOTAL)

    pipeline(
        FOLDER_TOTAL,
        "1",
        basis_video=TEST_BASIS,
        dims={"X": 50, "Y": 50, "W": 50, "H": 50},
    )

    _cleaning(FOLDER_TOTAL)
