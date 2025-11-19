###############################################################################################################################
################################################# Preparation Process #########################################################
###############################################################################################################################

import os
import time
from pathlib import Path

from pybimscantools import droneharmony
from pybimscantools import isococ
from pybimscantools import ifcconvert
from pybimscantools import coordinatelist as cl
from pybimscantools import coordinatemodel as cm
from pybimscantools import textcolor
from pybimscantools import markersbackend as mkb
from pybimscantools import pix4dcli as pix4d_cli
from pybimscantools import bimxd
from pybimscantools import depth_rendering as dr
from pybimscantools import exif
from pybimscantools import markers
from pybimscantools import pointcloud as pc
from pybimscantools import transformations as trafo


### Name of the project directory
project_name = "Test_data"      # if you setup a new project, please change the project name

### Create relative path to the project
path = os.path.join(os.path.join(os.path.dirname(os.getcwd()), "Data", project_name))



""" *******************************
IFC-to-collada conversion
******************************* """

""" This step is optional to convert the IFC file to collada format.
The collada file will be created under the models/collada folder. """

Start_Time = time.time()
ifc_convert = ifcconvert.IfcConvert()
ifc_convert.convert_to_collada(os.path.join(path, "models\ifc"),  os.path.join(path, "models\collada"))
End_Time = time.time()
print(
    textcolor.colored_text(
        f"Elapsed time was {ifc_convert.seconds_to_minute(End_Time-Start_Time)} minutes",
        "Blue",
    )
)



""" *******************************
IFC-to-polygon extraction algorithm
******************************* """

""" This step is to create a polygonal representation of construction site from the IFC file.

Set up the algorithm
Parameters explanation:
resolution: groups identical IfcSlabs at different heights into single layers
z_span: defines the height of the scanning window
z_resolution: specifies the vertical step size of the scanning window
alpha: controls the detection of non-convex shapes
threshold: sets the minimum area difference between scanning windows to identify new layers """

alg = isococ.ISOCoC(resolution=0.01,
                    z_span=30,
                    z_resolution=2.5,
                    alpha= 0.0,
                    threshold=0.05)

### Read the IFC file, extract and show the ifc slabs
""" This step is to visualise the IFC file and all slabs in the range
to get an idea of the building structure. """

file_name = "KSA_FAS_51_XX_200_43_240123.ifc"       # put in the name of the IFC file
(all_slab_vertices, slab_plot, all_slab_edges) = alg.read_from_file(
                os.path.join(path, "models\ifc", file_name),
                min_value=6,        # minimum height of the building to be scanned
                max_value=42,       # maximum height of the building to be scanned
                plot=True,
                indvi_plot=False,
                verbose=False
            )
slab_plot.show()

### Algorithm to scan through the IFC file and extract the union shape
union_shape: cl.CoordinateList | cm.CoordinateModel = alg.scan_through(os.path.join(path, "models\ifc", file_name),
                 min_height=6,
                 max_height=42,
                 plot=True,
                 rearrange_points=False,
                 verbose=False)



""" *******************************
Polygon (CoordinateModel)
******************************* """

"""This step is to handle the polygonal representation of the construction site in the right coordinate system.
# Usually the IFC file (the consstruction model) is in the project coordinate system(local construction site coordinate system).
# Therefore, the polygonal representation of the construction site extracted from the algorithm is as well in the project coordinate system.
# However, the extracted polygonal representation needs to be visualized in the drone harmony software, which is working in the global coordinate system.
# Therefore, the polygonal representation needs to be transformed from the project coordinate system to the global coordinate system. """

### Since the height of the polygon is defined by Z values already, we can set all the heights to 0 for google earth.
union_shape_google_earth = union_shape.copy()
if isinstance(union_shape_google_earth, cm.CoordinateModel):
    union_shape_google_earth.set_height_all(0)
else:
    union_shape_google_earth.set_height(0)

