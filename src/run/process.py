import os
from pathlib import Path

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

    if n == 1:
        data_items = _process_one_video(inlet, xlsx, {})
    elif n == 2:
        data_items = _process_two_videos(inlet, xlsx, {})
    elif n > 3:
        raise FileException("too many", "video", inlet)
    else:
        raise FileException("no", "video", inlet)

    return data_items


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


def _make_data_dictionary(title: str, xlsx: dict, data_dict={}) -> dict:
    """Make dictionary of data using dictionary created
    using XLSX reader utility.
    """

    def _get_data(title: str, xlsx: dict, sensor_data={}) -> dict:
        for xl_title in xlsx:
            stage, sensor = xl_title.split("_")
            if stage == title:
                sensor_data[sensor] = xlsx[xl_title]
        return sensor_data

    if title == "total":
        for title in ["concentration", "washing", "reference"]:
            data_dict[title] = _get_data(title, xlsx)
    else:
        data_dict[title] = _get_data(title, xlsx)
    return data_dict


def _check_file_naming(vid_title: str) -> str:
    """Check what the naming convention of
    the video is, to determine if it is
    concentration, washing or other
    """
    if "Concentration" in vid_title:
        return "concentration"
    elif "Washing" in vid_title:
        return "washing"
    else:
        return "total"


def get_video(path: str, video_name: str = ".mp4") -> list:
    """Get all videos on path based on video name. Defaults
    to all videos.
    """
    vids = [v for v in os.listdir(path) if video_name in v]
    return [f"{path}{os.sep}{v}" for v in vids]


def count_vid_files(inlet: str) -> int:
    return len(get_video(inlet))


def _get_xlsx_reader(path: str, video_name: str = "*") -> dict:
    """Checks all the files on path to determine if any is
    an xlsx, then create a dictionary out of the xlsx data
    """
    glob_path = Path(f"{path}{os.sep}")
    xlsx_list = [str(pp) for pp in glob_path.glob(f"**{os.sep}{video_name}.xlsx")]

    if len(xlsx_list) > 1:
        raise FileException("too many", "xlsx files", path)
    elif len(xlsx_list) < 1:
        raise FileException("too few", "xlsx files", path)

    return ReadExcel(xlsx_list[0]).run()
