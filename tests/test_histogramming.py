import os
import shutil

from src.config import ENV
from src.core.histogram_pipeline import HistogramPipeline


def test_histogram_pipeline(load_result_data):
    # call pytest fixture from conftest
    data_dict = load_result_data()

    path_sliced = f"tests{os.sep}data{os.sep}sample_output{os.sep}sliced_result.csv"
    htp = HistogramPipeline(path_sliced, data_dict)

    htp.plot(
        title=f"Histogram for Concentration",
        save=True,
        filename=f"concentration_{ENV.HIST_PLOT}",
    )

    shutil.rmtree(f"tests{os.sep}data{os.sep}sample_output{os.sep}results")
