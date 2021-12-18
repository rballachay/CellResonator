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
from sklearn.metrics import mean_squared_error
import scipy.ndimage
import matplotlib.dates as mdates
from sklearn.preprocessing import MinMaxScaler
from numpy.polynomial import Polynomial

myFmt = mdates.DateFormatter('%m:%s')

path = '/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/sliced_sep17_conc.csv'
sliced = np.loadtxt(path,delimiter=',')

means=sliced[:,25:50].mean(axis=1)[::5]
#means = np.median(sliced[:,:50],axis=1)

time_per_frame = 0.033701279491161897*5*5
time = np.linspace(0,len(means),len(means))*time_per_frame

txt = '/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Resonator Data/Sep17_conc.csv'
cellcount = pd.read_csv(txt,header=None)
cellcount = np.array(cellcount)


# create figure and axis objects with subplots()
fig,ax = plt.subplots(dpi=200)
fig.set_figheight(5)
fig.set_figwidth(10)
#fig.set_figdpi(200)
# make a plot
scaler = MinMaxScaler()
ax.plot((time[150:1600])/60,scaler.fit_transform(scipy.ndimage.gaussian_filter1d(means[150:1600],sigma=40).reshape(-1,1)),'maroon',label='Predicted Cell Loss')
fig.autofmt_xdate()
# set x-axis label
ax.set_xlabel("Run Duration ")
ax.set_title("September 17th Concentration")
# set y-axis label
ax.set_ylabel("Average Brightness at Top of Frame",color="maroon",fontsize=10)
ax.grid(False)
# twin object for two different y-axis on the sample plot
ax2=ax.twinx()
# make a plot with different y-axis using second axis object
ax2.set_ylabel("Downstream Cell Count",color="darkblue",fontsize=10)
ax2.grid(False)

ax2.plot((cellcount[:,0]-40)/60,cellcount[:,1].reshape(-1,1),'k.',label='Downstream Cell Count')
"""
x=(cellcount[:,0]-40)/60
y=scaler.fit_transform(cellcount[:,1].reshape(-1,1)).reshape(-1)
p = Polynomial.fit(x,y, 4)
MSE = mean_squared_error(p(time[10:580]/60),scaler.fit_transform(scipy.ndimage.gaussian_filter1d(means[10:580],sigma=40).reshape(-1,1)),squared=False)
ax2.plot(time[10:580]/60,p(time[10:580]/60),label='RMSE = %.2f'%MSE)

handles, labels = ax2.get_legend_handles_labels()
fig.legend(handles, labels,loc=(0.65,0.2))
"""

