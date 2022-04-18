from src.config import ENV
from src.core.histogram_pipeline import HistogramPipeline
from src.core.resonator_pipeline import ResonatorPipeline
from src.run.process import process_config
from src.run.splitting import total_video_splitter
from src.run.utils import check_results_folder, get_background


def pipeline(
    inlet: str,
    basis_image: str = ENV.BASIS_IMAGE,
    height: int = int(ENV.H),
    plot_name: str = ENV.HIST_PLOT,
    filename: str = ENV.SLICED_FILENAME,
):
    """Run the main pipeline for image processing, including video splitting,
    and actual video pipeline, which includes extracting brightness data from the
    video and plotting data alongside cell counts
    """

    # process config, aka get data dictionary with video and cell counts
    data_items, wash_start = process_config(inlet)

    # check if results folder exists. if it does, rename to result_n
    check_results_folder(inlet)

    # iterate over each item in data items and run pipeline
    # is sorted so that concentration will always come first
    for data_type in sorted(data_items):

        # for total video, need to first split
        # videos, then run each individually
        if data_type == "total":
            total_video_pipeline(
                data_items,
                basis_image,
                height,
                plot_name,
                filename,
                wash_start=wash_start,
            )
        else:
            # standard pipeline to run
            _run_pipeline(
                data_items[data_type],
                data_type,
                basis_image,
                height,
                plot_name,
                filename,
                wash_start=wash_start,
            )


def total_video_pipeline(
    data_dict: dict,
    basis_image: str = ENV.BASIS_IMAGE,
    height: int = (ENV.H),
    plot_name: str = ENV.HIST_PLOT,
    filename: str = ENV.SLICED_FILENAME,
    wash_start: float = 0.0,
):
    """In the case that a video of the total workflow is provided, then
    the data needs to be separated into concentration and washing so
    that it is processed in the same manner as individual videos.
    """

    # split video into parts and save
    targets = total_video_splitter(data_dict["total"])

    # create dictionaries in form of concentration/washing
    # then run regular pipeline
    for title in ("concentration", "washing"):
        _data_dict_tmp = {}
        _data_dict_tmp["video"] = targets[title]
        _data_dict_tmp["data"] = data_dict["total"]["data"]

        _run_pipeline(
            _data_dict_tmp,
            title,
            basis_image,
            height,
            plot_name,
            filename,
            wash_start=wash_start,
        )


def _run_pipeline(
    data_dict: dict,
    data_type: str,
    basis_image: str = ENV.BASIS_IMAGE,
    height: int = int(ENV.H),
    plot_name: str = ENV.HIST_PLOT,
    filename: str = ENV.SLICED_FILENAME,
    xlsxname: str = ENV.RESULTS_DATA,
    cropped_vid: str = ENV.CROPPED_FILENAME,
    wash_start: float = 0.0,
):
    """The main video processing pipeline for all types. Runs
    resonator pipeline, which produces csv results, then gets
    background and produces histogram/csv results.
    """

    # Run video processing, produce csv results
    rsp = ResonatorPipeline(
        data_dict["video"],
        basis_image=basis_image,
        height=height,
        filename=f"{data_type}_{filename}",
    )
    path = rsp.run(f"{data_type}_{cropped_vid}")

    # Get background intensity from csv file
    _background = get_background(path)

    # Plot histogram + save xlsx results
    htp = HistogramPipeline(
        path,
        data_dict["data"][data_type],
        xlsxname=f"{data_type}_{xlsxname}",
        s_per_frame=1 / rsp.fps,
        vid_start=wash_start if data_type == "washing" else 0.0,
        background=_background,
    )
    htp.plot(
        title=f"Histogram for {data_type.capitalize()}",
        save=True,
        filename=f"{data_type}_{plot_name}",
    )
