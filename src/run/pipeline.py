import os

from moviepy.editor import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from src.config import ENV
from src.core.histogram_pipeline import HistogramPipeline
from src.core.resonator_pipeline import ResonatorPipeline
from src.extra.tools import check_dir_make
from src.run.process import process_config


def pipeline(
    inlet: str,
    basis_image: str = ENV.BASIS_IMAGE,
    dims: dict = {"X": int(ENV.X), "Y": int(ENV.Y), "W": int(ENV.W), "H": int(ENV.H)},
    plot_name: str = ENV.HIST_PLOT,
    filename: str = ENV.SLICED_FILENAME,
):
    """Run the main pipeline for image processing, including video splitting,
    and actual video pipeline, which includes extracting brightness data from the
    video and plotting data alongside cell counts
    """

    # process config, aka get data dictionary with video and cell counts
    data_items = process_config(inlet)

    # iterate over each item in data items and run pipeline
    for data_type in data_items:

        # for total video, need to first split
        # videos, then run each individually
        if data_type == "total":
            total_video_pipeline(
                inlet,
                data_items,
                basis_image,
                dims,
                plot_name,
                filename,
            )
        else:
            # standard pipeline to run
            _run_pipeline(
                data_items[data_type],
                data_type,
                inlet,
                basis_image,
                dims,
                plot_name,
                filename,
            )


def _run_pipeline(
    data_dict: dict,
    data_type: str,
    inlet: str,
    basis_image: str = ENV.BASIS_IMAGE,
    dims: dict = {"X": int(ENV.X), "Y": int(ENV.Y), "W": int(ENV.W), "H": int(ENV.H)},
    plot_name: str = ENV.HIST_PLOT,
    filename: str = ENV.SLICED_FILENAME,
    xlsxname: str = ENV.RESULTS_DATA,
    cropped_vid: str = ENV.CROPPED_FILENAME,
):

    rsp = ResonatorPipeline(
        data_dict["video"],
        basis_image=basis_image,
        dims=dims,
        filename=f"{data_type}_{filename}",
    )
    path = rsp.run(f"{data_type}_{cropped_vid}")

    htp = HistogramPipeline(
        path,
        data_dict["data"][data_type],
        xlsxname=f"{data_type}_{xlsxname}",
        fps=rsp.fps,
    )
    htp.plot(
        title=f"Histogram for {data_type.capitalize()}",
        save=True,
        filename=f"{data_type}_{plot_name}",
    )


def total_video_pipeline(
    inlet: str,
    data_dict: dict,
    basis_image: str = ENV.BASIS_IMAGE,
    dims: dict = {"X": int(ENV.X), "Y": int(ENV.Y), "W": int(ENV.W), "H": int(ENV.H)},
    plot_name: str = ENV.HIST_PLOT,
    filename: str = ENV.SLICED_FILENAME,
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
            _data_dict_tmp, title, inlet, basis_image, dims, plot_name, filename
        )


def total_video_splitter(data_dict):
    target_dat = _split_data(data_dict["total"])
    return {dat[0]: _split_video(data_dict["video"], dat) for dat in target_dat}


def _split_data(data_dict: dict) -> tuple:
    """HistogramPipeline is only set up to do a single phase - be that
    concentration or washing. In order to run a "total video" need to
    split the sliced array into two parts - one for concentration and
    one for washing.
    """

    # make dictionary out of dataframe ref_data which
    # includes important info about start & stop of vid
    ref_dat = data_dict["data"]["reference"]["data"]
    ref_dict = dict(zip(ref_dat["index"], ref_dat.value))

    return (
        ("concentration", (0, ref_dict["End of concentration"])),
        (
            "washing",
            (
                ref_dict["Start of washing"],
                VideoFileClip(data_dict["video"]).duration,
            ),
        ),
    )


def _split_video(vid_path: str, rng_dat: tuple) -> str:
    """Split video according to data provided in
    rng_dat, saving each in the input folder.
    """
    vid_i = os.sep.join(vid_path.split(os.sep)[:-1])
    vid_n = vid_path.split(os.sep)[-1]
    targetname = f"{vid_i}{os.sep}split_vids{os.sep}{rng_dat[0]}_{vid_n}"
    check_dir_make(f"{vid_i}{os.sep}split_vids")
    ffmpeg_extract_subclip(
        vid_path,
        rng_dat[1][0],
        rng_dat[1][1],
        targetname=targetname,
    )
    return targetname
