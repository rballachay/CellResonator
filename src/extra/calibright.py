import os
from pathlib import Path
from typing import Tuple

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from sklearn.linear_model import LinearRegression

COLORS = list(mcolors.BASE_COLORS.keys())


def calibrate_brightness(path: Path, save: Path = Path("data/calibrate/results")):
    """Main function for calibrating relationship between brightness and cell loss.
    Takes all xlsx data from input path, reads in the cell count and brightness
    columns, creates linear regression model, saves coeffients into .env file and
    saves calibration image to save path.
    """
    fit_df, hash_df = gen_df(path)
    alpha, beta = _fit_linear_model(fit_df)
    fig = _plot_data(fit_df, alpha, beta)
    fig.savefig(f"{save.resolve()}{os.sep}cal_fig_{hash_df}.png")
    _save_cal_coefs(alpha, beta)


def gen_df(path: Path) -> Tuple[pd.DataFrame, str]:
    """Read in the data, and generate a hash of the data that will
    be used to avoid writing the exact same calibration multiple
    times.
    """
    data = _read_data(path)
    fit_df = _gen_data(data)
    return fit_df, str(pd.util.hash_pandas_object(fit_df).sum())[:6]


def _read_data(path: Path) -> dict:
    """Read in all xlsx files from path and return as dictionary"""
    data = {}
    csv_list = [path / f for f in os.listdir(path) if ".xlsx" in f]
    for csv in csv_list:
        data[csv.stem] = pd.read_excel(csv)
    return data


def _gen_data(data: dict) -> pd.DataFrame:
    """Put data in format acceptable for"""
    for title, df in data.items():
        df["title"] = title
        df["date"] = title.split("_")[-1]
        df = _fit_data(df)
        data[title] = df
    return pd.concat(data.values())


def _fit_data(df: pd.DataFrame):
    """Need to fit polynomial model in order to have the brightness at each
    time point cell counts are taken"""
    _df = df.copy()
    a = np.polyfit(
        _df["Time (min) - imaging"], _df["Image analysis (Scaled Brightness)"], 7
    )
    _df.loc[:, "Polyfit"] = np.poly1d(a)(_df["Time (min) - cells"].values)
    return _df


def _plot_data(df: pd.DataFrame, alpha: float, beta: float) -> plt.Figure:
    """Plot calibration curve for brightness vs cell count, where
    each day of analysis if plotted with a different symbol/color.
    """
    fig, ax = plt.subplots(dpi=200)
    for (i, _date) in enumerate(df.date.unique()):
        _df = df[df.date == _date]
        ax.plot(
            _df["Polyfit"],
            _df["Cell count (M cells/mL)"],
            color=COLORS[i],
            marker=".",
            label=_date,
            linestyle="",
        )
    ax.plot(df["Polyfit"], df["Polyfit"] * alpha + beta, "k")
    ax.set_ylabel("Cell Count (M cells/mL)")
    ax.set_xlabel("Average Brightness")
    ax.legend()
    fig.text(0.12, 0.9, _title(alpha, beta), size=10, color="purple")
    return fig


def _title(alpha: float, beta: float):
    sign = "-" if beta < 0 else "+"
    return f"cells = {alpha:.3f} * brightness {sign} {abs(beta):.3f}"


def _fit_linear_model(fit_df: pd.DataFrame):
    """Fit linear regression model to brightness & cell count"""
    lr = LinearRegression()
    data = fit_df[["Polyfit", "Cell count (M cells/mL)"]].dropna().values
    lr.fit(data[:, 0].reshape(-1, 1), data[:, 1].reshape(-1, 1))
    return (lr.coef_[0][0], lr.intercept_[0])


def _save_cal_coefs(alpha: float, beta: float):
    """Open up the environment variable file
    and reset the coordinates after selecting
    with interactive class.
    """
    with open(".env", "r") as file:
        data = file.readlines()
    for i, line in enumerate(data):
        if "ALPHA_BRI = " in line:
            data[i] = f"ALPHA_BRI = {alpha}\n"
        elif "BETA_BRI = " in line:
            data[i] = f"BETA_BRI = {beta}\n"

    # and write everything back
    with open(".env", "w") as file:
        file.writelines(data)
