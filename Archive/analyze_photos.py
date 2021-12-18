#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 15 14:07:48 2021

@author: RileyBallachay
"""
import cv2
import os
import time
import matplotlib.pyplot as plt
import scipy.ndimage

directory = 'data_subtracted'

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
means=[]
for (i,image) in enumerate(images[0:]):
    plt.figure()
    imageGREY = image.mean(axis=2)
    imageGREY = imageGREY.mean(axis=1)
    ax=plt.gca()
    ax.set_ylim([0,35])
    plt.plot(scipy.ndimage.gaussian_filter1d(imageGREY,sigma=2))
    means.append(sum(imageGREY[:100])/len(imageGREY[:100]))
    
plt.figure()
plt.set_ylim([0,35])
plt.plot(scipy.ndimage.gaussian_filter1d(means,sigma=2))