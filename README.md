# Eve: 3D animation Houdini pipeline

## Introduction
"Eve" is an **out of the box VFX pipeline** for a single artist or animation studio using Houdini application. 
It is full CG oriented pipeline which can handle small tasks with just a few shots as well as huge projects like animation feature or TV series.

This repository is a clean version of early created [Houdini](https://github.com/kiryha/Houdini) pipeline.

#### Documentation
Refer to [Eve wiki](https://github.com/kiryha/Houdini/wiki) for more info about pipeline usage and some fancy tutorials!

## Requirements and Installation
Currently, Eve designed to be run on Windows OS. 
Here is the list of things you need to have before Eve pipeline will works:

- Houdini  
- Python 2.7.5 x 64 (or later version) 
- pip  
- PySide

#### Install Houdini
Go to [SESI site](https://www.sidefx.com/products/compare/), choose, download and install your Houdini version.

#### Install Python
Get your [X64 Python 2.7.5](https://www.python.org/downloads/release/python-275/)

#### Install pip
To install PIP do the folowing:
* Download [get-pip.py](https://bootstrap.pypa.io/get-pip.py), place in Python folder, e.g `C:/Python27/` 
* Run cmd in `C:/Python27` folder and execute: `python get-pip.py`  
* Add pip path to a system environment variables: `PATH = c:/Python27/scripts`  

#### Install Pyside
Run cmd and exequte: `pip install PySide`

#### Install Github Desktop
Install [Github Desktop](https://electronjs.org/apps/github-desktop) and clone this repo to the local drive, 
where you supposing to keep Eve pipeline.

[![](https://live.staticflickr.com/65535/48019681856_fd0a55facb_o.gif)](https://live.staticflickr.com/65535/48019681856_fd0a55facb_o.gif)


## Usage
Go to Eve local folder on your HDD and run Project Manager tool with `projectManager.bat`

[![](https://live.staticflickr.com/65535/48019770601_10f9642217_o.gif)](https://live.staticflickr.com/65535/48019770601_10f9642217_o.gif)

Select location of your project on hard drive, enter project name and Houdini build number and press "Create Project" button.
Go to `<projectLocation>/PREP/PIPELINE/`, run Houdini with `runHoudini.bat` and do your CGI magic! 