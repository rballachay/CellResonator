#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 13 12:08:37 2021

@author: RileyBallachay
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import scipy.ndimage
import matplotlib.dates as mdates
import datetime
from sklearn.preprocessing import MinMaxScaler

class ResonatorPipeline:
    
    def __init__(self,inFolder,outFolder):
        self.inlet = inFolder
        self.outlet = outFolder
        self.basis = '/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Pipeline/Basis'
    
        self.prepare_registration()
        self.grab_background()
        self.pipeline_main()
        
    def prepare_registration(self):
        # Grab the first frame from our reference photo
        vid_basis = self.basis+'/background.mp4'
        vidcap = cv2.VideoCapture(vid_basis)
        success,image_basis = vidcap.read()  
        
        vid_new = self.inlet + '/background.mp4'
        vidcap = cv2.VideoCapture(vid_new)
        success,image_new = vidcap.read() 
        
        self.get_homography(image_new,image_basis)
        return
    
    def get_homography(self,image_new,image_basis):
        MAX_FEATURES = 500
        GOOD_MATCH_PERCENT = 0.99
        
        im1 = image_new
        im2 = image_basis
        # Convert images to grayscale
        im1Gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
        im2Gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
      
        # Detect ORB features and compute descriptors.
        orb = cv2.ORB_create(MAX_FEATURES)
        keypoints1, descriptors1 = orb.detectAndCompute(im1Gray, None)
        keypoints2, descriptors2 = orb.detectAndCompute(im2Gray, None)
      
        # Match features.
        matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
        matches = matcher.match(descriptors1, descriptors2, None)
      
        # Sort matches by score
        matches.sort(key=lambda x: x.distance, reverse=False)
      
        # Remove not so good matches
        numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
        matches = matches[:numGoodMatches]
      
        # Draw top matches
        imMatches = cv2.drawMatches(im1, keypoints1, im2, keypoints2, matches, None)
        cv2.imwrite(self.outlet+"/matches.jpg", imMatches)
      
        # Extract location of good matches
        points1 = np.zeros((len(matches), 2), dtype=np.float32)
        points2 = np.zeros((len(matches), 2), dtype=np.float32)
      
        for i, match in enumerate(matches):
          points1[i, :] = keypoints1[match.queryIdx].pt
          points2[i, :] = keypoints2[match.trainIdx].pt
      
        # Find homography
        h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)
      
        # Use homography
        self.height, self.width, channels = im2.shape
        im1Reg = cv2.warpPerspective(im1, h, (self.width, self.height))
        
        self.homography = h
        return
    
    def grab_background(self):
        # Open the video
        background_path = self.inlet+'/background.mp4'
        cap = cv2.VideoCapture(background_path)
        
        # Get video characteristics
        w_frame, h_frame = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps, frames = cap.get(cv2.CAP_PROP_FPS), cap.get(cv2.CAP_PROP_FRAME_COUNT)
        
        ims = []
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret==True:
                frame = frame
                ims.append(frame)
            else:
                break

        ims =  np.array([np.array(im) for im in ims])
        imave = np.average(ims,axis=0).astype(int)
        imave=np.array(np.round(imave),dtype=np.uint8)
        
        self.back_to_sub = imave
        return
      
    def groupedAvg(self,myArray, N=5):
        result = np.cumsum(myArray, 0)[N-1::N]/float(N)
        result[1:] = result[1:] - result[:-1]
        return result
        
    def hist_normalization(self,img, a=0, b=255):
        c = img.min()
        d = img.max()
     
        out = img.copy()
        # normalization
        out = (b - a) / (d - c) * (out - c) + a
        out[out < a] = a
        out[out > b] = b
     
        out = out.astype(np.uint8)
        return out

    def pipeline_main(self):
        X = 366; Y= 104; W=273; H= 521
        
        # Initialize frame counter
        cnt = 0
        cap = cv2.VideoCapture(self.inlet+'/main.mp4')
        # Some characteristics from the original video
        w_frame, h_frame = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps, frames = cap.get(cv2.CAP_PROP_FPS), cap.get(cv2.CAP_PROP_FRAME_COUNT)
        
        time_per_frame = 1/fps
        print(frames)
        
        # output
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.outlet+'/result.mp4', fourcc, fps, (W, H))
        
        time = 0
        slices = []
        
        # Now we start
        while(cap.isOpened()):
            ret, frame = cap.read()
        
            cnt += 1 # Counting frames
        
            # Avoid problems when video finish
            if ret==True:
                time = time+time_per_frame
                printtime = str(datetime.timedelta(seconds=time))
                
                # Croping the frame
                #frame = self.hist_normalization(frame)
                frame = cv2.subtract(frame,self.back_to_sub)
                frame = cv2.warpPerspective(frame, self.homography, (self.width, self.height))
                crop_frame = frame[Y:Y+H, X:X+W]

                # Percentage
                xx = cnt *100/frames
                print((xx),'%')
        
                imageGREY = crop_frame.mean(axis=2)
                imageGREY = imageGREY.mean(axis=1)
                slices.append(imageGREY)
            
                # Saving from the desired frames
                font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
                crop_frame = cv2.putText(crop_frame, printtime,
                                    (10, 50),
                                    font, 1,
                                    (255, 255, 255), 
                                    2, cv2.LINE_8)
                
                # I see the answer now. Here you save all the video
                out.write(crop_frame)
            else:
                break
        
        sliced = np.stack(slices, axis=0)
        self.sliced = self.groupedAvg(sliced)
        np.savetxt(self.outlet+'/sliced.csv',self.sliced,delimiter=',')
        
        cap.release()
        out.release()
        
        
inlet = '/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Pipeline/Inlet/May 10'
outlet = '/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Pipeline/Outlet/May 10'       
        
pipeline=ResonatorPipeline(inlet, outlet)