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
        xlsxname: bool = ENV.XLSX,
    ):
        if out_folder is None:
            out_folder = os.sep.join(path_sliced.split(os.sep)[:-1])
        self.out_folder = out_folder

        self.cellcount, self.sensordata, self.brightness = self._preproc_data(
            data_dict["cells"].values,
            data_dict["sensor"].values,
            self._read_sliced(path_sliced, window),
            t_correct,
        )

        if xlsxname is not None:
            self._data_to_xlsx(
                self.cellcount, self.sensordata, self.brightness, xlsxname
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
            brightness[:, 0],
            brightness[:, 1],
            "maroon",
            label="Predicted Cell Loss",
        )

    def _plot_cellcount(self, ax, cellcount):
        ax2 = ax.twinx()
        ax2.set_ylabel("Downstream Cell Count", color="black", fontsize=10)
        (p2,) = ax2.plot(
            cellcount[:, 0],
            cellcount[:, 1],
            "k.",
            label="Downstream Cell Count",
        )

    def _plot_sensordata(self, ax, sensordata):
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

    def _make_fig(self, title):
        fig, ax = plt.subplots(dpi=200)
        fig.set_figheight(5)
        fig.set_figwidth(12)
        fig.autofmt_xdate()
        ax.set_xlabel("Run Duration (minutes)")
        ax.set_title(title)
        ax.set_ylabel("Average Brightness at Top of Frame", color="maroon", fontsize=10)
        return fig, ax

    def _preproc_data(self, cellcount, sensordata, brightness, t_correct):
        cellcount, sensordata, brightness = self._t_correct(
            cellcount, sensordata, brightness, t_correct
        )
        cellcount, sensordata, brightness = self._fix_bounds(
            cellcount, sensordata, brightness
        )
        return cellcount, sensordata, brightness

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

        min_bright = bisect.bisect(brightness[:, 0], data[0, 0])
        max_bright = bisect.bisect(brightness[:, 0], data[-1, 0])

        return cellcount, sensordata, brightness[min_bright:max_bright]

    def _t_correct(self, cellcount, sensordata, brightness, t_correct):
        sensordata[:, 0] = (sensordata[:, 0] - t_correct) / 60
        cellcount[:, 0] = (cellcount[:, 0] - t_correct) / 60
        brightness[:, 0] = brightness[:, 0] / 60
        brightness[:, 1] = MinMaxScaler().fit_transform(
            scipy.ndimage.gaussian_filter1d(brightness[:, 1], sigma=40).reshape(-1, 1)
        )[:, 0]
        return sensordata, cellcount, brightness

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

    def _data_to_xlsx(self, cellcount, sensordata, brightness, xlsxname):
        df = pd.DataFrame(
            data=brightness,
            columns=["Time (s) - imaging", "Image analysis (Scaled Brightness)"],
        )

        if not np.all(np.isnan(cellcount)):
            df["Time (s) - cells"] = pd.Series(cellcount[:, 0])
            df["Cell count (M cells/mL)"] = pd.Series(cellcount[:, 1])

        if not np.all(np.isnan(sensordata)):
            df["Time (s) - sensor"] = pd.Series(sensordata[:, 0])
            df["Sensor"] = pd.Series(sensordata[:, 1])

        df.to_excel(f"{self.out_folder}{os.sep}{xlsxname}", index=False)
