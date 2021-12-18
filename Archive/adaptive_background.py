#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 11 11:10:27 2021

@author: RileyBallachay
"""
import numpy as np
import pandas as pd
import cv2
from skimage import morphology, measure
 
cap = cv2.VideoCapture('/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Pipeline_v2.0/Outlet/Oct_26_specks/result.mp4')
w_frame, h_frame = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps, frames = cap.get(cv2.CAP_PROP_FPS), cap.get(cv2.CAP_PROP_FRAME_COUNT)

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()

# output
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Pipeline_v2.0/Outlet/Oct_26_specks/specks.mp4', fourcc, fps, (w_frame, h_frame), 0)
       
init=1
cnt=0                                                       
while(cap.isOpened()):
    
    ret, frame = cap.read()
    fgmask = fgbg.apply(frame)
 
    # I see the answer now. Here you save all the video
    out.write(fgmask)
    cnt+=1
    
    if ret==True:

        fgmask = fgbg.apply(frame)
 
        # I see the answer now. Here you save all the video
        out.write(fgmask)
        
        fgmask = morphology.remove_small_objects(fgmask, 50)
        fgmask = morphology.remove_small_holes(fgmask, 50)
            
        if np.sum(fgmask)==0:
            continue
        else:
            fgmask = measure.label(fgmask)
            
            if cnt%fps==0:
                if init:
                    astack = pd.DataFrame.from_dict(measure.regionprops_table(fgmask,properties=('label','bbox','area')))
                    astack['frame'] = cnt
                    init=0
                else:       
                    temp = pd.DataFrame.from_dict(measure.regionprops_table(fgmask,properties=('label','bbox','area')))
                    temp['frame'] = cnt
                    astack = pd.concat([astack,temp],axis=0)
    else:
        break

     
astack.to_csv('/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Pipeline_v2.0/Outlet/Oct_26_specks/specks.csv')
cap.release()
out.release()
cv2.destroyAllWindows()