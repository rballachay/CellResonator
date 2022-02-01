import os

import pandas as pd
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip

from src.config import ENV
from src.histogram_pipeline import HistogramPipeline
from src.resonator_pipeline import ResonatorPipeline
from src.process import process_config


def pipeline(
    inlet: str,
    file_num: str,
    basis_image: str = ENV.BASIS_IMAGE,
    dims: dict = {"X": int(ENV.X), "Y": int(ENV.Y), "W": int(ENV.W), "H": int(ENV.H)},
    plot_name: str = ENV.HIST_PLOT,
    filename: str = ENV.SLICED_FILENAME,
):
    data_items = process_config(inlet, file_num)

    for data_type in data_items:
        if data_type == "total":
            total_video_pipeline(
                inlet, data_items, basis_image, dims, plot_name, filename
            )
        else:
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
    xlsxname: str = ENV.XLSX,
    cropped_vid: str = ENV.CROPPED_FILENAME,
):

    rsp = ResonatorPipeline(
        data_dict["video"],
        basis_image=basis_image,
        dims=dims,
        filename=f"{data_type}_{filename}",
    )
    rsp.run(f"{data_type}_{cropped_vid}")

    htp = HistogramPipeline(
        f"{inlet}{os.sep}{data_type}_{filename}",
        data_dict["data"][data_type],
        xlsxname=f"{data_type}_{xlsxname}",
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

    targets = total_video_splitter(data_dict["total"])

    for title in ("concentration", "washing"):
        _data_dict_tmp = {}
        _data_dict_tmp["video"] = targets[title]
        _data_dict_tmp["data"] = data_dict["total"]["data"]

        _run_pipeline(
            _data_dict_tmp, title, inlet, basis_image, dims, plot_name, filename
        )


def total_video_splitter(
    data_dict: dict,
):
    """HistogramPipeline is only set up to do a single phase - be that
    concentration or washing. In order to run a "total video" need to
    split the sliced array into two parts - one for concentration and
    one for washing.
    """

    ref_dat = data_dict["data"]["reference"]["data"]
    ref_dict = dict(zip(ref_dat["index"], ref_dat.value))

    rng_dat = (
        ("concentration", (0, ref_dict["End of concentration"])),
        (
            "washing",
            (
                ref_dict["Start of washing"],
                VideoFileClip(data_dict["video"]).duration,
            ),
        ),
    )

    targets = {}
    for dat in rng_dat:
        targets[dat[0]] = _split_video(data_dict["video"], dat)

    return targets


def _split_video(vid_path, rng_dat):
    vid_i = os.sep.join(vid_path.split(os.sep)[:-1])
    vid_n = vid_path.split(os.sep)[-1]
    targetname = f"{vid_i}{os.sep}{rng_dat[0]}_{vid_n}"
    ffmpeg_extract_subclip(
        vid_path,
        rng_dat[1][0],
        rng_dat[1][1],
        targetname=f"{vid_i}{os.sep}{rng_dat[0]}_{vid_n}",
    )
    return targetname