### Transformation matrix from IFC to LV95
transformation_file_name = "points_for_transformation_ifc_to_lv95.xlsx"     # put in the name of the transformation file
T = trafo.read_transformation_matrix_from_points_from_xlsx(path, transformation_file_name)
trafo.print_transformation_matrix_for_cloud_compare(T)
union_shape.apply_transformation_matrix(T)
union_shape.transform_from_lv95_to_google_earth()
union_shape_google_earth.apply_transformation_matrix(T)
union_shape_google_earth.transform_from_lv95_to_google_earth()

### Create a KML file for Google Earth visualization
### The KML file will be created under the models/kml folder.
union_shape_google_earth.create_kml_for_google_earth(path, file_name.split(".")[0] + ".kml")



""" *******************************
Drone Harmony
******************************* """

""" This step is to upload the polygonal representation of the construction site to the drone harmony software.
The user can use drone harmony web application to plan the drone flight mission for the construction site afterwards. 
The user needs to have an account and API key to use the drone harmony API.
Therefore, this section is commented out by default. 
Please refer to the drone harmony API documentation for more information about how to get these parameters. """

# ### Set up the Drone Harmony API
# API_KEY = "" # put in your API key from drone harmony
# CLIENT_USER_ID = "" # put in your client user id (can be anything, see drone harmony API manual)
# dh = droneharmony.DroneHarmony(API_KEY, CLIENT_USER_ID)

# ### Uploading the CoordinateModel
# ret_data = dh.prepare_geo_json(union_shape, site_name="KSA", color="Gold", scene_name="Hospital")
# Response = dh.post_site(ret_data)
# dh.read_through()




###############################################################################################################################
################################################# Evaluation Process ##########################################################
###############################################################################################################################

"""
KSA (Kantonsspital Aarau)
LV95  : 2'647'002.81, 1'248'819.15
WGS 84: 47.388525, 8.061138
Date  : 18.07.2024
Notes : Markers were only applied sparsly on the two top huts of the building. Therefore the point cloud processing with
        PIX4Dtagger failed. The mission was executed with RTK GPS and the marker information is only used to to get estimate
        the transformation between the RTK GPS and the IFC coordinate system.
"""


""" *******************************
Markers (already wrt IFC)
******************************* """

""" This step is dealing with markers that are applied on the construction site.
Usually the markers(CWA 18046:2023) are applied on the construction site such that the images taken by the drone can be georeferenced.
Meaning that post-processing steps such as point cloud generation and so on, processing these images will result in the coordinates of the markers.
In our case, due to the use of PIX4Dtagger in our pipeline, chili tags were required for the point cloud processing with georeferences.
Therefore, chili tags were applied in a small consistent distance with respect to the the CWA markers on every markers.
Typically, a surveyor is required to measure the markers(in this case, CWA) within the project coordinate system.
This data is then put in the file markers_ifc.xlsx under the markers folder. If there are other tags required for the project, for example, 
other robots that are using different kinds of tags, different tags can also be applied on the CWA markers like in our case with chili tags.
The relative corners of the chili tags are then put in the file relative_corners_tag_chilli.xlsx under the markers folder. 
This is the distance with respect to the CWA marker. These two files are then used to create px4tagger.txt file which is used in the PIX4Dtagger software
for automatic point cloud generation with georeferences. Moreover, the files will also be uploaded to the central server(currently https://humantech.dev/) so that
every partner can access the information of the CWA markers and tags of their choices for localization. """

### Convert markers from *.xlsx to *.json and *.json to pandas dataframe
markers.convert_markers_from_xlsx_to_json(path)
marker_table = markers.read_markers_from_json_to_table(path)

### In case there is more than one corners_tag_*.xlsx file, create corners_tag_*.json and relative_corners_tag_*.json
for file_name in os.listdir(os.path.join(path, "markers")):
    if "relative_corners_tag" in file_name and file_name.endswith(".xlsx"):
        tag_type = file_name.split(".")[0].split("_")[-1]
        file_name_json = markers.convert_relative_corners_tag_from_xlsx_to_json(path, file_name)
        corner_table = markers.read_relative_corners_tag_from_json_to_table(path, file_name_json)
        corners_tag_name = "corners_tag_" + tag_type + ".json"
        markers.create_tag_corners_json(path, marker_table, corner_table, corners_tag_name)

