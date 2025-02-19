import copy
import os

import matplotlib.pyplot as plt
import numpy as np
import simplekml
from swissreframe import initialize_reframe

from pybimscantools import textcolor
from pybimscantools import transformations
from pybimscantools import helper


class CoordinateList:
    """
    CoordinateList class containing a list of coordinates
    """

    def __init__(self, coordinates: list = None, altitude: float = None) -> None:
        self.__coordinates = []
        self.__height = 0
        if coordinates is not None and altitude is None:
            self.extend(coordinates)
        elif coordinates is not None and altitude is not None:
            self.extend_2d(coordinates, altitude)

    def __getitem__(self, i: int) -> list:
        """
        Return the i-th entry of the CoordinateList
        """
        return self.__coordinates[i]

    def copy(self) -> 'CoordinateList':
        """
        Create a copy of a CoordinateList object
        """
        return copy.deepcopy(self)

    def append(self, coordinate: list) -> None:
        """
        Append a coordinate to the end of the CoordinateList
        """
        self.__coordinates.append(coordinate)

    def pop(self) -> None:
        """
        Pop a coordinate from the end of the list
        """
        self.__coordinates.pop()

    def extend(self, coordinates: list) -> None:
        """
        Extend the CoordinateList with a list of coordinates
        """
        self.__coordinates.extend(coordinates)

    def extend_2d(self, coordinates_2d: list, altitude: float = 0) -> None:
        """
        Extend a CoordinateList with a 2d list of coordinates
        """
        for coordinate_2d in coordinates_2d:
            self.append([coordinate_2d[0], coordinate_2d[1], altitude])

    def len(self) -> int:
        """
        Return the number of coordinates in the list
        """
        return len(self.__coordinates)

    def last_idx(self) -> int:
        """
        Return the number of coordinates in the list - 1
        """
        return self.len() - 1

    def get_coordinate(self, i: int) -> list:
        """
        Return the i-th entry of the CoordinateList
        """
        return self.__coordinates[i]

    def set_height(self, height: float) -> None:
        """
        Set the height of the CoordinateList
        """
        self.__height = height

    def shift_height(self, delta: float) -> None:
        """
        Shift the height of the CoordinateList
        """
        self.__height += delta 

    def get_height(self) -> float:
        """
        Return the height of the CoordinateList
        """
        return self.__height

    def transform_from_lv95_to_google_earth(self) -> None:
        """
        Transform the CoordinateList from lv95 to google earth
        """
        coordinates_copy = self.copy()
        self.transform_from_lv95_to_etrf93_geographic()
        # copy 3rd coloumn of coordinates_copy into 3rd column of coordinates
        for i in range(0, self.len()):
            self.__coordinates[i] = (self.__coordinates[i][0],
                                     self.__coordinates[i][1],
                                     coordinates_copy.__coordinates[i][2] + self.__height)

    def apply_transformation_matrix(self, t: list) -> None:
        """
        Apply a transformation matrix to the CoordinateList
        """
        r = t[0:3, 0:3]
        p = t[0:3, 3]
        for i in range(len(self.__coordinates)):
            self.__coordinates[i] = r.dot(self.__coordinates[i]) + p

    def transform_from_lv95_to_etrf93_geographic(self) -> None:
        """ 
        Apply lv95 to etrf93 geographic transformation to the
        CoordinateList using swissreframe 
        """
        swiss_ref = initialize_reframe()
        for i in range(len(self.__coordinates)):
            self.__coordinates[i] = swiss_ref.compute_gpsref(self.__coordinates[i],
                                                             'lv95_to_etrf93_geographic')

    def transform_from_lv95_to_etrf93_geocentric(self) -> None:
        """
        Apply lv95 to etrf93 geocentric transformation to the 
        CoordinateList using swissreframe
        """
        swiss_ref = initialize_reframe()
        for i in range(len(self.__coordinates)):
            self.__coordinates[i] = swiss_ref.compute_gpsref(self.__coordinates[i],
                                                             'lv95_to_etrf93_geocentric')

    def transform_from_etrf93_geographic_to_lv95(self) -> None:
        """
        Apply etrf93 geographic to lv95 transformation to the 
        CoordinateList using swissreframe
        """
        swiss_ref = initialize_reframe()
        for i in range(len(self.__coordinates)):
            self.__coordinates[i] = swiss_ref.compute_gpsref(self.__coordinates[i],
                                                             'etrf93_gepgraphic_to_lv95')

    # apply etrf93 geocentric to lv95 transformation to the CoordinateList using swissreframe
    def transform_from_etrf93_geocentric_to_lv95(self) -> None:
        """
        Apply etrf93 geocentric to lv95 transformation to the 
        CoordinateList using swissreframe
        """
        swiss_ref = initialize_reframe()
        for i in range(len(self.__coordinates)):
            self.__coordinates[i] = swiss_ref.compute_gpsref(self.__coordinates[i],
                                                             'etrf93_geocentric_to_lv95')

    def print(self) -> None:
        """
        Print the CoordinateList
        """
        for i in range(len(self.__coordinates)):
            print(self.__coordinates[i])

    def plot_coordinates(self, color: str = 'b', marker: str = 'o') -> None:
        """
        Plot the coordinates of the CoordinateList in 3D
        """
        # plot the coordinates in 3D
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')

        ax.set_box_aspect([1.0, 1.0, 1.0])

        # extract the x, y and z values from the converted coordinates
        ax.scatter([x[0] for x in self.__coordinates],
                   [y[1] for y in self.__coordinates],
                   [z[2] for z in self.__coordinates], c=color, marker=marker)

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

    # def plot_tags(self, color: str = 'b', marker: str = 'o') -> None:
    #     """
    #     Plot the coordinates of the CoordinateList in 3D assuming
    #     it is a list of tags consisting of sets of 4 coordinates
    #     """
    #     # plot the coordinates in 3D
    #     fig = plt.figure()
    #     ax = fig.add_subplot(projection='3d')

    #     ax.set_box_aspect([1.0, 1.0, 1.0])

    #     # create a list that contains the mean of group of always 4 coordinates
    #     for i in range(0, len(self.__coordinates), 4):
    #         tag_coordinates = np.array(self.__coordinates[i:i + 4])
    #         tag_center = np.mean(tag_coordinates, axis=0)

    #         axis_y = transformations.get_normal_to_3d_points(tag_coordinates)
    #         axis_x = tag_coordinates[0, :] - tag_coordinates[1, :]
    #         axis_x = axis_x / np.linalg.norm(axis_x)
    #         axis_z = np.cross(axis_x, axis_y)
    #         if axis_z[2] < 0:
    #             axis_y = -axis_y
    #             axis_z = -axis_z

    #         # draw tag corner 0 blue
    #         ax.scatter(tag_coordinates[0,0], tag_coordinates[0,1], tag_coordinates[0,2],
    #                    c='b', marker=marker)
    #         # draw the other 3 corners black
    #         ax.scatter(tag_coordinates[1:, 0], tag_coordinates[1:, 1], tag_coordinates[1:, 2],
    #                    c='k', marker=marker)

    #         # draw a frame with the tag convention (x- left, y- out, z- up)
    #         ax.quiver(tag_center[0], tag_center[1], tag_center[2],
    #                   axis_x[0], axis_x[1], axis_x[2], length=1.0, color='r')
    #         ax.quiver(tag_center[0], tag_center[1], tag_center[2],
    #                   axis_y[0], axis_y[1], axis_y[2], length=1.0, color='g')
    #         ax.quiver(tag_center[0], tag_center[1], tag_center[2],
    #                   axis_z[0], axis_z[1], axis_z[2], length=1.0, color='b')

    #     x_limits = ax.get_xlim3d()
    #     y_limits = ax.get_ylim3d()
    #     z_limits = ax.get_zlim3d()

    #     x_range = abs(x_limits[1] - x_limits[0])
    #     x_middle = np.mean(x_limits)
    #     y_range = abs(y_limits[1] - y_limits[0])
    #     y_middle = np.mean(y_limits)
    #     z_range = abs(z_limits[1] - z_limits[0])
    #     z_middle = np.mean(z_limits)

    #     # the plot bounding box is a sphere in the sense of the infinity
    #     # norm, hence I call half the max range the plot radius.
    #     plot_radius = 0.5 * max([x_range, y_range, z_range])

    #     ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    #     ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    #     ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])

    #     # set the labels
    #     ax.set_xlabel('x')
    #     ax.set_ylabel('y')
    #     ax.set_zlabel('z')

    #     plt.show()

    def apply_transformation_matrix_from_points_for_transformation(self, path: str,
                                                                   file_name: str) -> None:
        """
        Applies the transformation matrix from points for transformation
        """
        self.apply_transformation_matrix(
            transformations.get_transformation_matrix_from_points_from_xlsx(
                path, file_name))

    def create_kml_polygon_from_coordinates(self, kml: simplekml.Kml,
                                            file_name: str,
                                            hex_color_idx: int) -> simplekml.Polygon:
        """
        Create a polygon with the defined points and extrude it
        """
        polygon = kml.newpolygon(name=file_name)

        self.append(self.get_coordinate(0))
        polygon.outerboundaryis = self.__coordinates
        self.pop()

        polygon.extrude = 1  # set extrude to 1 to enable extrusion
        polygon.altitudemode = simplekml.AltitudeMode.absolute  # set the altitude mode to absolute
        polygon.polystyle.color = simplekml.Color.hex(textcolor.HEX_COLOR_LIST[hex_color_idx])

        return polygon

    def create_kml_for_google_earth(self, path: str,
                                    file_name: str,
                                    hex_color_idx: int = 0) -> None:
        """
        Create a kml file for google earth from the CoordinateList
        """
        path = helper.create_subdir_if_not_exists(os.path.join(path, "models"), "kml")

        # create a new KML object
        kml = simplekml.Kml()

        # create a polygon with the defined points and extrude it
        self.create_kml_polygon_from_coordinates(kml, os.path.splitext(file_name)[0], hex_color_idx)

        # save the KML file
        kml.save(os.path.join(path, file_name))