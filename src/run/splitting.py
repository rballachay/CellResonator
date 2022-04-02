import os
from typing import Tuple

from cv2 import watershed
from moviepy.editor import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from src.extra.tools import check_dir_make


def total_video_splitter(data_dict: dict) -> dict:
    """High-level function for splitting total video"""
    target_dat = _split_data(data_dict)
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

    # Access important info for splitting
    _conc_tuple, _wash_tuple = _get_tuples(ref_dict, data_dict)

    return (
        ("concentration", _conc_tuple),
        ("washing", _wash_tuple),
    )


def _get_tuples(ref_dict: dict, data_dict: dict) -> Tuple[tuple, tuple]:
    """Try to access important values for video splitting. Throw exception if
    these values are not present.
    """
    try:
        _conc_tuple = (0, ref_dict["End of concentration"])
    except:
        raise Exception(
            "Failed to split total video, there is no concentration end in the xlsx. Add to cell N6"
        )

    try:
        _wash_tuple = (
            ref_dict["Start of washing"],
            VideoFileClip(data_dict["video"]).duration,
        )
    except:
        raise Exception(
            "Failed to split total video, there is no washing start in the xlsx. Add to cell N7"
        )

    return _conc_tuple, _wash_tuple


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
