import pytest
import json
import pandas as pd
import os
from src.config import ENV


@pytest.fixture(scope="module")
def load_result_data():
    def _load(path=f"tests/data/sample_output/result.json", _key="concentration"):
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
        for file in _get_files_made():
            path = f"{folder}/{file}"
            if os.path.exists(path):
                os.remove(path)

    return _cleaning


def _get_files_made():
    return (
        f"concentration_{ENV.SLICED_FILENAME}",
        f"washing_{ENV.SLICED_FILENAME}",
        ENV.CROPPED_FILENAME,
        ENV.MATCHES_FILENAME,
        f"concentration_{ENV.HIST_PLOT}",
        f"washing_{ENV.HIST_PLOT}",
        "washing_vid.mp4",
        "concentration_vid.mp4",
        "washing_vid_small.mp4",
        "concentration_vid_small.mp4",
        "vid_Washing_small.mp4",
        "vid_Concentration_small.mp4",
        f"concentration_{ENV.XLSX}",
        f"washing_{ENV.XLSX}",
    )