### Read tag_corners.json to pandas dataframe and create 'px4tagger.txt'
tag_table = markers.read_marker_corners_json_to_table(path, "corners_tag_chilli.json")
# markers.plot_tags(tag_table)        # only for visualisation
markers.create_tag_corners_txt_from_table(path, tag_table)

### Set up the backend session
mkb_session = mkb.MarkersBackend(path, project_name)
### Uploading CWA marker
mkb_session.upload_markers()
### Uploading dependent tag(s)
for file in os.listdir(os.path.join(path, "markers")):
    if "relative_corners_tag" in file and file.endswith(".xlsx"):
        tag_type = file.split(".")[0].split("_")[-1]
        mkb_session.upload_relative_corners(corners_type=tag_type, file_name=file)
        ### Getting the uploaded relative corners
        mkb_session.get_relative_corners(corners_type=tag_type)

### Get all relative corner tag types in the project
mkb_session.get_relative_corners_type()
### For deleting the uploaded relative corners
# mkb_session.delete_relative_corners(corners_type="chilli")



""" *******************************
Transformation (RTK to IFC)
******************************* """

""" As described above that the images taken by drone for this project were not that good for PIX4Dtagger to detect the chili tags, this is why we have to process the point cloud
in the RTK GPS coordinate instead of the project coordinate system and also a reason we need the transformation from the RTK GPS to the project coordinate system.
The file points_for_transformation.xlsx in the project folder contains the points that are used to calculate the transformation matrix.
This T matrix will be used to transform the point cloud from the RTK GPS coordinate system to the project coordinate system afterwards. """

### Extract transformation matrix from a set of points (>=4)
T = trafo.read_transformation_matrix_from_points_from_xlsx(path)
trafo.print_transformation_matrix_for_cloud_compare(T)
trafo.convert_transformation_matrix_to_json(path, T, "T_rtk_to_ifc.json")



""" *******************************
Triggering PIX4D CLI
******************************* """

""" This step is to trigger the PIX4D CLI for automated point cloud processing.
Since this project processes point cloud in the RTK GPS coordinates, PIX4Dtagger is not used in this case.
However, if the images taken by the drone are good enough for PIX4Dtagger to detect chili tags, the user can use the PIX4Dtagger for automating georeferencing of the point cloud.
In that case,, the resulting point cloud will already be in the project coordinate system and the transformation matrix will not be needed.
You need to follow the steps in the README.MD file in order to set up the PIX4D and its requirements on your computer.
After PIX4Dmapper has finished processing the point cloud, it will create some files under pix4d/project_name/1_initial/params folder and the point cloud file under
pix4d/project_name/2_densification/point_cloud folder. Two text files and point cloud file are needed to be copied to the dedicated locations in the next step. """

""" This step requires PIX4D 4.5.6 version to be installed and a valid license.
Therefore, this section is commented out by default. """

# img_loc = os.path.join(path, "images")
# marker_loc = os.path.join(path, "px4tagger.txt")
# output_loc = os.path.join(path, "pix4d")

# pix4d = pix4d_cli.Pix4dCli()
# ### For project that uses markers
# # pix4d.run_pix4dtagger(img_loc, marker_loc, output_loc, project_name + "_marker.p4d", "YOUR_USERNAME")     # put in your username of your computer
# # pix4d.run_pix4dmapper_marker_system(os.path.join(output_loc, project_name + "_marker.p4d"))
# ### For project that uses RTK
# pix4d.run_pix4dmapper_rtk(img_loc, output_loc, project_name + "_rtk.p4d")



