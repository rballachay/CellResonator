#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 18:42:09 2021

@author: RileyBallachay
"""

from image_processing_pipeline import ResonatorPipeline
from histogram_pipeline import HistogramPipeline

def main(inlet):    
    outlet = "/".join(inlet.split("/")[:-2]) + "/Outlet/" + inlet.split("/")[-1]
            
    rpl=ResonatorPipeline(inlet, outlet)
    path_sliced=rpl.run()
    
    hpl=HistogramPipeline(path_sliced,inlet+'/cellcounts.csv')
    hpl.plot(title=inlet.split("/")[-1], save=True, path=outlet+'/results.png')
    

inlet_folder = '/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Pipeline_v2.0/Inlet/Nov10_conc'

main(inlet_folder)