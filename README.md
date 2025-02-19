# pybimscantools

A python package for automated data acquisition pipeline.
This package has been slightly modified from the version utilized by HumanTech project to generalize the use of the software.

------------------------------------------------------------------------

** Notice for python swissreframe package
In order to use swissreframe package, JAVA is required on your system. Please follow the instructions below before installing the environment.

## Python swissreframe

### Windows

In windows you need to set an environment variable called **JAVA_HOME** to a 64 bit version of Java. You need to install `Java` if it is not already installed.

| Description    | Value                                  |
|----------------|----------------------------------------|
 Variable name  | **JAVA_HOME**                          
 Variable value | ``C:\Program Files\Java\jre1.8.0_291``


### Linux

To install Java follow this link: https://www.java.com/en/download/help/linux_x64_install.html#install


```
nano ~/.bashrc
export JAVA_HOME=/usr/java/jre1.8.0_421
export PATH=$JAVA_HOME/bin:$PATH
```

```
source ~/.bashrc
```

Test the java installation:

```
java -version
```
------------------------------------------------------------------------


## Installation of environment

You can create an environment for this software through either `miniforge for conda` or using `virtual environment` from python.

### 1. Using miniforge for conda

#### Installing miniforge for conda

1. Install miniforge (conda and mamba) from https://github.com/conda-forge/miniforge.

2. Run the Miniforge installation.

3. Update and init conda:

```
conda update -n base conda
conda init
```

#### Packaging with Conda and ``humantech_windows.yaml`` on Windows

Create a new environment from the ``dependencies\humantech_windows.yaml`` file:

```
conda env create -n humantech -f dependencies\humantech_windows.yaml
conda activate humantech
```

Creating a new environment ***humantech***, installing required packages and using Python 3.10.14:

```
conda create -n humantech requests urllib3 numpy jpype1 matplotlib scipy termcolor pandas pyquaternion simplekml openpyxl Flask piexif laspy ifcopenshell shapely alphashape lark python=3.10.14
```

Activating the environment.

```
conda activate humantech
```

#### The packages that are not available via conda need to be installed via pip

Use the miniforge3 prompt. (make shure ``humantech`` is activated)

On windows:

```
C:\Users\miche\miniforge3\envs\humantech\Scripts\pip install open3d swissreframe
```

On linux:
```
/home/pichim/miniforge3/envs/humantech/bin/pip install open3d swissreframe
```

You can use ``pip --version`` to locate pip within the ``humantech`` environment.

Updating all packages and dependencies:

```
conda update --all
```

List all packages installed in the environment:

```
conda list
```

### OR
### 2. Using virtual environment from python (venv)

Creating a virtual environment in the project folder:

```
python.exe -m venv venv
``` 

Activate the virtual environment:

```
cd venv/Scripts/
activate
```

Update `pip`:

```
python.exe -m pip install --upgrade pip
```

Make sure you have `setuptools` and `wheel` installed on your system:

```
python.exe -m pip install setuptools wheel
```

Update `setuptools` and `wheel`:

```
python.exe -m pip install --upgrade setuptools wheel
```

#### Required Packages

There are 2 options for installing the required packages. You can `install the pybimscantools package directly from the pypi server` or `package the pybimscantools as a package yourself and install its wheel`.

##### 2.1 Installing pybimscantools directly from pypi server

```
python.exe -m pip install pybimscantools
```

##### OR
##### 2.2 Packaging the pybimscantools as a package and install its wheel

Since all these files `requirements.txt` `setup.py` `MANIFEST.in` `pyproject.toml` required for packaging a wheel are provided, you can package pybimscantools by running below command in the project folder `pybimscantools`.

```
python.exe setup.py sdist bdist_wheel
```

This will create a `dist/` folder containing a `.whl` file and a `.tar.gz` source distribution.

Install the wheel using pip:

```
python.exe -m pip install dist/pybimscantools-0.1-py3-none-any.whl
```
------------------------------------------------------------------------

