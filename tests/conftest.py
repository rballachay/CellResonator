import json
import os
import shutil

import pandas as pd
import pytest
from src.config import ENV


@pytest.fixture(scope="module")
def load_result_data():
    def _load(
        path=f"tests{os.sep}data{os.sep}sample_output{os.sep}result.json",
        _key="concentration",
    ):
        with open(path, "r") as fp:
            data_dict = json.load(fp)

        for key_1 in data_dict[_key]["data"]:
            for key_2 in data_dict[_key]["data"][key_1]:
                data_dict[_key]["data"][key_1][key_2] = pd.DataFrame.from_dict(
                    data_dict[_key]["data"][key_1][key_2]
                )
        if _key == "concentration":
            return data_dict[_key]["data"]["concentration"]
        else:
            return data_dict[_key]

    return _load


@pytest.fixture(scope="module")
def cleaning():
    def _cleaning(folder):
        path = f"{folder}{os.sep}{_get_files_made()}"
        if os.path.isdir(path):
            shutil.rmtree(f"{folder}{os.sep}{_get_files_made()}")

    return _cleaning


def _get_files_made():
    return "results"
