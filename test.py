###########################
### Preparation Process ###
###########################

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
from pybimscantools import depth_rendering as dr
from pybimscantools import exif
from pybimscantools import markers
from pybimscantools import pointcloud as pc
from pybimscantools import transformations as trafo


# name of the project directory
project_name = "Test_data"

# create relative path to the project
path = os.path.join(os.path.join(os.path.dirname(os.getcwd()), "Data", project_name))


"""
IFC-to-collada conversion
"""

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


"""
IFC-to-polygon extraction algorithm
"""

# Set up the algorithm
alg = isococ.ISOCoC(resolution=0.01,
                    z_span=30,
                    z_resolution=2.5,
                    alpha= 0.0,
                    threshold=0.05)

# Read the IFC file, extract and show the ifc slabs
file_name = "KSA_FAS_51_XX_200_43_240123.ifc"
(all_slab_vertices, slab_plot, all_slab_edges) = alg.read_from_file(
                os.path.join(path, "models\ifc", file_name),
                min_value=6,
                max_value=42,
                plot=True,
                indvi_plot=False,
                verbose=False
            )
slab_plot.show()

# Algorithm to scan through the IFC file and extract the union shape
union_shape = alg.scan_through(os.path.join(path, "models\ifc", file_name),
                 min_height=6,
                 max_height=42,
                 plot=True,
                 rearrange_points=False,
                 verbose=False)


"""
Polygon (CoordinateModel)
"""
# Since the height of the polygon is defined by Z values already, we can set all the heights to 0 for google earth
union_shape_google_earth = union_shape.copy()
if isinstance(union_shape_google_earth, cm.CoordinateModel):
    union_shape_google_earth.set_height_all(0)
else:
    union_shape_google_earth.set_height(0)

# Transformation matrix from IFC to LV95
transformation_file_name = "points_for_transformation_ifc_to_lv95.xlsx"
T = trafo.read_transformation_matrix_from_points_from_xlsx(path, transformation_file_name)
trafo.print_transformation_matrix_for_cloud_compare(T)
union_shape.apply_transformation_matrix(T)
union_shape.transform_from_lv95_to_google_earth()
union_shape_google_earth.apply_transformation_matrix(T)
union_shape_google_earth.transform_from_lv95_to_google_earth()
union_shape_google_earth.create_kml_for_google_earth(path, file_name.split(".")[0] + ".kml")


"""
Drone Harmony
"""

# Set up the Drone Harmony API
API_KEY = "" # put in your API key from drone harmony
CLIENT_USER_ID = "" # put in your client user id (can be anything, see drone harmony API manual)
dh = droneharmony.DroneHarmony(API_KEY, CLIENT_USER_ID)

# Uploading the CoordinateModel
ret_data = dh.prepare_geo_json(union_shape, site_name="KSA", color="Gold", scene_name="Hospital")
Response = dh.post_site(ret_data)
dh.read_through()




##########################
### Evaluation Process ###
##########################

"""
KSA (Kantonsspital Aarau)
LV95  : 2'647'002.81, 1'248'819.15
WGS 84: 47.388525, 8.061138
Date  : 18.07.2024
Notes : Markers were only applied sparsly on the two top huts of the building. Therefore the point cloud processing with
        PIX4Dtagger failed. The mission was executed with RTK GPS and the marker information is only used to to get estimate
        the transformation between the RTK GPS and the IFC coordinate system.
"""

"""
Markers (already wrt IFC)
"""

# convert markers from *.xlsx to *.json and *.json to pandas dataframe
markers.convert_markers_from_xlsx_to_json(path)
marker_table = markers.read_markers_from_json_to_table(path)

