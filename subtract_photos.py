#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 15 12:23:00 2021

@author: RileyBallachay
"""
import cv2
import os
import time

directory = 'data'

def load_images_from_folder(folder):
    images = []
    filenames = []
    dirlist = sorted(os.listdir(folder))
    for filename in dirlist:
        print(filename)
        img = cv2.imread(os.path.join(folder,filename))
        print(img)
        if img is not None:
            images.append(img)
            filenames.append(filename)
    return images,filenames


images,filenames = load_images_from_folder(directory)
images_subtracted = []
images_subtracted.append(images[0])
name = 'data_subtracted/'+filenames[0]
temp = images[0]
cv2.imwrite(name,temp)

for (i,image) in enumerate(images[1:]):
    name = 'data_subtracted/'+filenames[i]
    temp = cv2.subtract(image,images[0])
    x=387;y=105;w=238;h=482
    temp = temp[y:y+h,x:x+w]
    cv2.imwrite(name,temp)


