# ASTM Grasp Strength Analysis
A library which allows users to analyze grasp strength trials performed in association with the ASTM standard for robot grasp strength.

## Installation

* Clone this repository:

```
git clone https://github.com/usnistgov/astm_grasp_strength_analysis.git
cd astm_grasp_strength_analysis
```

* Create virtual environment for python and install required packages (Linux)

```
python -m venv .astm_grasp
source .astm_grasp/bin/activate
sudo apt-get install python3-tk
pip install -r requirements.txt
```

* Create virtual environment for python and install required packages (Windows)

```
python -m venv .astm_grasp
.astm_grasp\Scripts\activate
pip install tk
pip install -r requirements.txt
```

* When running the code, ensure that the kernel being used in the jupyter notebook is the one that was created earlier (.astm_grasp)

## Models

The models folder holds the dataclasses used to present data in the jupyter notebooks:

* grasp_analysis_results.py -> contains a data class that is used to hold the results of the grasp analysis process
* grasp_region.py -> contains a data class the is used to contain information for a single grasp
* initialization_angle.py -> contains a data class that is used to hold information related to results of the grasp initialization process

## Provided Data

The sample_data folder contains two files with example data:

* robotiq_cylinder/RobotIQ_60SFMA_50Cycles_Cyl.csv -> a csv file containing 3 columns of data, each column corresponding to to one of the force sensors in the SFMA. This data includes 50 grasps in a single trial. Units for this data are in Newtons.
* robotiq_initialization/RobotIQ_70SFMA_33Cycles_DeterminePositionMaxGraspStrength.csv -> a csv file containing 3 columns of data, each column corresponding to one of the force sensors in the SFMA. The data is captured where 3 grasps are recorded at each angle increment. Units for this data are in Newtons.


## Running the code

* Two Jupyer notebooks have been provided which perform different functions in the grasp analysis. First, initialization.ipynb analyzes a trial (single csv file) based on the initialization specified in the ASTM standard. Second, analysis.ipynb analyzes any number of .csv files within a directory, where each file is an independent trial (single csv file) for grasp strength, with any number of recorded grasps.

** Test files have been provided to show how the code will work.

## Uncertainty

The software employs deterministic algorithms; as such, it does not introduce independent measurement uncertainty. The uncertainty of the outputs is derived entirely from the uncertainty of the input data provided by the user.

## NIST Software Disclaimer

NIST-developed software is provided by NIST as a public service. You may use, copy, and distribute copies of the software in any medium, provided that you keep intact this entire notice. You may improve, modify, and create derivative works of the software or any portion of the software, and you may copy and distribute such modifications or works. Modified works should carry a notice stating that you changed the software and should note the date and nature of any such change. Please explicitly acknowledge the National Institute of Standards and Technology as the source of the software. 

NIST-developed software is expressly provided "AS IS." NIST MAKES NO WARRANTY OF ANY KIND, EXPRESS, IMPLIED, IN FACT, OR ARISING BY OPERATION OF LAW, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT, AND DATA ACCURACY. NIST NEITHER REPRESENTS NOR WARRANTS THAT THE OPERATION OF THE SOFTWARE WILL BE UNINTERRUPTED OR ERROR-FREE, OR THAT ANY DEFECTS WILL BE CORRECTED. NIST DOES NOT WARRANT OR MAKE ANY REPRESENTATIONS REGARDING THE USE OF THE SOFTWARE OR THE RESULTS THEREOF, INCLUDING BUT NOT LIMITED TO THE CORRECTNESS, ACCURACY, RELIABILITY, OR USEFULNESS OF THE SOFTWARE.

You are solely responsible for determining the appropriateness of using and distributing the software and you assume all risks associated with its use, including but not limited to the risks and costs of program errors, compliance with applicable laws, damage to or loss of data, programs or equipment, and the unavailability or interruption of operation. This software is not intended to be used in any situation where a failure could cause risk of injury or damage to property. The software developed by NIST employees is not subject to copyright protection within the United States.

## Product Disclaimer

Certain equipment, instruments, software, or materials are identified in this software publication in order to specify the software adequately.  Such identification is not intended to imply recommendation or endorsement of any product or service by NIST, nor is it intended to imply that the materials or equipment identified are necessarily the best available for the purpose.


