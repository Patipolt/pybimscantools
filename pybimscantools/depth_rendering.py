# https://github.com/pablospe/render_depthmap_example

# TODO:
# - parse_camera_parameters_and_scale currently not used for transformation.

import os

import matplotlib.pyplot as plt
import numpy as np
import open3d as o3d
import laspy

from pybimscantools import helper
from pybimscantools import transformations


SCALE_PARAMS = 1.0 / 3.5
SHOW_PLT = False
# VOXEL_SIZE = 0.03 # downsampling, currently not used


def parse_camera_parameters_and_scale(path: str,
                                      image_name: str,
                                      SCALE_PARAMS,
                                      file_name: str='calibrated_camera_parameters.txt') -> (float, float, float, float, np.array):
    """
    Parse the camera parameters for the given image name from the given file name
    """


    with open(os.path.join(path, "images", file_name), 'r') as file:
        file_content = file.read()

    # split the content into sections based on the image name
    sections = file_content.split(image_name)

    # get the specific section for the given image name
    section = sections[1].split('\n\n')[0].strip()
    lines = section.split('\n')

    k = np.array([
        [float(val) for val in lines[1].split()],
        [float(val) for val in lines[2].split()],
        [float(val) for val in lines[3].split()]
    ])

    fx = SCALE_PARAMS * k[0, 0]
    fy = SCALE_PARAMS * k[1, 1]
    cx = SCALE_PARAMS * k[0, 2]
    cy = SCALE_PARAMS * k[1, 2]

    p = np.array([float(val) for val in lines[6].split()])

    r = np.array([
        [float(val) for val in lines[7].split()],
        [float(val) for val in lines[8].split()],
        [float(val) for val in lines[9].split()]
    ])

    t = np.zeros((4, 4))
    t[:3, :3] = r
    t[:3, 3] = p
    t[3, 3] = 1.0

    return fx, fy, cx, cy, t


def extract_width_and_height_and_scale(path: str,
                                       SCALE_PARAMS: float,
                                       file_name: str='calibrated_camera_parameters.txt') -> (int, int):
    """
    Extract the width and height from the given file name and scale them with the given scale parameters
    """

    with open(os.path.join(path, "images", file_name), 'r') as file:
        file_content = file.read()

    # split the content into lines
    lines = file_content.split('\n')

    # iterate over lines to find the first image entry
    for line in lines:
        parts = line.split()
        if len(parts) == 3 and (parts[0].endswith('.JPG') or parts[0].endswith('.jpg')):
            width = int(SCALE_PARAMS * float(parts[1]))
            height = int(SCALE_PARAMS * float(parts[2]))
            return width, height


def transform_to_intrinsic(t: np.array) -> np.array:
    """
    Transform the given transformation matrix to intrinsic convention
    """

    # rotate view point, camera needs to be z forward, x right, y down
    t_cam = np.zeros((4, 4))
    t_cam[0, 1] = -1.0  # x <- -y
    t_cam[1, 2] = -1.0  # y <- -z
    t_cam[2, 0] = 1.0   # z <-  x
    t_cam[3, 3] = 1.0

    return t_cam @ transformations.get_inverse_transformation_matrix(t)


def render_depth_images(img_filename_list: list,
                        img_transformation_list: list,
                        path: str,
                        file_name: str='pointcloud.las',
                        do_use_transformed_pointcloud: bool = False) -> None:
    """"
    Render depth images for the given images and transformations
    """

    # sub directory for ply files
    path_sub_dir = helper.create_subdir_if_not_exists(path, "polygons")

    # check if ply file exists and if not create it out of the las file
    file_name_ply = file_name.split(".")[0] + ".ply"
    # file_name_ply = file_name.split(".")[0] + "_subsampled_" + str(VOXEL_SIZE * 100).replace(".", "_") + "_cm.ply"
    if helper.does_file_name_exist_in_path(path_sub_dir, file_name_ply):
        pcd = o3d.io.read_point_cloud(os.path.join(path_sub_dir, file_name_ply))

    else:
        if do_use_transformed_pointcloud:
            las_file = laspy.read(os.path.join(path, "pointclouds", "transformed", file_name))
        else:
            las_file = laspy.read(os.path.join(path, "pointclouds", file_name))

        # convert the data to Open3D format
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(np.vstack((las_file.x, las_file.y, las_file.z)).transpose())
        pcd.colors = o3d.utility.Vector3dVector(np.vstack((las_file.red, las_file.green, las_file.blue)).transpose() / 65535.0)

        # # downsample the point cloud
        # pcd = pcd.voxel_down_sample(VOXEL_SIZE)

        # save the point cloud
        o3d.io.write_point_cloud(os.path.join(path, "polygons", file_name_ply), pcd)


    # create window
    vis = o3d.visualization.Visualizer()
    visible = False
    width, height = extract_width_and_height_and_scale(path, SCALE_PARAMS)
    vis.create_window(width=width, height=height, visible=visible)

    # add point cloud
    vis.add_geometry(pcd)

    # sub directory for depth rendered images
    path_sub_dir = helper.create_subdir_if_not_exists(os.path.join(path, "images"), "depth_rendered")

    # create pin hole camera parameters
    pin_hole_camera_parameters = o3d.camera.PinholeCameraParameters()

    # read camera and set intrinsic and extrinsic parameters
    # - currently all the images use the same intrinsic parameters, so i choose the first one
    # - the transformation extracted here is the original one from PIX4D and not necessary the IFC
    fx, fy, cx, cy, t = parse_camera_parameters_and_scale(path, img_filename_list[0], SCALE_PARAMS)
    pin_hole_camera_parameters.intrinsic = o3d.camera.PinholeCameraIntrinsic(width, height, fx, fy, cx, cy)

    for image_nr in range(len(img_filename_list)):

        pin_hole_camera_parameters.extrinsic = transform_to_intrinsic(img_transformation_list[image_nr])

        # set intrinsic and extrinsic parameters
        vis.get_view_control().convert_from_pinhole_camera_parameters(pin_hole_camera_parameters, allow_arbitrary=True)
        vis.update_renderer()

        # capture depth
        depth = vis.capture_depth_float_buffer(do_render=True)
        if SHOW_PLT:
            plt.imshow(depth)
            plt.show()
        vis.capture_depth_image(os.path.join(path_sub_dir, img_filename_list[image_nr].split(".")[0] + "_depth.png"), do_render=True, depth_scale=1000.0)

        # capture image
        image = vis.capture_screen_float_buffer(do_render=True)
        if SHOW_PLT:
            plt.imshow(image)
            plt.show()
        vis.capture_screen_image(os.path.join(path_sub_dir, img_filename_list[image_nr].split(".")[0] + "_pc_image.png"), do_render=True)

        print(f"   {img_filename_list[image_nr]} pc image and depth saved")

        # #  TODO: remove me
        # if image_nr == 5:
        #     break