import os
from src.histogram_pipeline import HistogramPipeline
import json
import pandas as pd
from src.config import ENV

def _load_data(path=f"tests/data/sample_output/result.json"):
    with open(path, "r") as fp:
        data_dict = json.load(fp)

    for key_1 in data_dict["concentration"]["data"]:
        for key_2 in data_dict["concentration"]["data"][key_1]:
            data_dict["concentration"]["data"][key_1][key_2] = pd.DataFrame.from_dict(
                data_dict["concentration"]["data"][key_1][key_2]
            )

    return data_dict["concentration"]["data"]["concentration"]


def test_histogram_pipeline():
    data_dict = _load_data()
    path_sliced = "tests/data/sample_output/sliced_result.csv"
    htp = HistogramPipeline(path_sliced,data_dict)

    htp.plot(
            title=f"Histogram for Concentration",
            save=True,
            filename=f"concentration_{ENV.HIST_PLOT}",
    )

    os.remove(f"tests/data/sample_output/concentration_{ENV.HIST_PLOT}")



def test_total_video_splitter():
    data_dict = _load_data("tests/data/sample_output/result_total.json")


