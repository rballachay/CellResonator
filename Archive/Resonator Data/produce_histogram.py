#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 24 16:09:10 2021

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

path = '/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Histogram Slices/sliced_may10.csv'
sliced = np.loadtxt(path,delimiter=',')

means=sliced[:,:10].mean(axis=1)[::10]

time_per_frame = 0.033701279491161897*5*10
time = np.linspace(0,len(means),len(means))*time_per_frame

path2 = '/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Resonator Data/May10_2021.csv'
data = np.loadtxt(path2,delimiter=',', skiprows=1,usecols=(0,1))

ranger = list(range(22,45))
cellcount = np.loadtxt('May10_2021.csv',delimiter=',', skiprows=0,usecols=(2,3),max_rows=21)

data1 = data[:23]
data2 = data[23:]

data1[:,0] = data1[:,0] - 52
data2[:,0] = data2[:,0] - 52

# create figure and axis objects with subplots()
fig,ax = plt.subplots(dpi=200)
fig.set_figheight(5)
fig.set_figwidth(10)
#fig.set_figdpi(200)
# make a plot
scaler = MinMaxScaler()
ax.plot(time[450:1200]/60,scaler.fit_transform(scipy.ndimage.gaussian_filter1d(means[450:1200],sigma=50).reshape(-1,1)),'maroon')
ax.plot(time[1200:]/60,scaler.fit_transform(scipy.ndimage.gaussian_filter1d(means[1200:],sigma=50).reshape(-1,1)),'maroon')

fig.autofmt_xdate()
# set x-axis label
ax.set_xlabel("Run Duration ")
ax.set_title("May 10th Concentration and Washing")
# set y-axis label
ax.set_ylabel("Average Brightness at Top of Frame",color="maroon",fontsize=10)

# twin object for two different y-axis on the sample plot
ax2=ax.twinx()
# make a plot with different y-axis using second axis object
ax2.plot(data1[:,0]/60,scaler.fit_transform(data1[:,1].reshape(-1,1)),'grey',label='Concentration')
ax2.plot(data2[:,0]/60,scaler.fit_transform(data2[:,1].reshape(-1,1)),'darkblue',label='Washing')
ax2.set_ylabel("Measured Signal Downstream",color="darkblue",fontsize=10)
handles, labels = ax2.get_legend_handles_labels()
fig.legend(handles, labels,loc=(0.75,0.75))

ax2.plot((cellcount[:11,0]-52)/60,scaler.fit_transform(cellcount[:11,1].reshape(-1,1)),'k.',label='Concentration Cell Count')
ax2.plot((cellcount[11:,0]-52)/60,scaler.fit_transform(cellcount[11:,1].reshape(-1,1)),'c.',label='Washing Cell Count')
handles, labels = ax2.get_legend_handles_labels()
fig.legend(handles, labels,loc=(0.75,0.75))

'''
concentration = np.polyfit(data1[:,0]/60, scaler.fit_transform(data1[:,1].reshape(-1,1)).reshape(-1), 8)
conc_poly = np.poly1d(concentration)

wash = np.polyfit(data2[:,0]/60, scaler.fit_transform(data2[:,1].reshape(-1,1)).reshape(-1), 8)
wash_poly = np.poly1d(wash)

ax2.plot(time[450:1200]/60,conc_poly(time[450:1200]/60),'green')
ax2.plot(time[1400:2150]/60,wash_poly(time[1400:2150]/60),'green',label='Regression')
handles, labels = ax2.get_legend_handles_labels()
fig.legend(handles, labels,loc=(0.75,0.75))
plt.show()

x= conc_poly(time[450:1200]/60)
y = scaler.fit_transform(scipy.ndimage.gaussian_filter1d(means[450:1200],sigma=50).reshape(-1,1)).reshape(-1)
sns.regplot(x=x,y=y)
plt.show()

x= wash_poly(time[1400:2150]/60)
y = scaler.fit_transform(scipy.ndimage.gaussian_filter1d(means[1400:2150],sigma=50).reshape(-1,1)).reshape(-1)
sns.regplot(x=x,y=y)
plt.show()

np.savetxt('NN Training Data/May_10_x.csv',np.concatenate((sliced[450:1200,:10],sliced[1400:2150,:10])),delimiter=',')
np.savetxt('NN Training Data/May_10_y.csv',np.concatenate((conc_poly(time[450:1200]/60),wash_poly(time[1400:2150]/60))),delimiter=',')
'''