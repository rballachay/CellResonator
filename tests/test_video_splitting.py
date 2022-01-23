from src.pipeline import total_video_splitter


def test_total_video_splitter(load_result_data):
    json_path = "tests/data/sample_output/result_total.json"
    data_dict = load_result_data(json_path, _key="total")
    total_video_splitter(data_dict)
    return data_dict
