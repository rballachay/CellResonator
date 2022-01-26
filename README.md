# Cell Resonator

## Overview

This repo uses image analyis to predict cell losses in the top of a cell resonator (a device which uses acoustic waves to capture cells so that they may be washed). The average brightness at the top of the resonator (~top 50 pixels) is used to indicate the number of cells passing through the region, and thus, indicate the cell loss. A sample of the resonator footage used to predict cell losses is demonstrated below.

![](docs/gifs/restonator.gif "Τhe Cell Resonator")


Each time the camera is positioned relative to the resonator, the exact pixel coordiantes of the top of the resonator changes, thus the images need to be calibrated. ORB (Oriented FAST and Rotated BRIEF) features are detected in the target and a reference video of the resonator, the homography is calculated and the target video is warped frame-by-frame to match the coordinates of the first video. The ORB feature matches between a reference and target video are shown below: 

![](docs/images/matches.jpg "ORB feature matching")

Once the videos are matches, the average resonator intensity is extracted as a csv file and the histograms are plotted alongside the ground-truth data extracted from downstream live cell counts and a resistance sensor. An example of the pipeline's output is shown below:

![](docs/images/results.png "Conc") 

## Usage

1. Move the following files in a single folder:

* Excel sheet from template described in docs
* Videos (any of the following)
    * 1 conc / wash video
    * Total video (conc + wash in 1 video) 
    * 2 videos, conc and wash

2. Install requirements from terminal/command line using

```bash
pip install -r requirements.txt
```

(make sure you are inside the CellResonator directory when doing this)

3. Run the package from terminal/command line using

```bash
python -m main -i "path/to/folder/with/data"
```

The script will run and produce the histograms indicated above


## Dependencies

Cell Resonator requires:

### Environment
* os -> mac, windows, linux
* python > 3.8.3
* pip > 21.3.1

### Packages
* pandas==1.0.5
* seaborn==0.11.1
* scipy==1.4.1
* numpy==1.19.5
* matplotlib==3.2.2
* opencv_python==4.5.1.48
* moviepy==1.0.3
* python-dotenv==0.19.2
* scikit_learn==1.0.2
* click==8.0.3

Install requirements using:
```bash
pip install -r requirements.txt
```

## Testing

Testing is done using python package pytest. In order to test, need to be on mac and run the following:
```bash
pip install pytest

pytest tests
```

## Help/Troubleshooting

For more information, or to report a bug, email developer at riley.ballachay@gmail.com
