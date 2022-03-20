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
    fname = fname.replace("washing", "concentration")
    sliced = np.loadtxt(fname, delimiter=",")
    means = sliced[:, window[0] : window[1]].mean(axis=1)
    return np.mean(means[:nframes_back])
