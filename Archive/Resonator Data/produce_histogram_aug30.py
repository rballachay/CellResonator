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

path = '/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Resonator Data/sliced_aug30_conc.csv'
sliced = np.loadtxt(path,delimiter=',')

means=sliced[:,25:75].mean(axis=1)[::5]
#means = np.median(sliced[:,:50],axis=1)

time_per_frame = 0.033701279491161897*5*5
time = np.linspace(0,len(means),len(means))*time_per_frame

txt = '/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Resonator Data/Aug30_conc.csv'
cellcount = pd.read_csv(txt,header=None)
cellcount = np.array(cellcount)


# create figure and axis objects with subplots()
fig,ax = plt.subplots(dpi=200)
fig.set_figheight(5)
fig.set_figwidth(10)
#fig.set_figdpi(200)
# make a plot
scaler = MinMaxScaler()
ax.plot((time[125:(850*5-2650)])/60,scaler.fit_transform(scipy.ndimage.gaussian_filter1d(means[125:(850*5-2650)],sigma=40).reshape(-1,1)),'maroon',label='Predicted Cell Loss')
fig.autofmt_xdate()
# set x-axis label
ax.set_xlabel("Run Duration ")
ax.set_title("August 30th Washing")
# set y-axis label
ax.set_ylabel("Average Brightness at Top of Frame",color="maroon",fontsize=10)

# twin object for two different y-axis on the sample plot
ax2=ax.twinx()
# make a plot with different y-axis using second axis object
ax2.set_ylabel("Downstream Cell Count",color="darkblue",fontsize=10)

ax2.plot((cellcount[:,0]-50)/60,cellcount[:,1].reshape(-1,1),'k.',label='Downstream Cell Count')
handles, labels = ax2.get_legend_handles_labels()
fig.legend(handles, labels,loc=(0.65,0.8))

handles, labels = ax.get_legend_handles_labels()