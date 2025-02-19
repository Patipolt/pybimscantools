"""
This example shows how to use the marker workflow. Furthermore, it shows how to upload and download the corresponding
informatin to and from the backend. In the example here all the data is already with respect to the IFC frame. It is
assumed that within the project directory there is a subdirectory called "markers" containing the file "markers_ifc.xlsx"
and the file "relative_corners_tag_00.xlsx".
"""

import os

from pybimscantools import markersbackend as mkb

from pybimscantools import markers


# name of the project directory
project_name = "EXAMPLE_SANDBOX"

# create relative path to the project
path = os.path.join(os.path.join(os.path.dirname(os.getcwd()), "Data", project_name))


# # apply transformation matrix to given markers.xlsx and save as markers_ifc.xlsx
# markers.apply_transformation_matrix_to_markers_xlsx_and_copy(site_name, T_lv95_to_ifc)

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