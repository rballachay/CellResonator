import moviepy.editor as moviepy

clip = moviepy.VideoFileClip("tests/data/test_folder_1file/test_vid.mp4")
clip = clip.resize(height=90)
clip.write_videofile("tests/data/test_folder_1file/test_vid_small.mp4")
