import os
from src.resonator_pipeline import ResonatorPipeline
from src.config import ENV

FOLDER = f"tests{os.sep}data{os.sep}test_folder_2files"
VID_PATH = f"{FOLDER}{os.sep}vid_Washing.mp4"


def test_resonator_pipeline(cleaning):
    cleaning(FOLDER)
    rep = ResonatorPipeline(VID_PATH)
    rep.run()

    cleaning(FOLDER)
