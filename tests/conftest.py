import pytest
import json
import pandas as pd

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
