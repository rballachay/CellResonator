import os
import warnings

from src.config import ENV
from src.core.histogram_pipeline import HistogramPipeline
from src.core.resonator_pipeline import ResonatorPipeline
from src.run.utils import get_video


def workflow1(
    inlet: str,
    basis_image: str = ENV.BASIS_IMAGE,
    dims: dict = {"X": int(ENV.X), "Y": int(ENV.Y), "W": int(ENV.W), "H": int(ENV.H)},
    filename: str = ENV.SLICED_FILENAME,
    xlsxname: str = ENV.RESULTS_DATA,
    cropped_vid: str = ENV.CROPPED_FILENAME,
):
    """Workflow for running on single video in a folder, and outputting the
    results as an xlsx file to get brightness.
    """

    vids = get_video(inlet)
    warnings.warn(
        f"There are {len(vids)} videos in the inlet folder. Note that these are all going to be processed!\n"
    )

    for vid in vids:
        prefix = f"workflow1_{vid.split(os.sep)[-1][:-4]}"
        rsp = ResonatorPipeline(
            vid,
            basis_image=basis_image,
            dims=dims,
            filename=f"{prefix}_{filename}",
        )
        path = rsp.run(f"{prefix}_{cropped_vid}")

        HistogramPipeline(
            path,
            xlsxname=f"{prefix}_{xlsxname}",
        )
