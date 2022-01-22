#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 18 20:56:55 2021

@author: RileyBallachay
"""
import numpy as np
import cv2
import matplotlib.pyplot as plt
import scipy.misc
from PIL import Image
import datetime

# Here you can define your croping values
x = 366; y= 104; w=273; h= 521
"""
# Open the video
cap = cv2.VideoCapture('backgroun_2.mp4')

w_frame, h_frame = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps, frames = cap.get(cv2.CAP_PROP_FPS), cap.get(cv2.CAP_PROP_FRAME_COUNT)

ims = []
while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        frame = frame[y:y+h, x:x+w]
        ims.append(frame)
    else:
        break
        

ims =  np.array([np.array(im) for im in ims])
imave = np.average(ims,axis=0).astype(int)
imave=np.array(np.round(imave),dtype=np.uint8)

"""
# Initialize frame counter
cnt = 0
cap = cv2.VideoCapture('/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Original_Videos/May10_2021.mp4')
# Some characteristics from the original video
w_frame, h_frame = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps, frames = cap.get(cv2.CAP_PROP_FPS), cap.get(cv2.CAP_PROP_FRAME_COUNT)

time_per_frame = 1/fps
print(frames)

# output
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('result_total_may10_trial.mp4', fourcc, fps, (w, h))

time = 0
slices = []
imageList = []
# Now we start
while(cap.isOpened()):
    ret, frame = cap.read()

    cnt += 1 # Counting frames

    # Avoid problems when video finish
    if ret==True:
        if cnt%10==0:
            time = time+time_per_frame
            printtime = str(datetime.timedelta(seconds=time))
            # Croping the frame
            temp_frame = frame[y:y+h, x:x+w]
            #crop_frame = cv2.subtract(temp_frame,imave)
            crop_frame = temp_frame
    
            # Percentage
            xx = cnt *100/frames
            print((xx),'%')
    
            imageGREY = crop_frame.mean(axis=2)
            imageGREY = imageGREY.mean(axis=1)
            slices.append(imageGREY)
            # Saving from the desired frames
            #if 15 <= cnt <= 90:
            #    out.write(crop_frame)
            font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
            crop_frame = cv2.putText(crop_frame, printtime,
                                (10, 50),
                                font, 1,
                                (255, 255, 255), 
                                2, cv2.LINE_8)
            # I see the answer now. Here you save all the video
            out.write(crop_frame)
    
            # Just to see the video in real time          
            #cv2.imshow('frame',frame)
            cv2.imshow('croped',crop_frame)
            
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break
    else:
        break

def groupedAvg(myArray, N=5):
    result = np.cumsum(myArray, 0)[N-1::N]/float(N)
    result[1:] = result[1:] - result[:-1]
    return result

sliced = np.stack(slices, axis=0)
sliced = groupedAvg(sliced)
np.savetxt('sliced.csv',sliced,delimiter=',')
np.savetxt('PCA_compressed.csv',pca_rep,delimiter=',')
cap.release()
out.release()
cv2.destroyAllWindows()