# ASTM Grasp Strength Analysis
A library which allows users to analyze grasp strength trials performed in associated with the ASTM standard for robot grasp strength.

## Installation

* Clone this repository:

```
git clone https://github.com/usnistgov/astm_grasp_strength_analysis.git
cd astm_grasp_strength_analysis
```

* Create virtual environment for python

```
python -m venv .astm_grasp
source .astm_grasp/bin/activate
```

* Install required packages

```
sudo apt-get install python3-tk
pip install -r requirements.txt
```

* When running the code, ensure that the kernel being used in the jupyter notebook is the one that was created earlier (.astm_grasp)

## Running the code

* Two Jupyer notebooks have been provided which perform different functions in the grasp analysis. First grasp_strength_initialization.ipynb analyzes a trial based on the initialization specified in the ASTM standard. grasp_strength_analysis.ipynb analyzes any number of .csv files within a folder, where each file is an independent trial for grasp strength, with any number of recorded grasps.

** Test files have been provided to show how the code will work.

