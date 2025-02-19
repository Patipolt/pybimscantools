"""
This example shows how to extract and embed pose information into images. Furthermore, it shows how to
render depth images from a point cloud. It is assumed that within the project directory there is a
subdirectory called "images" containing the images that were used to generate the point cloud and a 
subdirectory called "pointclouds" containing the point cloud file or files. In the example here all the
data is already with respect to the IFC frame.
"""

import os

from pybimscantools import depth_rendering as dr
from pybimscantools import exif


# name of the project directory
project_name = "EXAMPLE_DEPTH_FYRSTIKKBAKKEN"

# create relative path to the project
path = os.path.join(os.path.join(os.path.dirname(os.getcwd()), "Data", project_name))


# embed pose information
exif.embed_pose_information(path)

# extract pose information
img_filename_list, img_transformation_list = exif.extract_file_names_and_transformation_as_lists(path)
# exif.plot_camera_frames(img_transformation_list) # only for visualisation

# render depth images
file_name_pc = "Wall_Site_PIX4Dtagger.las"
dr.render_depth_images(img_filename_list, img_transformation_list, path, file_name_pc)