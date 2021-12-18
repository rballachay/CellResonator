#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 18 20:56:55 2021

@author: RileyBallachay
"""
import numpy as np
import cv2
import matplotlib.pyplot as plt
from sklearn.decomposition import KernelPCA
from sklearn.preprocessing import StandardScaler
import scipy.misc
import scipy
from PIL import Image
import datetime

# Here you can define your croping values
x = 366; y= 104; w=273; h= 521

# Initialize frame counter
cnt = 0
cap = cv2.VideoCapture('/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Cropped_vid.mp4')
# Some characteristics from the original video
w_frame, h_frame = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps, frames = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

time_per_frame = 1/fps
print(frames)

time = 0
i=0
slices = []
imageList = []
# Now we start
images = np.zeros((int(frames/10),2500))
while(cap.isOpened()):
    ret, frame = cap.read()

    cnt += 1 # Counting frames

    # Avoid problems when video finish
    if ret==True:
        if cnt%10==0:
            # Percentage
            xx = cnt *100/frames
            print((xx),'%')
            frame=frame[:100,...]
            frame = frame.mean(axis=2)
            img = cv2.resize(frame,(50,50))
            img = img.flatten()
            images[i]=img
            i+=1
    else:
        break

scaler = StandardScaler()
images = scaler.fit_transform(images)
n_components = 1
pca = KernelPCA(n_components=n_components,kernel='rbf',fit_inverse_transform=True)
out = pca.fit_transform(images)

out1 = scipy.ndimage.gaussian_filter1d(out[:,0],sigma=100)
#out2 = scipy.ndimage.gaussian_filter1d(out[:,1],sigma=10)
plt.figure(dpi=200)
plt.xlabel('Time (s)')
plt.ylabel('Principal Component')
plt.plot(-out1)
#plt.plot(out2)

restored = pca.inverse_transform(out)
fig = plt.figure()
ax = plt.Axes(fig, [0., 0., 1., 1.])
ax.set_axis_off()
fig.add_axes(ax)   
ax.imshow(restored[1000].reshape((50,50)),cmap='gray')
#plt.imshow(restored[700].reshape((50,50)))

fig2 = plt.figure()
ax2 = plt.Axes(fig2, [0., 0., 1., 1.])
ax2.set_axis_off()
fig2.add_axes(ax2)   
ax2.imshow(restored[3000].reshape((50,50)),cmap='gray')

fig3 = plt.figure()
ax3 = plt.Axes(fig3, [0., 0., 1., 1.])
ax3.set_axis_off()
fig3.add_axes(ax3)   
ax3.imshow(restored[8000].reshape((50,50)),cmap='gray')


#np.savetxt('PCA_compressed.csv',pca_rep,delimiter=',')
cap.release()

