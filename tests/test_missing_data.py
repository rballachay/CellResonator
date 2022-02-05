import json
import os

import pandas as pd
from pandas._testing import assert_frame_equal
from src.pipeline import pipeline
from src.process import process_config

FOLDER = f"tests{os.sep}data{os.sep}sample_missing"


VID_PATH = f"{FOLDER}{os.sep}vid_Washing.mp4"


def make_process_config_conc(cleaning, file=FOLDER):

    cleaning(file)
    data_items = process_config(file, 1)

    conc_wash = data_items["concentration"]["data"]
    for key_1 in conc_wash:
        conc_wash = data_items["concentration"]["data"][key_1]
        for key_2 in conc_wash:
            conc_wash[key_2] = conc_wash[key_2].to_dict()

    with open(f"{file}{os.sep}result.json", "w") as fp:
        json.dump(data_items, fp)

    cleaning(file)


def test_process_config_conc(cleaning, file=FOLDER):
    cleaning(file)
    data_items = process_config(file, 1)
    with open(f"{file}{os.sep}result.json", "r") as fp:
        data_items_basis = json.load(fp)

    for key_1 in data_items["concentration"]["data"]:
        for key_2 in data_items["concentration"]["data"][key_1]:
            df_basis = pd.DataFrame.from_dict(
                data_items_basis["concentration"]["data"][key_1][key_2]
            )
            df_basis.index = df_basis.index.astype("int64")
            df_test = data_items["concentration"]["data"][key_1][key_2]
            assert_frame_equal(df_test, df_basis)

    cleaning(file)


def test_pipeline(cleaning):
    cleaning(FOLDER)

    pipeline(
        FOLDER,
        "1",
        basis_image="tests/data/test_basis.jpg",
        dims={"X": 50, "Y": 50, "W": 50, "H": 50},
    )

    cleaning(FOLDER)
