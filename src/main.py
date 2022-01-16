#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 18:42:09 2021

@author: RileyBallachay
"""
import click
from src.image_processing_pipeline import ResonatorPipeline
from src.histogram_pipeline import HistogramPipeline
from .utils import process_config

@click.command()

@click.option(
    "--i",
    "inlet",
    prompt=True,
    help="Path to folder where videos + excel file are located"
)

@click.option(
    "--f",
    "file_num",
    prompt=False,
    default="2",
    help="1: conc+wash in one video, 2: conc+wash in separate videos"
)


def main(inlet, file_num): 
    
    data_items = process_config(inlet, file_num)

    for title in data_items:
        outlet = "/".join(inlet.split("/")[:-2]) + "/Outlet/" + inlet.split("/")[-1]
                
        rpl=ResonatorPipeline(inlet, outlet)
        path_sliced=rpl.run()
        
        hpl=HistogramPipeline(path_sliced,inlet+'/cellcounts.csv')
        hpl.plot(title=inlet.split("/")[-1], save=True, path=outlet+'/results.png')
    

inlet_folder = '/Users/RileyBallachay/Documents/Fifth Year/Work for Dr.Piret/Pipeline_v2.0/Inlet/Nov10_conc'

main(inlet_folder)
