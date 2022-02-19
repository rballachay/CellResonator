#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 18:42:09 2021

@author: RileyBallachay
"""
import click

from src.pipeline import pipeline
from src.workflows import workflow1

FN_MAP = {
    "default": pipeline,
    "workflow1": workflow1,
}


@click.command()
@click.option(
    "-i",
    "inlet",
    prompt=False,
    help="Path to folder where videos + excel file are located",
)
@click.option(
    "-t",
    "type",
    type=click.Choice(["default", "workflow1"], case_sensitive=False),
    prompt=False,
    help="""Analysis type: 
            default for default (analyze concentration and washing), 
            workflow1 for running brightness on whole video and outputting xlsx""",
)
def main(inlet, type):
    FN_MAP.get(type, pipeline)(inlet)


if __name__ == "__main__":
    main()
