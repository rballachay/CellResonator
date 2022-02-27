import os

from src.run.pipeline import total_video_splitter


def test_total_video_splitter(cleaning, load_result_data):
    json_path = f"tests{os.sep}data{os.sep}sample_output{os.sep}result_total.json"
    data_dict = load_result_data(json_path, _key="total")
    data_dict["video"] = data_dict["video"].replace("/", os.sep)
    total_video_splitter(data_dict)
    cleaning(f"tests{os.sep}data{os.sep}sample_output")
    return data_dict
