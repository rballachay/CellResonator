#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 24 16:09:10 2021

@author: RileyBallachay
"""
import bisect
import os
import warnings

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.ndimage
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler

from .config import ENV


class HistogramPipeline:
    def __init__(
        self,
        path_sliced: str,
        data_dict: dict,
        out_folder: str = None,
        window: tuple = (0, 50),
        t_correct: int = 50,
    ):
        if out_folder is None:
            out_folder = os.sep.join(path_sliced.split(os.sep)[:-1])

        self.out_folder = out_folder
        self.t_correct = t_correct

        self.cellcount, self.sensordata, self.brightness = self._fix_bounds(
            data_dict["cells"].values,
            data_dict["sensor"].values,
            self._read_sliced(path_sliced, window),
        )

    def plot(
        self,
        title: str,
        save: bool = False,
        filename: str = ENV.HIST_PLOT,
    ):
        fig, ax = self._make_fig(title)

        self._plot_brightness(ax, self.brightness)

        if not np.all(np.isnan(self.cellcount)):
            self._plot_cellcount(ax, self.cellcount)

        if not np.all(np.isnan(self.sensordata)):
            self._plot_sensordata(ax, self.sensordata)

        fig.tight_layout()

        if save:
            fig.savefig(f"{self.out_folder}{os.sep}{filename}")

    def _plot_brightness(self, ax, brightness):
        (p1,) = ax.plot(
            brightness[:, 0] / 60,
            MinMaxScaler().fit_transform(
                scipy.ndimage.gaussian_filter1d(brightness[:, 1], sigma=40).reshape(
                    -1, 1
                )
            ),
            "maroon",
            label="Predicted Cell Loss",
        )

    def _plot_cellcount(self, ax, cellcount):
        ax2 = ax.twinx()
        ax2.set_ylabel("Downstream Cell Count", color="black", fontsize=10)
        (p2,) = ax2.plot(
            (cellcount[:, 0] - self.t_correct) / 60,
            cellcount[:, 1].reshape(-1, 1),
            "k.",
            label="Downstream Cell Count",
        )

    def _plot_sensordata(self, ax, sensordata):
        ax3 = ax.twinx()
        ax3.set_ylabel("Sensor Measurements", color="grey", fontsize=10)
        (p3,) = ax3.plot(
            (sensordata[:, 0] - self.t_correct) / 60,
            sensordata[:, 1].reshape(-1, 1),
            color="gray",
            marker=".",
            linestyle="None",
            label="Sensor Measurements",
        )
        ax3.spines["right"].set_position(("outward", 70))

    def _make_fig(self, title):
        fig, ax = plt.subplots(dpi=200)
        fig.set_figheight(5)
        fig.set_figwidth(12)
        fig.autofmt_xdate()
        ax.set_xlabel("Run Duration (minutes)")
        ax.set_title(title)
        ax.set_ylabel("Average Brightness at Top of Frame", color="maroon", fontsize=10)
        return fig, ax

    def _fix_bounds(self, cellcount, sensordata, brightness):
        if not np.all(np.isnan(cellcount)):
            data = cellcount
        elif not np.all(np.isnan(sensordata)):
            data = sensordata
        else:
            warnings.warn(
                "You have neither cell count nor sensor data... is this a mistake?\n"
            )
            return cellcount, sensordata, brightness

        t_min = data[0, 0]
        t_max = data[-1, 0]
        min_bright = bisect.bisect(brightness[:, 0], data[0, 0])
        max_bright = bisect.bisect(brightness[:, 0], data[-1, 0])

        return cellcount, sensordata, brightness[min_bright:max_bright]

    def _read_sliced(self, path_sliced: str, window: tuple, avg_window: int = 5):
        sliced = np.loadtxt(path_sliced, delimiter=",")
        means = sliced[:, window[0] : window[1]].mean(axis=1)[::avg_window]
        time = (
            np.linspace(0, len(means), len(means))
            * float(ENV.TIME_PER_FRAME)
            * float(ENV.SLICE_FREQUENCY)
            * avg_window
        )
        brightness = np.stack((time, means), axis=1)
        return brightness
