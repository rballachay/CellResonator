import os

from src.core.read_excel import ReadExcel
from src.run.flag import FileException
from src.run.utils import count_vid_files, get_video, get_wash_start


def process_config(inlet: str):
    """Check that all files exist, and determine
    how the number of videos are going to be processed.
    """

    # get XLSX data from inlet
    xlsx = _get_xlsx_reader(inlet)

    # count the number of video files in inlet
    n = count_vid_files(inlet)

    # Processing either one or two video
    data_items = {}
    if n == 1:
        data_items = _process_one_video(inlet, xlsx, data_items)
    elif n == 2:
        for title in ["concentration", "washing"]:
            data_items = _process_one_video(inlet, xlsx, data_items, title=title)

    # If there are more or less than 1-2 videos, throw exception
    elif n > 3:
        raise FileException("too many", "video", inlet)
    else:
        raise FileException("no", "video", inlet)

    return data_items, get_wash_start(xlsx)


def _process_one_video(
    inlet: str, xlsx: dict, data_items: dict, title: str = "total"
) -> dict:
    """Process a single video from start to finish.
    1. Get the name of the video + Check that the video is correct
    3. Get data dictionary for said video
    4. Add data video to data_items
    """
    # get the name of a single video (check if it is total, conc or wash)
    vid_title, _title = _get_video_details(inlet, title)
    data = _make_data_dictionary(_title, xlsx)
    data_items[_title] = {"video": vid_title, "data": data}
    return data_items


def _get_video_details(path: str, title: str) -> str:
    """Get the video from path, using the title
    to determine whether list is acceptable or not
    """

    def _check_single_video(vid_title: str) -> str:
        """Check what the naming convention of
        the video is, to determine if it is
        concentration, washing or other"""
        if "concentration" in vid_title.lower():
            return "concentration"
        elif "washing" in vid_title.lower():
            print(
                "\nProcessing a single washing video - the background will be subtracted from washing... this is not advised\n"
            )
            return "washing"
        else:
            print("\nProcessing as a total video...")
            print(
                "If you meant to process concentration or washing videos, make sure you add concentration/washing in the video title\n"
            )
            return "total"

    if title == "total":
        _vid = get_video(path)[0]
        _title = _check_single_video(_vid)
        return _vid, _title
    else:
        vids = get_video(path)
        for vid in vids:
            if title in vid.lower():
                return vid, title

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


def _get_xlsx_reader(path: str, xlsx_name: str = ".xlsx") -> dict:
    """Checks all the files on path to determine if any is
    an xlsx, then create a dictionary out of the xlsx data
    """
    xlsx_list = [f"{path}{os.sep}{v}" for v in os.listdir(path) if xlsx_name in v]
    if len(xlsx_list) > 1:
        raise FileException("too many", "xlsx files", path)
    elif len(xlsx_list) < 1:
        raise FileException("no", "xlsx files", path)

    return ReadExcel(xlsx_list[0]).run()
