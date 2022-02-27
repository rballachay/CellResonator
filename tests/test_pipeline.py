import os

from src.config import ENV
from src.run.pipeline import pipeline

FOLDER = f"tests{os.sep}data{os.sep}test_folder_conc"

FOLDER_TOTAL = f"tests{os.sep}data{os.sep}test_folder_1file"

VID_PATH = f"{FOLDER}{os.sep}vid_Washing.mp4"


def test_pipeline(cleaning):
    cleaning(FOLDER)
    pipeline(
        FOLDER,
        basis_image="tests/data/test_basis.jpg",
        dims={"X": 10, "Y": 10, "W": 100, "H": 100},
    )
    cleaning(FOLDER)


def test_total_video_pipeline(cleaning):
    cleaning(FOLDER_TOTAL)
    pipeline(
        FOLDER_TOTAL,
        basis_image="tests/data/test_basis.jpg",
        dims={"X": 10, "Y": 10, "W": 100, "H": 100},
    )
    cleaning(FOLDER_TOTAL)
