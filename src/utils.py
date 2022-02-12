import os


def check_dir_make(path: str):
    if not os.path.exists(path):
        os.mkdir(path)
