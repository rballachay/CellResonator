import os
from src.resonator_pipeline import ResonatorPipeline
from src.config import ENV

FOLDER = "tests/data/test_folder_2files"
VID_PATH = f"{FOLDER}/vid_Washing.mp4"
TEST_BASIS = f"{FOLDER}/vid_Concentration.mp4"

FILES_MADE = (ENV.SLICED_FILENAME, ENV.CROPPED_FILENAME, ENV.MATCHES_FILENAME)


def test_resonator_pipeline():

    rep = ResonatorPipeline(
        VID_PATH, basis_video=TEST_BASIS, dims={"X": 50, "Y": 50, "W": 50, "H": 50}
    )
    rep.run()

    for file in FILES_MADE:
        path = f"{FOLDER}/{file}"
        assert os.path.exists(path)
        os.remove(path)
