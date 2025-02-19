import copy
import os

import simplekml

from pybimscantools import coordinatelist as cl
from pybimscantools import helper

class CoordinateModel:
    """
    CoordinateModel class containing a list of CoordinateLists
    """

    def __init__(self, coordinate_list: cl.CoordinateList = None) -> None:
        self.__coordinate_lists = []
        if isinstance(coordinate_list, cl.CoordinateList):
            self.__coordinate_lists.append(coordinate_list)

    def __getitem__(self, i: int) -> cl.CoordinateList:
        """
        Return the i-th entry of the CoordinateList
        """
        return self.__coordinate_lists[i]

    def copy(self) -> 'CoordinateModel':
        """
        Create a copy of a CoordinateModel object
        """
        return copy.deepcopy(self)

    def append(self, coordinate_list: cl.CoordinateList) -> None:
        """
        Append a CoordinateList to the end of the list
        """
        self.__coordinate_lists.append(coordinate_list)

    def pop(self) -> None:
        """
        Pop a CoordinateList from the end of the list
        """
        self.__coordinate_lists.pop()

    def len(self) -> int:
        """
        Return the number of CoordinateLists in the list
        """
        return len(self.__coordinate_lists)

    def last_idx(self) -> int:
        """
        Return the number of CoordinateLists in the list - 1
        """
        return self.len() - 1

    def get_coordinate_list(self, i: int) -> cl.CoordinateList:
        """
        Return the i-th entry of the CoordinateList
        """
        return self.__coordinate_lists[i]

    def set_height_all(self, height: float) -> None:
        """
        Set the height of the CoordinateLists contained in the CoordinateModel
        """
        for coordinate_list in self.__coordinate_lists:
            coordinate_list.set_height(height)
    
    def shift_height_all(self, delta: float) -> None:
        """
        Shift the height of the CoordinateLists contained in the CoordinateModel
        """
        for coordinate_list in self.__coordinate_lists:
            coordinate_list.shift_height(delta)

    def set_height_coordinate_list_i(self, i: int, height: float) -> None:
        """
        Set the height of the CoordinateList i
        """
        self.__coordinate_lists[i].set_height(height)

    def shift_height_coordinate_list_i(self, i: int, delta: float) -> None:
        """
        Shift the height of the CoordinateList i
        """
        self.__coordinate_lists[i].shift_height(delta)

    def get_height_coordinate_list_i(self, i: int) -> float:
        """
        Return the height of the CoordinateList i
        """
        return self.__coordinate_lists[i].get_height()

    def transform_from_lv95_to_google_earth(self) -> None:
        """
        Transform all CoordinateLists from lv95 to google earth
        """
        for coordinate_list in self.__coordinate_lists:
            coordinate_list.transform_from_lv95_to_google_earth()

    def apply_transformation_matrix(self, t: list) -> None:
        """
        Apply a transformation matrix to all CoordinateLists
        """
        for coordinate_list in self.__coordinate_lists:
            coordinate_list.apply_transformation_matrix(t)

    def transform_from_lv95_to_etrf93_geographic(self) -> None:
        """ 
        Apply lv95 to etrf93 geographic transformation to all 
        CoordinateLists using swissreframe
        """
        for coordinate_list in self.__coordinate_lists:
            coordinate_list.transform_from_lv95_to_etrf93_geographic()

    def transform_from_lv95_to_etrf93_geocentric(self) -> None:
        """
        Apply lv95 to etrf93 geocentric transformation to all
        CoordinateLists using swissreframe
        """
        for coordinate_list in self.__coordinate_lists:
            coordinate_list.transform_from_lv95_to_etrf93_geocentric()

    def transform_from_etrf93_geographic_to_lv95(self) -> None:
        """
        Apply etrf93 geographic to lv95 transformation to all 
        CoordinateLists using swissreframe
        """
        for coordinate_list in self.__coordinate_lists:
            coordinate_list.transform_from_etrf93_geographic_to_lv95()

    def transform_from_etrf93_geocentric_to_lv95(self) -> None:
        """
        Apply etrf93 geocentric to lv95 transformation to all 
        CoordinateLists using swissreframe
        """
        for coordinate_list in self.__coordinate_lists:
            coordinate_list.transform_from_etrf93_geocentric_to_lv95()

    def print(self) -> None:
        """
        Print the coordinates of all CoordinateLists
        """
        cntr = 0
        for coordinate_list in self.__coordinate_lists:
            print("CoordinateList " + str(cntr) + ":")
            coordinate_list.print()
            cntr += 1

    def plot(self, i: int) -> None:
        """
        Plot the coordinates of the CoordinateList i in 3D
        """
        self.__coordinate_lists[i].plot()

    def apply_transformation_matrix_from_points_for_transformation(self,
                                                                   path: str,
                                                                   file_name: str) -> None:
        """
        Apply a transformation matrix from points for transformation
        """
        for coordinate_list in self.__coordinate_lists:
            coordinate_list.apply_transformation_matrix_from_points_for_transformation(
                path, file_name)

    def create_kml_for_google_earth(self, path: str, file_name: str) -> None:
        """
        Create a KML file for google earth from the CoordinateList
        """
        path = helper.create_subdir_if_not_exists(os.path.join(path, "models"), "kml")

        # create a new KML object
        kml = simplekml.Kml()
        cntr = 0
        hex_color_idx = 0
        for coordinate_list in self.__coordinate_lists:
            # create a polygon with the defined points and extrude it
            coordinate_list.create_kml_polygon_from_coordinates(kml,
                                                                os.path.splitext(file_name)[0] +
                                                                "_" + str(cntr),
                                                                hex_color_idx)
            cntr += cntr
            hex_color_idx += 1
            if hex_color_idx == self.len():
                hex_color_idx = 0

        # save the KML file
        kml.save(os.path.join(path, file_name))
