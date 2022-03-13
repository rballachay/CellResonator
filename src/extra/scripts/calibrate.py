import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _read_csvs(path: Path) -> list:
    return [Path(f"{path}{os.sep}{f}") for f in os.listdir(path) if ".xlsx" in f]


def _read_data(csv_list: list):
    data = {}
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
        _df["Polyfit"] = np.poly1d(a)(_df["Time (min) - cells"])
        dfs.append(_df)
    return pd.concat(dfs)


def _plot_data(df: pd.DataFrame, save: Path):
    fig, ax = plt.subplots(dpi=200)
    ax.plot(df["Cell count (M cells/mL)"], df["Polyfit"], "k.")
    plt.xlabel("Cell Count (M cells/mL)")
    plt.ylabel("Average Brightness")
    plt.savefig(save.resolve())


def main(path: Path, save: Path):
    csv_list = _read_csvs(path)
    data = _read_data(csv_list)
    meta_df = _concat_data(data)
    fit_df = _fit_data(meta_df)
    _plot_data(fit_df, save)
    print(meta_df)


if __name__ == "__main__":
    main(Path("data/calibrate"), Path("data/calibrate/results/out.png"))
