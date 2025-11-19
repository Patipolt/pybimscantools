# pybimscantools

A python package for automated data acquisition pipeline.
This package has been slightly modified from the version utilized by HumanTech project to generalize the use of the software.

## Data

There is provided data available for download at: https://drive.google.com/file/d/1X82WFLAPbr41ybdGQwJHutIHWmgMMlVG/view?usp=sharing.
This provided data is processed by `pybimscantools` as an example to demonstrate automated data acquisition and its pre-processing pipeline. The users are required to change data in order to perform automated data acquisition and its related pre-processing tasks of project of their choices.

------------------------------------------------------------------------


## Python swissreframe

** Notice for python `swissreframe` package
In order to use `swissreframe` package, which is included in pybimscantools, `JAVA` is required on your system. Please follow the instructions below before installing the environment.

### Windows

In windows you need to set an environment variable in system variables called **JAVA_HOME** to a 64 bit version of Java. You need to install `Java`, if it is not already installed.

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

## How to use

Clone a repository from: https://github.com/Patipolt/pybimscantools.git

Install `pybimscantools` package

```
python.exe -m pip install pybimscantools
```

Once you have set up the environment ready for the software, there are some requirements below in order to use `pybimscantools` at its fully functioning state. After that, you can follow the steps in `test.py`.

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