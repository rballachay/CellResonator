import os
from pathlib import Path

from src.read_excel import ReadExcel


class FileException(Exception):
    def __init__(self, state, type, inlet):
        self.state = state
        self.inlet = inlet
        self.type = type

    def __str__(self):
        return f"There are {self.state} {self.type} files in the provided folder, please check folder {self.inlet} and refer to docs"


def process_config(inlet):
    xlsx = _get_xlsx(inlet)

    data_items = {}

    n = _count_files(inlet)

    if n == 1:
        data_items = _process_one_video(inlet, xlsx, data_items)
    elif n == 2:
        data_items = _process_two_videos(inlet, xlsx, data_items)
    elif n > 3:
        raise FileException("too many", "video", inlet)
    else:
        raise FileException("no", "video", inlet)

    return data_items


def _process_two_videos(inlet, xlsx, data_items):
    for title in ["concentration", "washing"]:
        data_items = _process_one_video(inlet, xlsx, data_items, title=title)
    return data_items


def _process_one_video(inlet, xlsx, data_items, title="total"):
    vid_title = _get_video_name(inlet, title)
    title = _check_file_naming(vid_title)
    data = _make_data_dictionary(title, xlsx)
    data_items[_check_file_naming(vid_title)] = {"video": vid_title, "data": data}
    return data_items


def _get_video_name(path, title):
    if title == "total":
        return _get_video(path)[0]
    else:
        vids = _get_video(path)
        for vid in vids:
            if title.capitalize() in vid:
                return vid
    raise FileException("no 'Concentration'/'Washing'", "videos", path)


def _make_data_dictionary(title, xlsx):
    data_dict = {}
    if title == "total":
        for title in ["concentration", "washing", "reference"]:
            data_dict[title] = _get_data(title, xlsx)
    else:
        data_dict[title] = _get_data(title, xlsx)
    return data_dict


def _get_data(title, xlsx):
    sensor_data = {}
    for xl_title in xlsx:
        stage, sensor = xl_title.split("_")
        if stage == title:
            sensor_data[sensor] = xlsx[xl_title]

    return sensor_data


def _check_file_naming(vid_title):
    if "Concentration" in vid_title:
        return "concentration"
    elif "Washing" in vid_title:
        return "washing"
    else:
        return "total"


def _get_video(path, video_name=".mp4"):
    vids = [v for v in os.listdir(path) if video_name in v]
    vids = [
        f"{path}{os.sep}{v}"
        for v in vids
        if all([i not in v for i in ("small", "result")])
    ]
    return vids


def _count_files(inlet):
    return len(_get_video(inlet))


def _get_xlsx(path, video_name="*"):
    glob_path = Path(f"{path}{os.sep}")
    xlsx_list = [str(pp) for pp in glob_path.glob(f"**{os.sep}{video_name}.xlsx")]

    # exclude results - essential for multiple files
    xlsx_list = [x for x in xlsx_list if "results" not in x]
    if len(xlsx_list) > 1:
        raise FileException("too many", "xlsx files", path)
    elif len(xlsx_list) < 1:
        raise FileException("too few", "xlsx files", path)

    return ReadExcel(xlsx_list[0]).run()
