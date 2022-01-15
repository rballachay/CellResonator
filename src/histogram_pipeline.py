#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 24 16:09:10 2021

@author: RileyBallachay
"""
import bisect
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import scipy.ndimage
import matplotlib.dates as mdates
from sklearn.preprocessing import MinMaxScaler

TIME_PER_FRAME = 0.033701279491161897
SLICE_FREQUENCY = 5

class HistogramPipeline:
    
    def __init__(self, path_sliced:str, path_cell_count:str, window:tuple=(0,50), time_correction:int=50):
        self.time_correction=time_correction
        self.brightness = self._read_sliced(path_sliced, window)
        self.cellcount = self._read_cellcount(path_cell_count, time_correction)
        self._fix_bounds()
        self._time_correct()
        
    def plot(self,title:str, save:bool=False, path:str='results.png'):
        brightness=self.brightness
        cellcount=self.cellcount
        fig,ax,ax2 = self._make_fig(title)
        scaler = MinMaxScaler()
        ax.plot(brightness[:,0],scaler.fit_transform(scipy.ndimage.gaussian_filter1d(brightness[:,1],sigma=40).reshape(-1,1)),'maroon',label='Predicted Cell Loss')
        ax2.plot(cellcount[:,0],cellcount[:,1].reshape(-1,1),'k.',label='Downstream Cell Count') 
        handles, labels = ax2.get_legend_handles_labels()
        fig.legend(handles, labels,loc=(0.65,0.8))
        
        if save:
            self._save_fig(fig,path)
            
    def _save_fig(self,fig,path):
        fig.savefig(path)
        
    def _make_fig(self,title):
        fig,ax = plt.subplots(dpi=200)
        fig.set_figheight(5)
        fig.set_figwidth(10)
        fig.autofmt_xdate()
        ax.set_xlabel("Run Duration (minutes)")
        ax.set_title(title)
        ax.set_ylabel("Average Brightness at Top of Frame",color="maroon",fontsize=10)
        ax2=ax.twinx()
        ax2.set_ylabel("Downstream Cell Count",color="black",fontsize=10)
        return fig,ax,ax2

    def _fix_bounds(self):
        cellcount = self.cellcount
        brightness = self.brightness
        t_min = cellcount[0,0]
        t_max = cellcount[-1,0]
        min_bright = bisect.bisect(brightness[:,0], t_min) 
        max_bright = bisect.bisect(brightness[:,0], t_max) 
        
        self.brightness = brightness[min_bright:max_bright]
        
    def _time_correct(self):
        cellcount = self.cellcount
        brightness = self.brightness
        cellcount[:,0] = (cellcount[:,0]) / 60
        brightness[:,0] = brightness[:,0] / 60
        self.brightness=brightness
        self.cellcount=cellcount
        
    def _read_sliced(self,path_sliced:str,window:tuple,avg_window:int=5):
        sliced = np.loadtxt(path_sliced,delimiter=',')
        means = sliced[:, window[0]:window[1]].mean(axis=1)[::avg_window]
        time_per_frame = TIME_PER_FRAME*SLICE_FREQUENCY*avg_window
        time = np.linspace(0,len(means),len(means))*time_per_frame
        brightness = np.stack((time,means),axis=1)
        return brightness
    
    def _read_cellcount(self,path_cell_count:str,time_correction:int):
        cellcount = np.array(pd.read_csv(path_cell_count,header=None))
        cellcount[:,0] = cellcount[:,0] - time_correction
        cellcount = np.array(cellcount)
        return cellcount


if __name__=="__main__":
    path1 = '/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Resonator Data/sliced_aug30_conc.csv'
    path2 = '/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Resonator Data/Aug30_conc.csv'
    htp = HistogramPipeline(path1,path2)
    htp.plot(title="August 30th Concentration", save=True)


