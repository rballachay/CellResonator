import os
from src.histogram_pipeline import HistogramPipeline
from src.config import ENV


def test_histogram_pipeline(load_result_data):
    # call pytest fixture from conftest
    data_dict = load_result_data()

    path_sliced = "tests/data/sample_output/sliced_result.csv"
    htp = HistogramPipeline(path_sliced, data_dict)

    htp.plot(
        title=f"Histogram for Concentration",
        save=True,
        filename=f"concentration_{ENV.HIST_PLOT}",
    )

    os.remove(f"tests/data/sample_output/concentration_{ENV.HIST_PLOT}")

