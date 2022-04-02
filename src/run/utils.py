import os

import numpy as np
from src.config import ENV


def get_background(
    fname: str,
    nframes_back: int = int(100 / int(ENV.SLICE_FREQ)),
    window: tuple = (int(ENV.WIN_TOP), int(ENV.WIN_BOTTOM)),
) -> float:
    """Get the average background intensity from the concentration
    sliced csv and return so it may be subtracted.
    """
    try:
        _fname = fname.replace("washing", "concentration")
        sliced = np.loadtxt(_fname, delimiter=",")
    except:
        print(
            "There is no concentration data, attemping to load washing data. Background subtraction with washing data is not advised."
        )
        _fname = fname.replace("concentration", "washing")
        sliced = np.loadtxt(fname, delimiter=",")

    means = sliced[:, window[0] : window[1]].mean(axis=1)
    return np.mean(means[:nframes_back])


def check_results_folder(inlet: str):
    """Don't want to overwrite results folders,
    so this will rename results to the lowest
    possible integer, i.e. results_1, to open
    up space for new results folder
    """
    res = f"{inlet}{os.sep}results"
    if os.path.isdir(res):
        i = 1
        while True:
            try:
                os.rename(res, f"{res}_{i}")
            except:
                i += 1
                continue
            break


def get_video(path: str, video_name: str = ".mp4") -> list:
    """Get all videos on path based on video name. Defaults
    to all videos.
    """
    vids = [v for v in os.listdir(path) if video_name in v]
    return [
        f"{path}{os.sep}{v}"
        for v in vids
        if all([i not in v for i in ("small", "result")])
    ]


def count_vid_files(inlet: str) -> int:
    return len(get_video(inlet))


def get_wash_start(xlsx: dict) -> float:
    """From xlsx data, get the start of washing step to adjust
    histogram at later stages.
    """
    ref = xlsx["reference_data"]
    return float(ref[ref["index"] == "Start of washing"].value)
