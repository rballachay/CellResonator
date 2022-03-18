import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def calibrate_brightness(path: Path, save: Path = Path("data/calibrate/results")):
    fit_df, hash_df = gen_df(path)
    fit_df = fit_df[fit_df["title"].str.contains("concentration")]
    alpha, beta = _fit_linear_model(fit_df)
    fig = _plot_data(fit_df, alpha, beta)
    fig.savefig(f"{save.resolve()}{os.sep}cal_fig_{hash_df}.png")
    _save_cal_coefs(alpha, beta)


def gen_df(path: Path):
    data = _read_data(path)
    meta_df = _concat_data(data)
    fit_df = _fit_data(meta_df)
    return fit_df, str(pd.util.hash_pandas_object(fit_df).sum())[:6]


def _read_data(path: Path) -> list:
    data = {}
    csv_list = [path / f for f in os.listdir(path) if ".xlsx" in f]
    for csv in csv_list:
        data[csv.stem] = pd.read_excel(csv)
    return data


def _concat_data(data: dict) -> pd.DataFrame:
    for title, df in data.items():
        df["title"] = title

        if "meta_df" not in locals():
            meta_df = df
        else:
            meta_df = pd.concat([meta_df, df])
    return meta_df


def _fit_data(df: pd.DataFrame):
    dfs = []
    for title in df.title.unique():
        _df = df[df.title == title]
        a = np.polyfit(
            _df["Time (min) - imaging"], _df["Image analysis (Scaled Brightness)"], 7
        )
        _df.loc[:, "Polyfit"] = np.poly1d(a)(_df["Time (min) - cells"].values)
        dfs.append(_df)
    return pd.concat(dfs)


def _plot_data(df: pd.DataFrame, alpha: float, beta: float) -> plt.Figure:
    fig, ax = plt.subplots(dpi=200)
    ax.plot(df["Cell count (M cells/mL)"], df["Polyfit"], "k.")
    ax.plot(
        df["Cell count (M cells/mL)"], df["Cell count (M cells/mL)"] * alpha + beta, "r"
    )
    ax.set_xlabel("Cell Count (M cells/mL)")
    ax.set_ylabel("Average Brightness")
    return fig


def _fit_linear_model(fit_df: pd.DataFrame):
    lr = LinearRegression()
    data = fit_df[["Cell count (M cells/mL)", "Polyfit"]].dropna().values
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
