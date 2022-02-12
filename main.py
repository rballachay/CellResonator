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
    prompt=False,
    help="Path to folder where videos + excel file are located",
)

def main(inlet):
    pipeline(inlet)


if __name__ == "__main__":
    main()
