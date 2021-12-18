#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 17:27:42 2021

@author: RileyBallachay
"""
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Pipeline_v2.0/Outlet/Oct_26_specks/specks.csv')
df_frame = df.groupby('frame').sum()

count = df.groupby('frame').count()['area']
df_frame["count"] = count
df_frame["time [s]"] = df_frame.index * 1/30

sns.set()
fig, ax1 = plt.subplots(dpi=200)
ax2 = ax1.twinx()
ax1.grid(False)
ax2.grid(False)
plt.figure(dpi=200)
ax1.plot(df_frame["time [s]"],df_frame["count"],'darkgreen',label='Count (objects)')
ax2.plot(df_frame["time [s]"],df_frame["area"],'darkred',label='Area (pixels)')

ax1.set_xlabel('Time into Run (s)')
ax1.set_ylabel('Count of Specks', color='darkgreen')
ax2.set_ylabel('Total Speck Area', color='darkred')
