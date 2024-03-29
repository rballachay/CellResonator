import os
from pathlib import Path

import moviepy.editor as mp


def get_downscaled_video(
    video_path: str, downsize: bool, height: int = 360, width: int = None
):
    if not downsize:
        return video_path
    # Note that I would use ffmpeg, however users of this script
    # are going to be on both windows and unix-type OS
    path = Path(video_path)
    out_path = f"{path.parent}{os.sep}{path.name[:-4]}_small.mp4"

    if os.path.exists(out_path):
        return out_path

    return downscale(video_path, out_path, height, width)


def downscale(video_path: str, out_path: str, height: int = 360, width: int = None):
    clip = mp.VideoFileClip(video_path)

    # make the height 360px ( According to moviePy documenation The width is
    # then computed so that the width/height ratio is conserved.)
    clip_resized = clip.resize(height=height, width=width)
    clip_resized.write_videofile(out_path)
    return out_path
