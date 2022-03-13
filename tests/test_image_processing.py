import os

from src.config import ENV
from src.core.resonator_pipeline import ResonatorPipeline

FOLDER = f"tests{os.sep}data{os.sep}test_folder_2files"
VID_PATH = f"{FOLDER}{os.sep}vid_Washing.mp4"


def test_resonator_pipeline(cleaning):
    cleaning(FOLDER)
    rep = ResonatorPipeline(
        VID_PATH,
        dims={"X": 5, "Y": 5, "W": 50, "H": 50},
        basis_image="tests/data/test_basis.jpg",
    )
    rep.run()
    cleaning(FOLDER)
