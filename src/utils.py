
import os
from src.read_excel import ReadExcel
import glob

class FileException(Exception):
    def __init__(self, state, type, inlet):
        self.state = state
        self.inlet = inlet
        self.type = type

    def __str__(self):
        return f"There are {self.state} {self.type} files in the provided folder, please check folder {self.inlet} and refer to docs"


def process_config(inlet, file_num):
    xlsx = _get_xlsx(inlet)
    data_items={}
    
    if str(file_num)=="1":
        data_items = _process_one_video(inlet,xlsx,data_items)
    elif str(file_num)=="2":
        data_items = _process_two_videos(inlet,xlsx,data_items)
    elif int(file_num)>3:
        raise FileException("too many","video",inlet)
    else:
        raise FileException("no","video",inlet)

    return data_items


def _process_two_videos(inlet,xlsx,data_items):
    for title in ["concentration","washing"]:
        data_items = _process_one_video(inlet,xlsx,data_items,title=title,n_ideal=2)
    return data_items


def _process_one_video(inlet,xlsx,data_items,title="*",n_ideal=1):
    n = _count_files(inlet)
    if n>n_ideal:
        raise FileException("too many", "videos", inlet)
    elif n<n_ideal:
        raise FileException("too few", "videos", inlet)
    else:
        video_name = _get_video_name(inlet, title)
        vid_title = _get_video(inlet, video_name)
        title = _check_file_naming(vid_title)
        data = _make_data_dictionary(title, xlsx)
        data_items[title] = {"video":vid_title, "data":data}

    return data_items


def _get_video_name(path,title):
    if title=="*":
        return title
    else:
        vids = _get_video(path)
        for vid in vids:
            if title.capitalize() in vid:
                return vid
                
    raise FileException("no 'Concentration'/'Washing'","videos",path)


def _make_data_dictionary(title, xlsx):
    data_dict = {}
    if title=="total":
        for title in ["concentration","washing"]:
            data_dict[title] = _get_data(title, xlsx)
    else:
        data_dict[title] = _get_data(title, xlsx)  
    return data_dict


def _get_data(title, xlsx):
    sensor_data = {}
    for xl_title in xlsx:
        stage,sensor = xl_title.split("_")
        if stage==title:
            sensor_data[sensor] = xlsx[xl_title]
    return sensor_data


def _check_file_naming(vid_title):
    if "Concentration" in vid_title:
        return "concentration"
    elif "Washing" in vid_title:
        return "washing"
    else:
        return "total"


def _get_video(path, video_name="*.mp4"):
    return glob.glob(f"{path}{os.sep}{video_name}")


def _count_files(inlet):
    return len([file for file in os.listdir(inlet) if file.endswith('.mp4')])


def _get_xlsx(path,video_name="*"):
    xlsx_list = glob.glob(f"{path}{os.sep}{video_name}.xlsx")
    if len(xlsx_list)>1:
        raise FileException("too many", "xlsx files", path)
    elif len(xlsx_list)<1:
        raise FileException("too few", "xlsx files", path)

    return ReadExcel(xlsx_list[0]).run()