# in case there is more than one corners_tag_*.xlsx file, create corners_tag_*.json and relative_corners_tag_*.json
for file_name in os.listdir(os.path.join(path, "markers")):
    if "relative_corners_tag" in file_name and file_name.endswith(".xlsx"):
        tag_type = file_name.split(".")[0].split("_")[-1]
        file_name_json = markers.convert_relative_corners_tag_from_xlsx_to_json(path, file_name)
        corner_table = markers.read_relative_corners_tag_from_json_to_table(path, file_name_json)
        corners_tag_name = "corners_tag_" + tag_type + ".json"
        markers.create_tag_corners_json(path, marker_table, corner_table, corners_tag_name)

# read tag_corners.json to pandas dataframe and create 'px4tagger.txt'
tag_table = markers.read_marker_corners_json_to_table(path, "corners_tag_chilli.json")
# markers.plot_tags(tag_table) # only for visualisation
markers.create_tag_corners_txt_from_table(path, tag_table)

# Set up the backend session
mkb_session = mkb.MarkersBackend(path, project_name)
# uploading CWA marker
mkb_session.upload_markers()
# uploading dependent tag(s)
for file in os.listdir(os.path.join(path, "markers")):
    if "relative_corners_tag" in file and file.endswith(".xlsx"):
        tag_type = file.split(".")[0].split("_")[-1]
        mkb_session.upload_relative_corners(corners_type=tag_type, file_name=file)
        # getting the uploaded relative corners
        mkb_session.get_relative_corners(corners_type=tag_type)

# get all relative corner tag types in the project
mkb_session.get_relative_corners_type()
# for deleting the uploaded relative corners
# mkb_session.delete_relative_corners(corners_type="April_test")


"""
Transformation (RTK to IFC)
"""

# extract transformation matrix from a set of points (>=4)
T = trafo.read_transformation_matrix_from_points_from_xlsx(path)
trafo.print_transformation_matrix_for_cloud_compare(T)
trafo.convert_transformation_matrix_to_json(path, T, "T_rtk_to_ifc.json")


"""
Triggering PIX4D CLI
"""

img_loc = os.path.join(path, "images")
marker_loc = os.path.join(path, "px4tagger.txt")
output_loc = os.path.join(path, "pix4d")

pix4d = pix4d_cli.Pix4dCli()
# for project that uses markers
# pix4d.run_pix4dtagger(img_loc, marker_loc, output_loc, project_name + "_marker.p4d", "thau_local")
# pix4d.run_pix4dmapper_marker_system(os.path.join(output_loc, project_name + "_marker.p4d"))
# for project that uses RTK
pix4d.run_pix4dmapper_rtk(img_loc, output_loc, project_name + "_rtk.p4d")


""" QUESTIONS FOR THE USER """
# Ask the user to copy the pose and orientation information from the Pix4D project to the project directory (inside images folder)
# Ask the user to copy the point cloud file from the Pix4D project to the project directory (create a new folder named pointclouds)
# check if those 2 txt files and the point cloud file (.las) are in the project directory
# for the point cloud file, check if there is a .las file in the pointclouds folder
while not os.path.exists(os.path.join(path, "images", "calibrated_external_camera_parameters.txt")) \
    and not os.path.exists(os.path.join(path, "images", "calibrated_camera_parameters.txt")) \
    and not any(file.suffix == '.las' for file in Path(os.path.join(path, "pointclouds")).glob('*')):
    input("Please copy the \"calibrated_external_camera_parameters.txt\" and \"calibrated_camera_parameters.txt\" from the Pix4D project to the project directory \
          (inside images folder) and the point clouds file to the pointclouds folder and press Enter to continue...")


"""
Transform Point Cloud to IFC
"""

# transform one specific pointcloud
file_name_pc = "Test_data.las"
pc.transform_pointcloud(path, file_name_pc, T)


"""
Embed Pose Information in EXIF and Render Depth Images
"""

# embed pose information
exif.embed_pose_information(path, t=T)

# extract pose information
img_filename_list, img_transformation_list = exif.extract_file_names_and_transformation_as_lists(path)
# exif.plot_camera_frames(img_transformation_list) # only for visualisation

# render depth images
dr.render_depth_images(img_filename_list, img_transformation_list, path, file_name_pc, do_use_transformed_pointcloud=True)