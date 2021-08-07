#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  5 23:07:32 2021

@author: RileyBallachay
"""
import numpy as np
import os
import glob
from keras.models import Sequential
from keras.layers import Dense
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
scaler=MinMaxScaler()

path = '/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Resonator Data/NN Training Data/'
extension = 'csv'
os.chdir(path)
result = glob.glob('*.{}'.format(extension))

x_files = [file for file in result if '_x' in file]
y_files = [file for file in result if '_y' in file]

x_data = np.loadtxt(path+x_files[0],delimiter=',')[np.r_[200:1000,1150:1800],:12500]
y_data = np.loadtxt(path+y_files[0],delimiter=',')

for i in range(1,len(x_files)):
    if i==1:
        x_temp = np.loadtxt(path+x_files[i],delimiter=',')[np.r_[400:1050,1250:1950],:12500]
    else:
        x_temp = np.loadtxt(path+x_files[i],delimiter=',')[np.r_[450:1200,1400:2150],:12500]
    x_data = np.concatenate((x_data,x_temp))
    print(i)
    y_temp = np.loadtxt(path+y_files[i],delimiter=',')
    y_data = np.concatenate((y_data,y_temp))
    print(i)
    
x_data = scaler.fit_transform(x_data)

model = Sequential()
model.add(Dense(10, input_dim=12500, activation='linear'))
model.add(Dense(10, activation='linear'))
model.add(Dense(1, activation='linear'))

model.compile(loss='mse', optimizer='adam', metrics=['accuracy'])

model.fit(x_data[:2800], y_data[:2800], epochs=100, batch_size=100) 
y_out = model.predict(x_data[2800:])
plt.plot(y_out,y_data[2800:],'.')
x1,x2,y1,y2 = plt.axis()  
plt.axis((0,1.2,0,1.2))