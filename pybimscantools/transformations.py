""" This file contains functions that are used to 
calculate transformations between coordinate systems 
"""

import json
import os

import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation

from pybimscantools import helper
from pybimscantools import textcolor


def get_normal_to_3d_points(m: np.array) -> np.array:
    """
    Function that takes a 3xN matrix of points and returns the normal vector
    """
    y = m - np.mean(m, axis=0)
    _, _, vt = np.linalg.svd(y)
    v = vt[2, :]
    print(f"   error norm = {np.linalg.norm(y @ v)}")

    return v


def print_transformation_matrix_for_cloud_compare(t: np.array) -> None:
    """
    Function that prints the transformation matrix to paste in CloudCompare
    """
    print("Transformation Matrix for CloudCompare")
    for i in np.arange(0, 4):
        print(*t[i, :], sep=" ")
    print("Edit->Apply Transformation or Cntr+T")


# function that takes a 3x1 direction vector and a scalar and
# return the corresponding transformation matrix
# example:
#   dx = 30.0
#   x = np.array([2697242.6, 1261374.2, 0.0]) - np.array([2697263.5, 1261406.5, 0.0])
#   Tx = transformations.get_transformation_to_shift_towards_vector(x, dx)
#   dy = 20.0
#   y = np.array([2697305.8, 1261378.8, 0.0]) - np.array([2697263.5, 1261406.5, 0.0])
#   Ty = transformations.get_transformation_to_shift_towards_vector(y, dy)
#   T = Tx.dot(Ty) = Ty.dot(Tx)

def get_transformation_to_shift_towards_vector(v: np.array,
                                               dv: float) -> np.array:
    """
    Function that takes a 3x1 direction vector and a gain
    and return the corresponding transformation matrix
    """
    t = np.identity(4)

    v_norm = np.linalg.norm(v)
    if v_norm != 0:
        v = v / v_norm

    t[0:3, 3] = dv * v / np.linalg.norm(v)

    return t


# positive angle around vn rotates v1 into v2 whereas |vn| = 1
# https://stackoverflow.com/questions/5188561/signed-angle-between-two-3d-vectors-with-same-origin-within-the-same-plane
def get_rotation_vector(v1: np.array,
                        v2: np.array) -> np.array:
    """
    Calculates the rotation vector that rotates v1 into v2
    """
    vn = np.cross(v1, v2)

    vn_norm = np.linalg.norm(vn)
    if vn_norm != 0:
        vn = vn / vn_norm

    ang = np.arctan2(np.dot(vn, np.cross(v1, v2)), np.dot(v1, v2))

    return ang * vn


def get_transformation_matrix_from_rotation_vector_and_translation(rotvec: np.array,
                                                                   p: np.array) -> np.array:
    """
    Function that takes a rotation vector rotvec and a translation
    vector p and returns the 4x4 transformation matrix
    """
    t = np.identity(4)
    t[0:3, 0:3] = Rotation.from_rotvec(rotvec).as_matrix()
    t[0:3, 3] = p
    t[3, 3] = 1.0

    return t


def get_inverse_transformation_matrix(t: np.array) -> np.array:
    """
    Function that takes a 4x4 transformation matrix T and
    returns the inverse transformation matrix
    """

    t_inv = np.identity(4)
    t_inv[0:3, 0:3] = t[0:3, 0:3].transpose()
    t_inv[0:3, 3] = -t[0:3, 0:3].transpose().dot(t[0:3, 3])
    t_inv[3, 3] = 1.0

    return t_inv


def get_unit_transformation_as_rotation_and_translation() -> (np.array, np.array):
    """
    Function that returns a unit transformation matrix
    """
    t = np.identity(4)

    return t[0:3, 0:3], t[0:3, 3]


# function that takes a file name and returns a 4x4 transformation matrix
# the file should contain 2 sets of 4 points, the first set is
# the reference and the second set is the model
# first the position vectors [x y z] w.r.t. the reference frame (R)
# then the corresponding position vectors
# w.r.t. the measurement frame (M), example below:
# ----------------------------------------------------------------------------------
# X Y Z
# -4.8940 27.9239 -36.4863     (R)
# 65.9122 -40.2540 76.7801
# -72.5519 -74.3449 -51.6353
# -135.4096 13.3823 -126.4875
# 1 50 -25                     (M)
# -120 75 60
# 5 -65 20
# 90 -70 -80
# ----------------------------------------------------------------------------------
# the returned transformation matrix is such that p_R = T_RM * p_M
def read_transformation_matrix_from_points_from_txt(path: str,
                                                    file_name: str) -> (np.array):
    """
    Function that takes a path and a file name and returns a 4x4 transformation matrix
    """
    file_was_found = helper.does_file_name_exist_in_path(path, file_name)
    if not file_was_found:
        print(f"   no file {file_name} was found, unit transformation will be used")
        r_rm, p_rm = get_unit_transformation_as_rotation_and_translation()

    else:
        data = pd.read_csv(os.path.join(path, file_name), sep=" ").to_numpy()
        r_rm, p_rm = check_and_get_transformation_from_data(file_name, data)

    t_rm = np.zeros((4, 4))
    t_rm[0:3, 0:3] = r_rm
    t_rm[0:3, 3] = p_rm.transpose()
    t_rm[3, 3] = 1.0

    return t_rm


