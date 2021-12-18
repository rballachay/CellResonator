#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 11 10:01:03 2021

@author: RileyBallachay
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import scipy.ndimage
import matplotlib.dates as mdates
from sklearn.preprocessing import MinMaxScaler
myFmt = mdates.DateFormatter('%m:%s')

def groupedAvg(myArray, N=10):
    result = np.cumsum(myArray, 0)[N-1::N]/float(N)
    result[1:] = result[1:] - result[:-1]
    return result

path = '/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Histogram_Slices/sliced_may5b.csv'
sliced = np.loadtxt(path,delimiter=',')

means=groupedAvg(sliced[:,:10].mean(axis=1))
#means = np.median(sliced[:,:50],axis=1)

time_per_frame = 0.033701279491161897*5*10
time = np.linspace(0,len(means),len(means))*time_per_frame

image_data = np.zeros((len(time),2))
image_data[:,0] = time
image_data[:,1] = means

txt = '/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Resonator Data/May5B.csv'
data = np.loadtxt(txt,delimiter=',', skiprows=1,usecols=(0,1))

ranger = list(range(22,45))
cellcount = np.loadtxt(txt,delimiter=',', skiprows=0,usecols=(2,3),max_rows=21)

data1 = data[:21] - 52
data2 = data[21:] - 52

data1[:,0] = data1[:,0] 
data2[:,0] = data2[:,0]

# create figure and axis objects with subplots()
fig,ax = plt.subplots(dpi=200)
fig.set_figheight(5)
fig.set_figwidth(10)
#fig.set_figdpi(200)
# make a plot
scaler = MinMaxScaler()

x_data = time[250:950]/60

ax.plot(x_data,scaler.fit_transform(scipy.ndimage.gaussian_filter1d(means[250:950],sigma=5).reshape(-1,1)),'maroon')
#ax.plot(time[1000:1800]/60,scaler.fit_transform(scipy.ndimage.gaussian_filter1d(means[1000:1800],sigma=1).reshape(-1,1)),'maroon')
fig.autofmt_xdate()
# set x-axis label
ax.set_xlabel("Run Duration ")
ax.set_title("June 4th Concentration and Washing")
# set y-axis label
ax.set_ylabel("Average Brightness at Top of Frame",color="maroon",fontsize=10)

# twin object for two different y-axis on the sample plot
ax2=ax.twinx()
# make a plot with different y-axis using second axis object
#ax2.plot(data1[:,0]/60,scaler.fit_transform(data1[:,1].reshape(-1,1)),'grey',label='Concentration')
#ax2.plot(data2[:,0]/60,scaler.fit_transform(data2[:,1].reshape(-1,1)),'darkblue',label='Washing')
#ax2.set_ylabel("Measured Signal Downstream",color="darkblue",fontsize=10)

ax2.plot((cellcount[:11,0])/60,scaler.fit_transform(cellcount[:11,1].reshape(-1,1)),'k.',label='Concentration Cell Count')
#ax2.plot((cellcount[11:,0])/60,scaler.fit_transform(cellcount[11:,1].reshape(-1,1)),'c.',label='Washing Cell Count')
handles, labels = ax2.get_legend_handles_labels()
fig.legend(handles, labels,loc=(0.75,0.75))

#gauss_kernels = np.arange(10,100,1)
#delays = np.arange(10,100,1)
gauss_kernels = [42]
delays = [12]

y= scaler.fit_transform(cellcount[:11,1].reshape(-1,1)).reshape(-1)
conc_model = np.poly1d(np.polyfit(cellcount[:11,0]/60,y,7))
ax2.plot(x_data,conc_model(x_data),'k',label='Concentration Cell Count')

RMSE = np.zeros((len(delays),len(gauss_kernels)))
for (i,delay) in enumerate(delays):
    for (j,gauss) in enumerate(gauss_kernels):
        delay = delay
        min_time = 416
        max_time = 1616
        scaler = MinMaxScaler()
        start = np.argmax(image_data[:,0]>min_time-delay)
        stop = np.argmax(image_data[:,0]>max_time-delay)
        time_data = image_data[start:stop,0]/60
        plot_data = scaler.fit_transform(scipy.ndimage.gaussian_filter1d(image_data[:,1],sigma=gauss)[start:stop].reshape(-1,1))
        
        time_data_reverted = [time+delay/60 for time in time_data]
        
        fig,ax = plt.subplots(dpi=200)
        fig.set_figheight(5)
        fig.set_figwidth(10)
        ax.plot(time_data_reverted,plot_data,'maroon')
        ax.set_xlabel("Run Duration ")
        ax.set_title("June 4th Concentration and Washing")
        # set y-axis label
        ax.set_ylabel("Average Brightness at Top of Frame",color="maroon",fontsize=10)
        
        # twin object for two different y-axis on the sample plot
        ax2=ax.twinx()
        ax2.plot(time_data_reverted,conc_model(time_data_reverted),'k',label='Concentration Cell Count')
        handles, labels = ax2.get_legend_handles_labels()
        fig.legend(handles, labels,loc=(0.75,0.75))
        
        data_2 = conc_model(time_data_reverted)
        data_1 = plot_data.flatten()
        returnval = ((data_1-data_2)**2).mean()

        RMSE[i,j] = returnval
        

X, Y = np.meshgrid(gauss_kernels[1:],delays[1:])
Z = RMSE[1:,1:]
plt.figure()

fig = plt.figure(dpi=200)
ax1 = fig.add_subplot(111, projection='3d')
ax1.plot_surface(X, Y, Z, alpha=0.9,cmap='viridis')
index1,index2 = np.unravel_index(Z.argmin(), Z.shape)
print(gauss_kernels[index2])
print(delays[index1])
index3 = Z[index1,index2]
ax1.scatter3D(gauss_kernels[index2],delays[index1],index3,'k',s=50)

plt.show() 
        