import os

from src.config import ENV
from src.core.resonator_pipeline import ResonatorPipeline

FOLDER = f"tests{os.sep}data{os.sep}test_folder_2files"
VID_PATH = f"{FOLDER}{os.sep}vid_Washing.mp4"


def test_resonator_pipeline(cleaning):
    cleaning(FOLDER)
    rep = ResonatorPipeline(VID_PATH, basis_image="tests/data/test_basis.jpg")
    rep.run()
    cleaning(FOLDER)
