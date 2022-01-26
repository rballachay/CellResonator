#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 18:42:09 2021

@author: RileyBallachay
"""
import click

from src.pipeline import pipeline


@click.command()
@click.option(
    "-i",
    "inlet",
    prompt=True,
    help="Path to folder where videos + excel file are located",
)
@click.option(
    "-f",
    "file_num",
    prompt=False,
    default="2",
    help="1: conc+wash in one video, 2: conc+wash in separate videos",
)
def main(inlet, file_num):
    pipeline(inlet, file_num)


if __name__ == "__main__":
    main()