# function that takes a file name and returns a 4x4 transformation matrix
# the file should contain 2 sets of 4 points, the first set is
# the reference and the second set is the model
# first the position vectors [x y z] w.r.t. the reference frame (R)
# then the corresponding position vectors
# w.r.t. the measurement frame (M), example below:
# ----------------------------------------------------------------------------------
# The resulting transformation matrix T will   px_R	      py_R      pz_R     px_M   py_M    pz_m
# transform from measurements w.r.t. (M)      -4.894     27.9239  -36.4863     1     50	    -25
# to measurements w.r.t. (R)                  65.9122   -40.254	   76.7801  -120     75	     60
# p_R = T_R * p_M                            -72.5519   -74.3449  -51.6353     5    -65	     20
# at least a set of 4 points is needed	     -135.4096	 13.3823 -126.4875    90    -70	    -80
# ----------------------------------------------------------------------------------
# the returned transformation matrix is such that p_R = T_RM * p_M

def read_transformation_matrix_from_points_from_xlsx(path: str,
                                                     file_name: str = 'points_for_transformation.xlsx') -> (np.array, np.array):
    """
    Function that takes a path and a file name and returns a 4x4 transformation matrix
    """
    # check if the file exists in the path
    file_was_found = helper.does_file_name_exist_in_path(path, file_name)
    if not file_was_found:
        print(f" no file {file_name} was found, unit transformation will be used")
        r_rm, p_rm = get_unit_transformation_as_rotation_and_translation()

    else:
        # read the file and calculate rotation and translation
        point_table = pd.read_excel(os.path.join(path, file_name), usecols='B:G', engine='openpyxl')

        data = point_table.to_numpy()
        # data is a Nx6 matrix, resize it to a 2*Nx3 matrix
        data = np.vstack((data[:, :3], data[:, 3:]))

        r_rm, p_rm = check_and_get_transformation_from_data(file_name, data)

    t_rm = np.zeros((4, 4))
    t_rm[0:3, 0:3] = r_rm
    t_rm[0:3, 3] = p_rm.transpose()
    t_rm[3, 3] = 1.0

    return t_rm


def check_and_get_transformation_from_data(file_name: str,
                                           data: np.array) -> (np.array, np.array):
    """
    Function that takes a filename and a np array and return the rotation matrix and translation vector
    """
    is_transformation_file_ok = True
    if (data.shape[0] % 2) == 1:
        # inform that there is not an even number in points
        print(f" {file_name} does contain an odd number of points, "
              "unit transformation will be used")
        is_transformation_file_ok = False
    elif data.shape[0] / 2 < 4:
        # inform that there is not enough data points
        print(f" {file_name} does not contain 2 sets of 4 points, "
              "unit transformation will be used")
        is_transformation_file_ok = False

    if is_transformation_file_ok:
        # kabsch algorithm
        points_r = data[0:int(data.shape[0] / 2), :]
        points_m = data[int(data.shape[0] / 2):int(data.shape[0]), :]
        r_rm, p_rm = rigid_transform_3d(points_m.transpose(), points_r.transpose())
    else:
        r_rm, p_rm = get_unit_transformation_as_rotation_and_translation()

    return r_rm, p_rm


def convert_transformation_matrix_to_json(path: str,
                                          t: np.array,
                                          file_name: str = 'T.json') -> str:
    """
    Function that takes a path, a filename and a transformation matrix and saves a *.json
    """
    with open(os.path.join(path, file_name), 'w') as f:
        json.dump({"T": t.tolist()}, f, indent=4, sort_keys=True)

    return str(file_name)


def read_transformation_from_json(path: str,
                                  file_name: str = 'T.json') -> np.array:
    """
    Function that takes a path and a filename to a transformation in a *.json and returns a numpy array
    """
    with open(os.path.join(path, file_name), 'r') as f:
        t_dict = json.loads(f.read())

    return np.array(t_dict['T'])


def create_cloudcompare_txt(path: str,
                            file_name: str,
                            t: np.array) -> None:
    """
    Function that takes a path, a filename and a transformation matrix and saves a *.txt
    """
    np.savetxt(os.path.join(path, file_name), t, fmt='%14.9f', delimiter='')


# https://github.com/nghiaho12/rigid_transform_3D
def rigid_transform_3d(points_m: np.array, points_r: np.array) -> (np.array, np.array):
    """
    Function that takes two 3xN matrices and returns the
    rotation matrix R and the translation vector t
    """
    assert points_m.shape == points_r.shape

    num_rows, num_cols = points_m.shape
    if num_rows != 3:
        raise Exception(f"   matrix A is not 3xN, it is {num_rows}x{num_cols}")

    num_rows, num_cols = points_r.shape
    if num_rows != 3:
        raise Exception(f"   matrix B is not 3xN, it is {num_rows}x{num_cols}")

    # find mean column wise
    centroid_a = np.mean(points_m, axis=1)
    centroid_b = np.mean(points_r, axis=1)

    # ensure centroids are 3x1
    centroid_a = centroid_a.reshape(-1, 1)
    centroid_b = centroid_b.reshape(-1, 1)

    # subtract mean
    ma = points_m - centroid_a
    mb = points_r - centroid_b

    h = ma @ np.transpose(mb)

    # find rotation
    u, s, vt = np.linalg.svd(h)
    r = vt.T @ u.T

    # special reflection case
    if np.linalg.det(r) < 0:
        print("   det(R) < R, reflection detected!, correcting for it ...")
        vt[2, :] *= -1
        r = vt.T @ u.T

    t = -r @ centroid_a + centroid_b

    # sanity check
    rank_k = np.linalg.matrix_rank(h)
    if rank_k < 3:
        print(textcolor.colored_text(f"   rank of H = {rank_k}, expecting 3", 'Red'))

    # quality check
    error = points_r.transpose() - (points_m.transpose() @ r.transpose() + t.transpose())
    error_norm = max(np.linalg.svd(error)[1])
    print(f"   error norm is {error_norm}")

    return r, t