""" QUESTIONS FOR THE USER """
# Ask the user to copy the pose and orientation information from the Pix4D project to the project directory (inside images folder)
# Ask the user to copy the point cloud file from the Pix4D project to the project directory (create a new folder named pointclouds)
# Check if those 2 txt files and the point cloud file (.las) are in the project directory
# For the point cloud file, check if there is a .las file in the pointclouds folder
while not os.path.exists(os.path.join(path, "images", "calibrated_external_camera_parameters.txt")) \
    or not os.path.exists(os.path.join(path, "images", "calibrated_camera_parameters.txt")) \
    or not any(file.suffix == '.las' for file in Path(os.path.join(path, "pointclouds")).glob('*')):
    input("Please copy the \"calibrated_external_camera_parameters.txt\" and \"calibrated_camera_parameters.txt\" from the Pix4D project to the project directory \
          (inside images folder) and the point clouds file to the pointclouds folder and press Enter to continue...")



""" *******************************
Transform Point Cloud to IFC
******************************* """

""" This step is to transform the point cloud from the RTK GPS coordinate system to the project coordinate system.
If the point cloud is already in the project coordinate system, this step is not needed.
This step will create a new point cloud file under pointclouds/transformed folder. """

### Transform one specific pointcloud
file_name_pc = "Test_data.las"
pc.transform_pointcloud(path, file_name_pc, T)



""" *******************************
Embed Pose Information in EXIF and Render Depth Images
******************************* """

""" This step is to embed the pose information in the images and render the depth images.
This step will create pose embedded images under images/pose_embedded folder and depth images under images/depth_rendered folder. """

### embed pose information
exif.embed_pose_information(path, t=T)

### Extract pose information
img_filename_list, img_transformation_list = exif.extract_file_names_and_transformation_as_lists(path)
# exif.plot_camera_frames(img_transformation_list)        # only for visualisation

### Render depth images
dr.render_depth_images(img_filename_list, img_transformation_list, path, file_name_pc, do_use_transformed_pointcloud=True)



""" *******************************
# BIMxD Collaboration (Automatic upload)
******************************* """

""" This step is to upload the project results to BIMxD collaboration platform. 
The user is required to have an account an access to a BIMxD project.
The code below shows the possibilities and different functionalities of the BIMxD API.
However, Some parameters inside bimxd.py are modified due to confidentiality reasons.
The user needs to fill in these parameters in order to use the BIMxD API.

# Catenda Hub user related information
CLIENT_ID = ""
CLIENT_SECRET = ""

# Catenda Hub project related information (project of your choices)
TEST_PROJECT_1_ID = ""
TEST_PROJECT_2_ID = ""
TEST_PROJECT_3_ID = ""
TEST_PROJECT_4_ID = ""

Therefore, this section is commented out by default.
Please contact Catenda or refer to BIMxD API documentation for more information about how to get these parameters. """

# bimxd_project_name = "project1"
# ### Setting up BIMXD
# bim_xd = bimxd.BimXd(project=bimxd_project_name)
# bim_xd.client_credentials_grant()
# bim_xd.setup_library(project=bimxd_project_name)

# ### Library
# bim_xd.library.list_library_items(list_all=True)

# ### Uploading a file or creating a folder to\in BIMXD
# bim_xd.library.create_library_item(None, int(input("Please insert the number of folder for the uploading file(s)!, -1 otherwise:")), True)
# bim_xd.library.list_library_items(list_all=True)

# ### Downloading a file from BIMXD
# bim_xd.library.download_library_item([2], save_to="C:\\Users\\<USERNAME>\\Desktop")

# ### Uploading project results
# bim_xd.library.upload_project_results(path)

# ### BCF
# bim_xd.setup_bcf()
# bim_xd.bcf.get_issue_boards()
# bim_xd.bcf.get_topics(1)

# ### Creating a BCF issue
# bim_xd.bcf.create_topics(
#     issue_board_no=1,
#     bcf_name="BCF_Workshop_<Preparation>",
#     bcf_type="Warning",
#     bcf_status="Open",
#     bcf_description="This BCF is for testing purposes only. It has no real meaning.",
#     bcf_labels=["Drone", "Thermal Drone"],
#     assigned_to="abc@def.com",
#     creation_author="abc@def.com"
# )
# ### Deleting a BCF issue
# bim_xd.bcf.delete_topics(1, [1])