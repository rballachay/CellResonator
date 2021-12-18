#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 15 12:06:01 2021

@author: RileyBallachay
"""
# Importing all necessary libraries
import cv2
import os
import time

# Read the video from specified path
cam = cv2.VideoCapture("/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Pipeline_v2.0/Basis/Nov10_2021_Washing.mp4")

try:

    # creating a folder named data
    if not os.path.exists('data_sep17_registration'):
        os.makedirs('data_sep17_registration')

    # if not created then raise error
except OSError:
    print('Error: Creating directory of data')

# frame
currentframe = 0
frame_per_second = int(cam.get(cv2.CAP_PROP_FPS))+1

while (True):
    print(currentframe)
    ret, frame = cam.read()
    if not(currentframe%(100*frame_per_second)):  
        # if video is still left continue creating images
        name = './data_sep17_registration/frame' + str(currentframe) + '.jpg'
        print('Creating...' + name)

        # writing the extracted images
        cv2.imwrite(name, frame)
    
    currentframe += 1
    

# Release all space and windows once done
cam.release()
cv2.destroyAllWindows()