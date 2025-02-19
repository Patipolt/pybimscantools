"""
This example shows how to trigger the Pix4D CLI to process images and markers.
It also triggers Pix4Dmapper to run photogrammetric process automatically.
This example assumes that the Pix4Dmapper version 4.5.6 is installed on the system in its default location (C:\Program Files\Pix4Dmapper).
Any newer version of Pix4Dmapper doesn't support Pix4Dtagger but still supports Pix4Dmapper command line mode.
It is recommended that the provided Pix4Dmapper database and profile should also be installed in its default location.
The example also assumes that the images and the markers are already in place.
"""

import os
from pybimscantools import pix4dcli as pix4d_cli

# name of the project directory
project_name = "KSA"

# create relative path to the project
path = os.path.join(os.path.join(os.path.dirname(os.getcwd()), "Data", project_name))


img_loc = os.path.join(path, "images")
marker_loc = os.path.join(path, "px4tagger.txt")
output_loc = os.path.join(path, "pix4d")

pix4d = pix4d_cli.Pix4dCli()
# for project that uses markers
pix4d.run_pix4dtagger(img_loc, marker_loc, output_loc, project_name + "_marker.p4d", "thau_local")
pix4d.run_pix4dmapper_marker_system(os.path.join(output_loc, project_name + "_marker.p4d"))
# for project that uses RTK
pix4d.run_pix4dmapper_rtk(img_loc, output_loc, project_name + "_rtk.p4d")