## How to use

Once you have set up the environment ready for the software, there are some requirements below in order to use `pybimscantools` at its fully functioning state. After that, you can follow the steps in `test.py`.

### Data

There is provided data available for download at: https://drive.google.com/file/d/1X82WFLAPbr41ybdGQwJHutIHWmgMMlVG/view?usp=sharing.
This provided data is processed by `pybimscantools` as an example to demonstrate automated data acquisition and its pre-processing pipeline. The users are required to change data in order to perform automated data acquisition and its related pre-processing tasks of their projects.

### Folder Structure

Make sure that the downloaded zipped `Data` folder is extracted and located within the same root as the software. Basically move it to the same root as `pybimscantools`.

```
Data/
├── Test_data/
│   ├── images/
│   ├── marker/
│   ├── models/
│   ├── pointclouds/
│   ├── points_for_transformation.xlsx
pybimscantools/
├── dependencies/
├── doc/
├── examples/
├── PIX4D_DB_PROFILES/
├── pybimscantools/
├── venv/
├── MANIFEST.in
├── pyproject.toml
├── README.MD
├── requirements.txt
├── setup.py
└── test.py
```

If you want to set up your own project, make sure the folder structure as below:
*Required structure and files in order to run the pipeline.

```
Data/
├── Test_data/
├── (Other_project_of_your_choices_with_same_structure_as_above)/
│   ├── images/
│   |   ├── ....jpg* (aerial images of your site)
│   ├── marker/
│   |   ├── marker_ifc.xlsx* (marker measurement according to CWA_CEN_XXX in Project Coordinate System)
│   |   ├── relative_corners_tag_(name_of_tag).xlsx* (tag info. w.r.t marker)
│   ├── models/
│   |   ├── ifc/
│   |   |    ├── ....ifc* (ifc file of your site)
│   ├── pointclouds*/
│   ├── points_for_transformation.xlsx* (transformation between 2 coordinates)
```

### Required Programs and Licenses

#### 1. PIX4Dmapper, photogrammetry software

`pybimscantools` associates with photogrammetry software, `PIX4Dmapper`. The user is required to have the photogrammetry software installed with a working license. The lastest version of `PIX4Dmapper` that `pybimscantools` supports is `4.5.6` due to the need of PIX4Dtagger integrated in this PIX4Dmapper specific version.
The user is required to install PIX4Dmapper in a typical location, `C:\Program Files\Pix4Dmapper`. Once installed, extract the DB profile of PIX4Dmapper from the folder `PIX4D_DB_PROFILES` and place them in PIX4D database location.

```
- Extract the zipped file, you will see 2 folders (common, and Pix4D mapper)
- Place the extracted folders under the PIX4D database location.
- Usually under C:\Users\{YOUR-USER}\AppData\Local\pix4d
```

#### 2. drone harmony, drone mission planning software

`pybimscantools` also associates with `drone harmony` software to visualize representations of construction site and partially automate the mission planning process. The user is required to have a working license with `drone harmony` as well as the `API_KEY` from drone harmony. `API_KEY` is required to be entered in the program (e.g. `test.py`).

------------------------------------------------------------------------

## License
This software is licensed under the MIT License, except for dependencies that have their own respective licenses. See the `LICENSE` file for details.

This software includes various third-party libraries with different licenses. Below is a list of key dependencies and their respective licenses:
```
alphashape      MIT
requests        Apache-2.0
urllib3         MIT
numpy           BSD-3-Clause
jpype1          Apache-2.0
matplotlib      PSF
scipy           BSD-3-Clause
termcolor       MIT
pandas          BSD-3-Clause
pyquaternion    MIT
simplekml       BSD-2-Clause
openpyxl        MIT
Flask           BSD-3-Clause
piexif          MIT
laspy           MIT
ifcopenshell    LGPL-3.0
shapely         BSD-3-Clause
lark            MIT
open3d          MIT
swissreframe    MIT
```
------------------------------------------------------------------------