import os
from src.resonator_pipeline import ResonatorPipeline
from src.config import ENV

FOLDER = "tests/data/test_folder_2files"
VID_PATH = f"{FOLDER}/vid_Washing.mp4"


def test_resonator_pipeline(cleaning):
    cleaning(FOLDER)
    rep = ResonatorPipeline(VID_PATH)
    rep.run()

    cleaning(FOLDER)
