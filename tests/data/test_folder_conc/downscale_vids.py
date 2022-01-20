import moviepy.editor as moviepy

clip = moviepy.VideoFileClip("tests/data/test_folder/test_Washing.mp4")
clip = clip.resize(height=360)
clip.write_videofile("tests/data/test_folder/vid_Washing.mp4")
