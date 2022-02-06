import json
import os

import pandas as pd
from pandas._testing import assert_frame_equal
from src.process import process_config

TEST_2FILES = f"tests{os.sep}data{os.sep}test_folder_2files"
TEST_1FILE = f"tests{os.sep}data{os.sep}test_folder_1file"
TEST_CONC = f"tests{os.sep}data{os.sep}test_folder_conc"

#######################################################################
# Section for testing 2 files in one folder (concentration + washing) #
#######################################################################


def make_process_config_2files(file=TEST_2FILES):
    data_items = process_config(file, 2)

    for key_1 in data_items:
        for key_2 in data_items[key_1]["data"]:
            for key_3 in data_items[key_1]["data"][key_2]:
                data_items[key_1]["data"][key_2][key_3] = data_items[key_1]["data"][
                    key_2
                ][key_3].to_dict()

    with open(f"{file}{os.sep}result.json", "w") as fp:
        json.dump(data_items, fp)


def test_process_config_2files(cleaning, file=TEST_2FILES):
    cleaning(file)
    data_items = process_config(file, 2)
    with open(f"{file}{os.sep}result.json", "r") as fp:
        data_items_basis = json.load(fp)

    for key_1 in data_items_basis:
        for key_2 in data_items[key_1]["data"]:
            for key_3 in data_items[key_1]["data"][key_2]:
                df_basis = pd.DataFrame.from_dict(
                    data_items_basis[key_1]["data"][key_2][key_3]
                )
                df_basis.index = df_basis.index.astype("int64")
                df_test = data_items[key_1]["data"][key_2][key_3]
                assert_frame_equal(df_test, df_basis)

    cleaning(file)


######################################################################
# Section for testing 1 file in one folder (concentration + washing) #
######################################################################


def make_process_config_1files(file=TEST_1FILE):
    data_items = process_config(file, 1)

    conc_wash = data_items["total"]["data"]
    for key_1 in conc_wash:
        conc_wash = data_items["total"]["data"][key_1]
        for key_2 in conc_wash:
            conc_wash[key_2] = conc_wash[key_2].to_dict()

    with open(f"{file}{os.sep}result.json", "w") as fp:
        json.dump(data_items, fp)


def test_process_config_1files(cleaning, file=TEST_1FILE):
    cleaning(file)

    data_items = process_config(file, 1)
    with open(f"{file}{os.sep}result.json", "r") as fp:
        data_items_basis = json.load(fp)

    for key_1 in data_items["total"]["data"]:
        for key_2 in data_items["total"]["data"][key_1]:
            df_basis = pd.DataFrame.from_dict(
                data_items_basis["total"]["data"][key_1][key_2]
            )
            df_basis.index = df_basis.index.astype("int64")
            df_test = data_items["total"]["data"][key_1][key_2]
            assert_frame_equal(df_test, df_basis)

    cleaning(file)


#################################################################
# Section for testing 1 conc file in one folder (concentration) #
#################################################################


def make_process_config_conc(file=TEST_CONC):
    data_items = process_config(file, 1)

    conc_wash = data_items["concentration"]["data"]
    for key_1 in conc_wash:
        conc_wash = data_items["concentration"]["data"][key_1]
        for key_2 in conc_wash:
            conc_wash[key_2] = conc_wash[key_2].to_dict()

    with open(f"{file}{os.sep}result.json", "w") as fp:
        json.dump(data_items, fp)


def test_process_config_conc(cleaning, file=TEST_CONC):
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
