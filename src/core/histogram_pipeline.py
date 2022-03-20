#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 24 16:09:10 2021

@author: RileyBallachay
"""
import bisect
import math
import os
import warnings
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.ndimage

from ..config import ENV
from ..extra.tools import check_dir_make


class HistogramPipeline:
    """Convert brightness data from csv file to
    excel file with smaller sampling frequency and
    plot with cell counts and sensor resistance,
    as applicable.

    Args:
        path_sliced: path to sliced brightness csv
        data_dict: dictionary with cell and/or sensor data
        out_folder: folder to save results
        window: slice window (in pixels), down from top
        t_correct: time between resonator + sensor, seconds
        xlsxname: xlsx file to save xlsx file
        fps: time per frame, can be accessed through video
    """

    def __init__(
        self,
        path_sliced: str,
        data_dict: dict = {"cells": np.empty(0), "sensor": np.empty(0)},
        out_folder: str = None,
        window: tuple = (int(ENV.WIN_TOP), int(ENV.WIN_BOTTOM)),
        t_correct: int = float(ENV.TIME_CORRECT),
        xlsxname: bool = ENV.RESULTS_DATA,
        s_per_frame: float = float(ENV.TIME_PER_FRAME),
        vid_start: float = 0.0,
        gauss_std: int = int(ENV.GAUSS_STD),
        slice_freq: int = int(ENV.SLICE_FREQ),
        background: int = 0.0,
        coeffs: tuple = (float(ENV.ALPHA_BRI), float(ENV.BETA_BRI)),
    ):
        self.s_per_frame = s_per_frame
        self.vid_start = vid_start
        self.gauss_std = gauss_std
        self.slice_freq = slice_freq
        self.background = background
        self.coeffs = coeffs

        # if out_folder not set, create results folder in input folder
        if out_folder is None:
            out_folder = f"{os.sep.join(path_sliced.split(os.sep)[:-1])}{os.sep}results"
        self.out_folder = out_folder

        # check that results folder exists
        check_dir_make(out_folder)

        # preprocess data -> fix bounds and t_correct
        self.cellcount, self.sensordata, self.brightness_raw = self._preproc_data(
            data_dict["cells"].values,
            data_dict["sensor"].values,
            self._read_sliced(path_sliced, window),
            t_correct,
        )

        # smooth brightness data for saving and plotting
        self.brightness = self._transform_brightness(self.brightness_raw)

        # save data to xlsx if path provided
        if xlsxname is not None:
            self._data_to_xlsx(xlsxname)

    def plot(
        self,
        title: str,
        save: bool = False,
        filename: str = ENV.HIST_PLOT,
    ):
        # create figure to plot
        fig, ax = self._make_fig(title)

        # plot brightness onto ax
        self._plot_brightness(ax, self.brightness)

        # only plot cellcount if data exists
        if not np.all(np.isnan(self.cellcount)):
            self._plot_cellcount(ax, self.cellcount)

        # only plot sensor data if it exists
        if not np.all(np.isnan(self.sensordata)):
            self._plot_sensordata(ax, self.sensordata)

        # tight layout to account for new axes
        fig.tight_layout()

        # save fig to destination
        if save:
            fig.savefig(f"{self.out_folder}{os.sep}{filename}")

    def _plot_brightness(self, ax: plt.Axes, brightness: np.array):
        # plot brightness data onto fig -> always runs
        x = brightness[:, 0]
        ax.plot(
            x,
            brightness[:, 1],
            "maroon",
            label="Predicted Cell Loss",
        )
        ax.set_xticks(np.arange(math.floor(min(x)), math.ceil(max(x)) + 1, 1.0))

    def _plot_cellcount(self, ax: plt.Axes, cellcount: np.array):
        # plot cell count data if it exists
        ax2 = ax.twinx()
        ax2.set_ylabel("Downstream Cell Count", color="black", fontsize=10)
        ax2.plot(
            cellcount[:, 0],
            cellcount[:, 1],
            "k.",
            label="Downstream Cell Count",
        )

    def _plot_sensordata(self, ax: plt.Axes, sensordata: np.array):
        # plot sensor data if it exists
        ax3 = ax.twinx()
        ax3.set_ylabel("Sensor Measurements", color="blue", fontsize=10)
        ax3.plot(
            sensordata[:, 0],
            sensordata[:, 1],
            "b*",
            label="Sensor Measurements",
        )
        ax3.spines["right"].set_position(("outward", 70))

    def _make_fig(self, title: str) -> Tuple[plt.Figure, plt.Axes]:
        # create figure to plot
        fig, ax = plt.subplots(dpi=200)
        fig.set_figheight(5)
        fig.set_figwidth(12)
        fig.autofmt_xdate()
        ax.set_xlabel("Run Duration (minutes)")
        ax.set_title(title)
        ax.set_ylabel("Average Brightness at Top of Frame", color="maroon", fontsize=10)
        return fig, ax

    def _preproc_data(
        self,
        cellcount: np.array,
        sensordata: np.array,
        brightness: np.array,
        t_correct: int,
    ) -> Tuple[np.array, np.array, np.array]:
        """Preprocess data in two steps:
        1. Fix bounds - remove excess brightness data
        2. Correct time from minutes to seconds, add delay
        """
        cellcount, sensordata, brightness = self._t_correct(
            cellcount, sensordata, brightness, t_correct
        )

        cellcount, sensordata, brightness = self._fix_bounds(
            cellcount, sensordata, brightness
        )

        return cellcount, sensordata, brightness

    def _apply_calibration(self, brightness: np.array) -> np.array:
        _brightness = brightness.copy()
        _brightness[:, 1] = _brightness[:, 1] * self.coeffs[0] + self.coeffs[1]
        return _brightness

    def _fix_bounds(
        self,
        cellcount: np.array,
        sensordata: np.array,
        brightness: np.array,
    ) -> Tuple[np.array, np.array, np.array]:
        """Brightness data spans the entire video, but we don't have
        cell counts for the entire time. To make the plot nicer, chop
        off excess data.
        """
        data = np.empty(0)
        if not np.all(np.isnan(cellcount)):
            data = np.concatenate((data, cellcount[:, 0]))
        if not np.all(np.isnan(sensordata)):
            data = np.concatenate((data, sensordata[:, 0]))
        if np.all(np.isnan(sensordata)) and np.all(np.isnan(cellcount)):
            warnings.warn(
                "You have neither cell count nor sensor data... is this a mistake?\n"
            )
            return cellcount, sensordata, brightness

        min_bright = bisect.bisect(brightness[:, 0], min(data))
        max_bright = bisect.bisect(brightness[:, 0], max(data))

        return cellcount, sensordata, brightness[min_bright:max_bright]

    def _t_correct(
        self,
        cellcount: np.array,
        sensordata: np.array,
        brightness: np.array,
        t_correct: np.array,
    ) -> Tuple[np.array, np.array, np.array]:
        """Change time from seconds to minutes, and
        subtract the 'time correction', to account for
        time it takes for cells to get from resonator
        to sensor downstream.
        """

        if not np.all(np.isnan(cellcount)):
            cellcount[:, 0] = cellcount[:, 0] / 60
        if not np.all(np.isnan(sensordata)):
            sensordata[:, 0] = sensordata[:, 0] / 60
        brightness[:, 0] = (brightness[:, 0] + self.vid_start + t_correct) / 60
        return cellcount, sensordata, brightness

    def _transform_brightness(self, brightness: np.array) -> np.array:
        """Perform gaussian smoothing on brightness data to
        reduce noise and mimic downstream dispersion.
        """
        _brightness = brightness.copy()
        _brightness[:, 1] = _brightness[:, 1] - self.background
        _brightness[:, 1] = scipy.ndimage.gaussian_filter1d(
            _brightness[:, 1], sigma=self.gauss_std
        )

        self.scaled_brightness = _brightness

        _brightness = self._apply_calibration(_brightness)

        return _brightness

    def _read_sliced(self, path_sliced: str, window: tuple) -> np.array:
        """Read in the sliced data from csv and convert slice number to
        time using s_per_frame and slice_freq
        """
        sliced = np.loadtxt(path_sliced, delimiter=",")
        means = sliced[:, window[0] : window[1]].mean(axis=1)
        time = (
            np.linspace(0, len(means), len(means)) * self.s_per_frame * self.slice_freq
        )
        brightness = np.stack((time, means), axis=1)
        return brightness

    def _data_to_xlsx(self, xlsxname: str):
        df = pd.DataFrame(
            data=np.hstack(
                (
                    self.brightness,
                    self.scaled_brightness[:, 1].reshape(-1, 1),
                    self.brightness_raw[:, 1].reshape(-1, 1),
                )
            ),
            columns=[
                "Time (min) - imaging",
                "Image analysis (Estimated Cell Loss)",
                "Image analysis (Scaled Brightness)",
                "Image analysis (Unscaled Brightness)",
            ],
        )

        if not np.all(np.isnan(self.cellcount)):
            df["Time (min) - cells"] = pd.Series(self.cellcount[:, 0])
            df["Cell count (M cells/mL)"] = pd.Series(self.cellcount[:, 1])

        if not np.all(np.isnan(self.sensordata)):
            df["Time (min) - sensor"] = pd.Series(self.sensordata[:, 0])
            df["Sensor"] = pd.Series(self.sensordata[:, 1])

        df.to_excel(f"{self.out_folder}{os.sep}{xlsxname}", index=False)
