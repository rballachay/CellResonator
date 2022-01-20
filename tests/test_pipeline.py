import os
from src.config import ENV
from src.pipeline import pipeline

FOLDER = "tests/data/test_folder_conc"
VID_PATH = f"{FOLDER}/vid_Washing.mp4"
TEST_BASIS = f"{FOLDER}/vid_Concentration.mp4"

FILES_MADE = (
    f"concentration_{ENV.SLICED_FILENAME}",
    ENV.CROPPED_FILENAME,
    ENV.MATCHES_FILENAME,
    f"concentration_{ENV.HIST_PLOT}"
)

def _cleaning():
    for file in FILES_MADE:
        path = f"{FOLDER}/{file}"
        if os.path.exists(path):
            os.remove(path)

def test_pipeline():
    _cleaning()

    data_dict = pipeline(
        FOLDER,
        "1",
        basis_video=TEST_BASIS,
        dims={"X": 50, "Y": 50, "W": 50, "H": 50},
    )

    _cleaning()

