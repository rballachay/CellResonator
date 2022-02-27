#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 24 16:09:10 2021

@author: RileyBallachay
"""
import bisect
import os
import warnings
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.ndimage
from sklearn.preprocessing import MinMaxScaler

from ..config import ENV
from ..extra.tools import check_dir_make


class HistogramPipeline:
    def __init__(
        self,
        path_sliced: str,
        data_dict: dict = {"cells": np.empty(1), "sensor": np.empty(1)},
        out_folder: str = None,
        window: tuple = (25, 100),
        t_correct: int = 50,
        xlsxname: bool = ENV.RESULTS_DATA,
        fps: float = ENV.TIME_PER_FRAME,
    ):
        self.fps = fps

        if out_folder is None:
            out_folder = f"{os.sep.join(path_sliced.split(os.sep)[:-1])}{os.sep}results"
        self.out_folder = out_folder

        check_dir_make(out_folder)

        self.cellcount, self.sensordata, self.brightness_raw = self._preproc_data(
            data_dict["cells"].values,
            data_dict["sensor"].values,
            self._read_sliced(path_sliced, window),
            t_correct,
        )

        self.brightness = self._transform_brightness(self.brightness_raw)

        if xlsxname is not None:
            self._data_to_xlsx(xlsxname)

    def plot(
        self,
        title: str,
        save: bool = False,
        filename: str = ENV.HIST_PLOT,
    ):
        if not hasattr(self, "brightness"):
            warnings.warn(
                "No data dictionary was provided in init - the plot method will not create a plot"
            )
            return

        fig, ax = self._make_fig(title)

        self._plot_brightness(ax, self.brightness)

        if not np.all(np.isnan(self.cellcount)):
            self._plot_cellcount(ax, self.cellcount)

        if not np.all(np.isnan(self.sensordata)):
            self._plot_sensordata(ax, self.sensordata)

        fig.tight_layout()

        if save:
            fig.savefig(f"{self.out_folder}{os.sep}{filename}")

    def _plot_brightness(self, ax: plt.Axes, brightness: np.array):
        (p1,) = ax.plot(
            brightness[:, 0],
            brightness[:, 1],
            "maroon",
            label="Predicted Cell Loss",
        )

    def _plot_cellcount(self, ax: plt.Axes, cellcount: np.array):
        ax2 = ax.twinx()
        ax2.set_ylabel("Downstream Cell Count", color="black", fontsize=10)
        (p2,) = ax2.plot(
            cellcount[:, 0],
            cellcount[:, 1],
            "k.",
            label="Downstream Cell Count",
        )

    def _plot_sensordata(self, ax: plt.Axes, sensordata: np.array):
        ax3 = ax.twinx()
        ax3.set_ylabel("Sensor Measurements", color="grey", fontsize=10)
        (p3,) = ax3.plot(
            sensordata[:, 0],
            sensordata[:, 1],
            color="gray",
            marker=".",
            linestyle="None",
            label="Sensor Measurements",
        )
        ax3.spines["right"].set_position(("outward", 70))

    def _make_fig(self, title: str) -> Tuple[plt.Figure, plt.Axes]:
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
        cellcount, sensordata, brightness = self._fix_bounds(
            cellcount, sensordata, brightness
        )
        cellcount, sensordata, brightness = self._t_correct(
            cellcount, sensordata, brightness, t_correct
        )
        return cellcount, sensordata, brightness

    def _fix_bounds(
        self, cellcount: np.array, sensordata: np.array, brightness: np.array
    ) -> Tuple[np.array, np.array, np.array]:
        if not np.all(np.isnan(cellcount)):
            data = cellcount
        elif not np.all(np.isnan(sensordata)):
            data = sensordata
        else:
            warnings.warn(
                "You have neither cell count nor sensor data... is this a mistake?\n"
            )
            return cellcount, sensordata, brightness

        min_bright = bisect.bisect(brightness[:, 0], data[0, 0])
        max_bright = bisect.bisect(brightness[:, 0], data[-1, 0])

        return cellcount, sensordata, brightness[min_bright:max_bright]

    def _t_correct(
        self, cellcount, sensordata: np.array, brightness: np.array, t_correct: np.array
    ) -> Tuple[np.array, np.array, np.array]:
        _cellcount = cellcount.copy()
        _sensordata = sensordata.copy()
        _brightness = brightness.copy()
        if not np.all(np.isnan(_cellcount)):
            _cellcount[:, 0] = (_cellcount[:, 0] - t_correct) / 60
        elif not np.all(np.isnan(_sensordata)):
            _sensordata[:, 0] = (_sensordata[:, 0] - t_correct) / 60
        _brightness[:, 0] = _brightness[:, 0] / 60
        return _sensordata, _cellcount, _brightness

    def _transform_brightness(self, brightness: np.array) -> np.array:
        _brightness = brightness.copy()
        _brightness[:, 1] = MinMaxScaler().fit_transform(
            scipy.ndimage.gaussian_filter1d(_brightness[:, 1], sigma=40).reshape(-1, 1)
        )[:, 0]
        return _brightness

    def _read_sliced(
        self, path_sliced: str, window: tuple, avg_window: int = 5
    ) -> np.array:
        sliced = np.loadtxt(path_sliced, delimiter=",")
        means = sliced[:, window[0] : window[1]].mean(axis=1)[::avg_window]
        time = (
            np.linspace(0, len(means), len(means))
            * float(self.fps)
            * float(ENV.SLICE_FREQ)
            * avg_window
        )
        brightness = np.stack((time, means), axis=1)
        return brightness

    def _data_to_xlsx(self, xlsxname: str):
        df = pd.DataFrame(
            data=np.hstack((self.brightness, self.brightness_raw[:, 1].reshape(-1, 1))),
            columns=[
                "Time (min) - imaging",
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
