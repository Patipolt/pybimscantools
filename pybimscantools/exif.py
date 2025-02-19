import os
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import piexif
import piexif.helper
from PIL import Image
from pyquaternion import Quaternion
from scipy.spatial.transform import Rotation

from pybimscantools import helper
from pybimscantools import textcolor


def plot_camera_frames(img_transformation_list: list) -> None:
    """
    Plots the camera frames for the given positions and quaternions (pose)
    """

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ax.set_box_aspect([1.0, 1.0, 1.0])

    # draw the camera frame for all entries of the lists
    for i in range(len(img_transformation_list)):
        r = img_transformation_list[i][0:3, 0:3]
        p = img_transformation_list[i][0:3, 3]

        # draw a frame with the tag convention (x- out of the camera, y- left, z- up)
        ax.quiver(p[0], p[1], p[2],
                  r[0, 0], r[1, 0], r[2, 0], length=2.0, color='r')
        ax.quiver(p[0], p[1], p[2],
                  r[0, 1], r[1, 1], r[2, 1], length=2.0, color='g')
        ax.quiver(p[0], p[1], p[2],
                  r[0, 2], r[1, 2], r[2, 2], length=2.0, color='b')

    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    x_middle = np.mean(x_limits)
    y_range = abs(y_limits[1] - y_limits[0])
    y_middle = np.mean(y_limits)
    z_range = abs(z_limits[1] - z_limits[0])
    z_middle = np.mean(z_limits)

    # the plot bounding box is a sphere in the sense of the infinity
    # norm, hence I call half the max range the plot radius.
    plot_radius = 0.5 * max([x_range, y_range, z_range])

    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])

    # set the labels
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    plt.show()


def extract_file_names_and_transformation_as_lists(path: str) -> (list, list):
    """
    Extracts the pose information from the images in the given folder and returns the file names and the trans as lists
    """

    path = os.path.join(path, "images")
    path = os.path.join(path, "pose_embedded")

    img_filename_list = []
    img_transformation_list = []

    file_cntr = 0
    for file_name in os.listdir(path):
        try:
            img = Image.open(os.path.join(path, file_name))
            exif_dict = piexif.load(img.info['exif'])

            # decode the bytes to string
            decoded_string = exif_dict["Exif"][piexif.ExifIFD.UserComment].decode('ascii')

            # extract the numerical data from brackets
            match = re.search(r'\[(.*?)\]', decoded_string)
            if match:
                numbers = match.group(1)
            else:
                numbers = ""

            # convert string numbers to a list of floats
            cleaned_numbers = re.sub(r'np\.float64\((.*?)\)', r'\1', numbers)
            float_nums = list(map(float, cleaned_numbers.split(',')))

            # extraxt transformation matrix
            t = np.identity(4)
            t[0:3, 0:3] = Quaternion(float_nums[3:]).rotation_matrix
            t[0:3, 3] = np.array(float_nums[:3])
            t[3, 3] = 1.0

            # inform user
            file_cntr += 1
            print(f"   {file_name} extracted pose")

            # extract pos and quat for each image
            img_filename_list.append(file_name)
            img_transformation_list.append(t)
        except:
            pass

        # #  TODO: remove me
        # if file_cntr == 5:
        #     break

    if file_cntr == 0:
        print(textcolor.colored_text("   no images found in the folder!", "Red"))

    return img_filename_list, img_transformation_list


def remove_gps_information(path: str) -> None:
    """
    Removes the GPS data from the images in the given folder and stores them in a subdirectory gps_removed
    """

    path = os.path.join(path, "images")

    path_sub_dir = helper.create_subdir_if_not_exists(path, "gps_removed")

    file_cntr = 0
    for file_name in os.listdir(path):
        try:
            img = Image.open(os.path.join(path, file_name))
            exif_dict = piexif.load(img.info['exif'])
            del exif_dict["GPS"]
            exif_bytes = piexif.dump(exif_dict)
            img.save(os.path.join(path_sub_dir, file_name), "jpeg", exif=exif_bytes)
            file_cntr += 1
            print(f"   {file_name} saved with gps removed")
        except:
            pass

    if file_cntr == 0:
        print(textcolor.colored_text("   no images found in the folder!", "Red"))


def embed_pose_information(path: str,
                           file_name: str = 'calibrated_external_camera_parameters.txt',
                           t: np.array = np.identity(4)) -> None:
    """
    Embeds the pose information from the given coordinates file into the images in the given folder and stores
    them in a subdirectory pose_embedded
    """

    path = os.path.join(path, "images")

    path_sub_dir = helper.create_subdir_if_not_exists(path, "pose_embedded")

    # aling camera frame so that x is pointing towards scene, y points left and z up
    quat_cc = Quaternion(matrix=np.array([[0, -1, 0], [0, 0, 1], [-1, 0, 0]]))

    r_rm = t[0:3, 0:3]
    pos_rm = t[0:3, 3]
    quat_rm = Quaternion(matrix=r_rm)

    # normalise quaternions
    quat_cc = quat_cc.normalised
    quat_rm = quat_rm.normalised

    # check if the file exists in the path
    file_was_found = helper.does_file_name_exist_in_path(path, file_name)
    if not file_was_found:
        print(f"   no {file_name} file was found")
        return

    file_cntr = 0
    data_table = pd.read_csv(os.path.join(path, file_name), sep=" ")  # extract data as a table
    for index, row in data_table.iterrows():
        img_name = row['imageName']

        try:
            # position w.r.t to (M)
            pos_i = np.array(row[['X', 'Y', 'Z']])

            # rotation w.r.t. (M)
            # see: https://support.pix4d.com/hc/en-us/articles/202558969-Yaw-Pitch-Roll-and-Omega-Phi-Kappa-angles
            quat_i = Quaternion(
                matrix=Rotation.from_euler('zyx', row[['Kappa', 'Phi', 'Omega']].to_numpy(), degrees=True).as_matrix())
            quat_i = quat_i.normalised

            # position w.r.t. (R)
            pos_i = pos_rm + quat_rm.rotate(pos_i)

            # rotate so that camera frame x is pointing towards scene, y points left and z up
            quat_i = quat_i * quat_cc

            # orientation w.r.t. (R)
            quat_i = quat_rm * quat_i

            # try to add information in user_comment
            user_str = f"{[pos_i[0], pos_i[1], pos_i[2], -quat_i[0], -quat_i[1], -quat_i[2], -quat_i[3]]}"

            # open file with Pillow an extract exif directory
            img = Image.open(os.path.join(path, img_name))
            exif_dict = piexif.load(img.info["exif"])

            # create and insert user_comment
            user_comment = piexif.helper.UserComment.dump(user_str, encoding="ascii")
            exif_dict["Exif"][piexif.ExifIFD.UserComment] = user_comment

            # create exif_bytes that goes along with the image and overwrite the image
            exif_bytes = piexif.dump(exif_dict)

            img.save(os.path.join(path_sub_dir, img_name), "jpeg", exif=exif_bytes)
            print(f"   {img_name} saved with pose embedded")
            file_cntr += 1
            
            # #  TODO: remove me
            # if file_cntr == 5:
            #     break

        except:
            pass

    if file_cntr == 0:
        print(textcolor.colored_text("   no images found in the folder!", "Red"))
