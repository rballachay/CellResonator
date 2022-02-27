import os


def check_dir_make(path: str):
    if not os.path.exists(path):
        os.makedirs(path)
    return path
