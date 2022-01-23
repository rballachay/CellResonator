#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 24 16:09:10 2021

@author: RileyBallachay
"""
import bisect
import os

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
        time_correction: int = 50,
    ):
        if out_folder is None:
            out_folder = os.sep.join(path_sliced.split(os.sep)[:-1])
        self.out_folder = out_folder
        self.time_correction = time_correction
        self.brightness = self._read_sliced(path_sliced, window)
        self.cellcount = self._read_cellcount(data_dict["cells"], time_correction)
        self.sensordata = self._read_sensordata(data_dict["sensor"], time_correction)
        self._fix_bounds()
        self._time_correct()

    def plot(
        self,
        title: str,
        save: bool = False,
        filename: str = ENV.HIST_PLOT,
    ):
        brightness = self.brightness
        cellcount = self.cellcount
        sensordata = self.sensordata
        fig, ax, ax2, ax3 = self._make_fig(title)
        scaler = MinMaxScaler()

        p1, = ax.plot(
            brightness[:, 0],
            scaler.fit_transform(
                scipy.ndimage.gaussian_filter1d(brightness[:, 1], sigma=40).reshape(
                    -1, 1
                )
            ),
            "maroon",
            label="Predicted Cell Loss",
        )
        p2, = ax2.plot(
            cellcount[:, 0],
            cellcount[:, 1].reshape(-1, 1),
            "k.",
            label="Downstream Cell Count",
        )
        p3, = ax3.plot(
            sensordata[:, 0],
            sensordata[:, 1].reshape(-1, 1),
            color="gray",
            marker='.',
            linestyle="None",
            label="Sensor Measurements",
        )

        #fig.legend(handles=[p1,p2,p3], bbox_to_anchor=(1.04,1), loc="upper left")
        ax3.spines['right'].set_position(('outward', 70))
        fig.tight_layout()

        if save:
            self._save_fig(fig, path=f"{self.out_folder}{os.sep}{filename}")

    def _save_fig(self, fig, path):
        fig.savefig(path)

    def _make_fig(self, title):
        fig, ax = plt.subplots(dpi=200)
        fig.set_figheight(5)
        fig.set_figwidth(12)
        fig.autofmt_xdate()
        ax.set_xlabel("Run Duration (minutes)")
        ax.set_title(title)
        ax.set_ylabel("Average Brightness at Top of Frame", color="maroon", fontsize=10)
        ax2 = ax.twinx()
        ax2.set_ylabel("Downstream Cell Count", color="black", fontsize=10)

        ax3 = ax.twinx()
        ax3.set_ylabel("Sensor Measurements", color="grey", fontsize=10)

        return fig, ax, ax2, ax3

    def _fix_bounds(self):
        cellcount = self.cellcount
        brightness = self.brightness
        t_min = cellcount[0, 0]
        t_max = cellcount[-1, 0]
        min_bright = bisect.bisect(brightness[:, 0], t_min)
        max_bright = bisect.bisect(brightness[:, 0], t_max)

        self.brightness = brightness[min_bright:max_bright]

    def _time_correct(self):
        self.cellcount[:, 0] = self.cellcount[:, 0] / 60
        self.brightness[:, 0] = self.brightness[:, 0] / 60
        self.sensordata[:, 0] = self.sensordata[:, 0] / 60

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

    def _read_cellcount(self, cellcount, time_correction: int):
        cellcount = cellcount.values
        cellcount[:, 0] = cellcount[:, 0] - time_correction
        return cellcount

    def _read_sensordata(self, sensordata, time_correction: int):
        sensordata=  sensordata.values
        sensordata[:, 0] =  sensordata[:, 0] - time_correction
        return sensordata

    
