import os

import pandas as pd

from .config import ENV
from .histogram_pipeline import HistogramPipeline
from .image_processing_pipeline import ResonatorPipeline
from .utils import process_config


def pipeline(
    inlet: str,
    file_num: str,
    basis_video: str = ENV.BASIS_VIDEO,
    dims: dict = {"X": int(ENV.X), "Y": int(ENV.Y), "W": int(ENV.W), "H": int(ENV.H)},
    plot_name: str = ENV.HIST_PLOT,
):
    data_items = process_config(inlet, file_num)

    for data_type in data_items:
        filename = f"{data_type}_{ENV.SLICED_FILENAME}"
        rsp = ResonatorPipeline(
            data_items[data_type]["video"],
            basis_video=basis_video,
            dims={"X": 50, "Y": 50, "W": 50, "H": 50},
            filename=filename,
        )
        rsp.run()

        data_dict = data_items[data_type]["data"][data_type]
        for key in data_dict:
            data_dict[key] = pd.DataFrame.from_dict(data_dict[key])

        htp = HistogramPipeline(f"{inlet}{os.sep}{filename}", data_dict)
        htp.plot(
            title=f"Histogram for {data_type.capitalize()}",
            save=True,
            filename=f"{data_type}_{ENV.HIST_PLOT}",
        )

    return data_dict


def total_video_splitter(path_sliced: str, data_dict: dict):
    """HistogramPipeline is only set up to do a single phase - be that
    concentration or washing. In order to run a "total video" need to
    split the sliced array into two parts - one for concentration and
    one for washing.
    """

    FPS = float(ENV.TIME_PER_FRAME) * float(ENV.SLICE_FREQUENCY)
    
    data_dict["concentration"]