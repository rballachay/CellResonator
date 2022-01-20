import pandas as pd


class ReadExcel:
    def __init__(self, xlsx):
        self.xlsx = xlsx

    def run(self):
        xlsx = self.xlsx
        df_dict = self.get_cellcount_sensor_data(xlsx)
        return df_dict

    def get_cellcount_sensor_data(self, xlsx):

        df_dict = {}

        for title in self.NAME_DICT:
            try:
                val = self.NAME_DICT[title]
                df = pd.read_excel(
                    xlsx, usecols=val[0], skiprows=val[1], header=val[2]
                ).dropna(axis=0)

                if val[3]:
                    df = self._format_reference_data(df)

                df_dict[title] = df

            except Exception:
                print(
                    f"Something went wrong trying to get {title} data, check format specified in the docs."
                )
                continue

        df_dict = self._correct_df_time(df_dict)
        return df_dict

    NAME_DICT = {
        "concentration_cells": ("A:B", 0, 1, False),
        "concentration_sensor": ("C:D", 0, 1, False),
        "washing_cells": ("G:H", 0, 1, False),
        "washing_sensor": ("I:J", 0, 1, False),
        "reference_data": ("M:N", None, 0, True),
    }

    def _correct_df_time(self, df_dict):
        _df_dict = df_dict.copy()
        for title in df_dict:
            if title == "reference_data":
                continue
            df = df_dict[title]
            df[df.columns[0]] = (
                60 * df[df.columns[0]] + _df_dict["reference_data"][title]
            )
        return df_dict

    def _format_reference_data(self, df):
        _df = df.copy()
        _df = _df.replace("Start of video", "0:0")
        _df = _df[_df[_df.columns[1]].str.contains(":")]
        _df[_df.columns[1]] = [
            float(i.split(":")[0]) * 60 + float(i.split(":")[1])
            for i in _df[_df.columns[1]]
        ]
        df_dict = dict(zip(_df[_df.columns[0]], _df[_df.columns[1]]))
        df_dict["concentration_cells"] = df_dict["concentration_sensor"] = df_dict[
            "Start of concentration"
        ]
        df_dict["washing_cells"] = df_dict["washing_sensor"] = df_dict[
            "Start of washing"
        ]
        return df_dict
