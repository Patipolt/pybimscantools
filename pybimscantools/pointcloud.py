import os

import numpy as np
import laspy

from pybimscantools import helper
from pybimscantools import textcolor


def transform_pointclouds(path: str, t: np.array = np.identity(4)) -> None:
    """
    Transforms the pointclouds in *.las format in the given folder and stores them in the subdirectory transformed
    """

    file_cntr = 0
    for file_name in os.listdir(os.path.join(path, "pointclouds")):
        if file_name.endswith(".las"):
            transform_pointcloud(path, file_name, t)
            file_cntr += 1

    if file_cntr == 0:
        print(textcolor.colored_text("   no pointclouds found in the folder!", "Red"))


def transform_pointcloud(path: str, file_name: str, t: np.array = np.identity(4)) -> None:
    """
    Transforms the pointcloud file_name in *.las format in the given folder and stores them in the subdirectory transformed
    """

    path = os.path.join(path, "pointclouds")

    path_sub_dir = helper.create_subdir_if_not_exists(path, "transformed")

    # check if the file exists in the path
    file_was_found = helper.does_file_name_exist_in_path(path, file_name)
    if not file_was_found:
        print(f"   no {file_name} file was found")
        return

    # load the LAS file
    las = laspy.read(os.path.join(path, file_name))
    
    # extract point coordinates
    points = np.vstack((las.x, las.y, las.z)).transpose()

    # apply the transformation to each point
    points_h = np.hstack((points, np.ones((points.shape[0], 1))))
    transformed_points_h = points_h @ t.T
    transformed_points = transformed_points_h[:, :3]

    # create a new LAS file and write the transformed points
    header = las.header
    las_transformed = laspy.create(point_format=las.point_format, file_version=header.version)

    # assign transformed coordinates to the new LAS file
    las_transformed.x = transformed_points[:, 0]
    las_transformed.y = transformed_points[:, 1]
    las_transformed.z = transformed_points[:, 2]

    # copy other attributes (e.g., intensity, classification) if necessary
    las_transformed.intensity = las.intensity
    las_transformed.return_number = las.return_number
    las_transformed.number_of_returns = las.number_of_returns
    las_transformed.scan_direction_flag = las.scan_direction_flag
    las_transformed.edge_of_flight_line = las.edge_of_flight_line
    las_transformed.classification = las.classification
    las_transformed.scan_angle_rank = las.scan_angle_rank
    las_transformed.user_data = las.user_data
    las_transformed.point_source_id = las.point_source_id
    # las_transformed.gps_time = las.gps_time

    # check if RGB color is present and copy it
    if hasattr(las, 'red') and hasattr(las, 'green') and hasattr(las, 'blue'):
        las_transformed.red = las.red
        las_transformed.green = las.green
        las_transformed.blue = las.blue

    file_was_found = helper.does_file_name_exist_in_path(path_sub_dir, file_name)
    if file_was_found:
        os.remove(os.path.join(path_sub_dir, file_name))

    # save the new LAS file
    las_transformed.write(os.path.join(path_sub_dir, file_name))
    print(f"   file {file_name} transformed and saved")
