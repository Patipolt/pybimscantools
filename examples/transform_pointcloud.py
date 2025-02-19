"""
This example shows how to transform a point cloud using a transformation matrix. It is assumed that within the project
directory there is a subdirectory called "pointclouds" containing the point cloud file or files that need to be transformed.
In the example here the transformatin matrix is estimated based on a set of points. The set of points has to be at
least 4 points in the original frame of reference and the corresponding points in the new frame of reference. The
workflow also works for point clouds containing big values for their coordinates, e.g. with respect to WGS84.
"""

import os

from pybimscantools import pointcloud as pc
from pybimscantools import transformations as trafo


# name of the project directory
project_name = "EXAMPLE_BIG_NUMBER_SUBSAMPLED_POINTCLOUD"

# create relative path to the project
path = os.path.join(os.path.join(os.path.dirname(os.getcwd()), "Data", project_name))


# extract transformation matrix from a set of points (>=4)
T = trafo.read_transformation_matrix_from_points_from_xlsx(path, "points_for_transformation.xlsx")
trafo.print_transformation_matrix_for_cloud_compare(T)
trafo.convert_transformation_matrix_to_json(path, T)

# transform one specific pointcloud
file_name_pc = "20240414_00_ZHAW_TH_RTK_Mixed_002_003_corner_subsampled.las"
pc.transform_pointcloud(path, file_name_pc, T)

# transform all the pointclouds in the subdirectory pointclouds
pc.transform_pointclouds(path, T)