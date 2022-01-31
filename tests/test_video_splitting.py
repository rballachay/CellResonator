from src.pipeline import total_video_splitter
import os


def test_total_video_splitter(cleaning, load_result_data):
    json_path = f"tests/data{os.sep}sample_output{os.sep}result_total.json"
    data_dict = load_result_data(json_path, _key="total")
    total_video_splitter(data_dict)
    cleaning(f"tests{os.sep}data{os.sep}sample_output")
    return data_dict
