import os
import warnings

from src.core.read_excel import ReadExcel


class FileException(Exception):
    """Custom exception to write errors about file
    number or type to console.
    """

    def __init__(self, state, type, inlet):
        self.state = state
        self.inlet = inlet
        self.type = type

    def __str__(self):
        return f"There are {self.state} {self.type} files in the provided folder, please check folder {self.inlet} and refer to docs"


def process_config(inlet: str):
    """Check that all files exist, and determine
    how the number of videos are going to be processed.
    """

    # get XLSX data from inlet
    xlsx = _get_xlsx_reader(inlet)

    # count the number of video files in inlet
    n = count_vid_files(inlet)

    # check if results folder exists. if it does,
    # rename to results_int
    _check_results_folder(inlet)

    if n == 1:
        data_items = _process_one_video(inlet, xlsx, {})
    elif n == 2:
        data_items = _process_two_videos(inlet, xlsx, {})
    elif n > 3:
        raise FileException("too many", "video", inlet)
    else:
        raise FileException("no", "video", inlet)

    return data_items, _get_wash_start(xlsx)


def _process_two_videos(inlet: str, xlsx: dict, data_items: dict) -> dict:
    for title in ["concentration", "washing"]:
        data_items = _process_one_video(inlet, xlsx, data_items, title=title)
    return data_items


def _process_one_video(
    inlet: str, xlsx: dict, data_items: dict, title: str = "total"
) -> dict:
    """Process a single video from start to finish.
    1. Get the name of the video
    2. Check that the video is correct
    3. Get data dictionary for said video
    4. Add data video to data_items
    """
    vid_title = _get_video_name(inlet, title)
    title = _check_file_naming(vid_title)
    data = _make_data_dictionary(title, xlsx)
    data_items[_check_file_naming(vid_title)] = {"video": vid_title, "data": data}
    return data_items


def _get_video_name(path: str, title: str) -> str:
    """Get the video from path, using the title
    to determine whether list is acceptable or not
    """
    if title == "total":
        return get_video(path)[0]
    else:
        vids = get_video(path)
        for vid in vids:
            if title.capitalize() in vid:
                return vid
    raise FileException("no 'Concentration'/'Washing'", "videos", path)


def _make_data_dictionary(title: str, xlsx: dict) -> dict:
    """Make dictionary of data using dictionary created
    using XLSX reader utility.
    """
    data_dict = {}
    if title == "total":
        for title in ["concentration", "washing", "reference"]:
            data_dict[title] = _get_data(title, xlsx)
    else:
        data_dict[title] = _get_data(title, xlsx)
    return data_dict


def _get_data(title: str, xlsx: dict) -> dict:
    sensor_data = {}
    for xl_title in xlsx:
        stage, sensor = xl_title.split("_")
        if stage == title:
            sensor_data[sensor] = xlsx[xl_title]
    return sensor_data


def _check_file_naming(vid_title: str) -> str:
    """Check what the naming convention of
    the video is, to determine if it is
    concentration, washing or other
    """
    if "concentration" in vid_title.lower():
        return "concentration"
    elif "washing" in vid_title.lower():
        return "washing"
    else:
        return "total"


def get_video(path: str, video_name: str = ".mp4") -> list:
    """Get all videos on path based on video name. Defaults
    to all videos.
    """
    vids = [v for v in os.listdir(path) if video_name in v]
    return [
        f"{path}{os.sep}{v}"
        for v in vids
        if all([i not in v for i in ("small", "result")])
    ]


def count_vid_files(inlet: str) -> int:
    return len(get_video(inlet))


def _get_xlsx_reader(path: str, xlsx_name: str = ".xlsx") -> dict:
    """Checks all the files on path to determine if any is
    an xlsx, then create a dictionary out of the xlsx data
    """
    xlsx_list = [f"{path}{os.sep}{v}" for v in os.listdir(path) if xlsx_name in v]
    if len(xlsx_list) > 1:
        raise FileException("too many", "xlsx files", path)
    elif len(xlsx_list) < 1:
        raise FileException("too few", "xlsx files", path)

    return ReadExcel(xlsx_list[0]).run()


def _check_results_folder(inlet: str):
    """Don't want to overwrite results folders,
    so this will rename results to the lowest
    possible integer, i.e. results_1, to open
    up space for new results folder
    """
    res = f"{inlet}{os.sep}results"
    if os.path.isdir(res):
        i = 1
        while True:
            try:
                os.rename(res, f"{res}_{i}")
            except:
                i += 1
                continue
            break


def _get_wash_start(xlsx: dict) -> float:
    ref = xlsx["reference_data"]
    return float(ref[ref["index"] == "Start of washing"].value)
