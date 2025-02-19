"""
This example shows how to communicate with BIMXD.
It shows how to upload and download files from BIMXD.
It also shows how to create and delete BCF issues.
"""

import os
from pybimscantools import bimxd

# name of the project directory
project_name = "KSA"

# create relative path to the project
path = os.path.join(os.path.join(os.path.dirname(os.getcwd()), "Data", project_name))


bimxd_project_name = "HT_" + project_name
bimxd_project_name_test = "HT_Testproject_playground"

# Setting up BIMXD
bim_xd = bimxd.BimXd(project=bimxd_project_name_test)
# bim_xd.get_authorization_code()   # for normal project, not for special account used in this project
# bim_xd.get_access_token(grant_type='authorization_code')  # for normal project, not for special account used in this project
bim_xd.client_credentials_grant()
bim_xd.setup_library(project=bimxd_project_name_test)

# Library
bim_xd.library.list_library_items(list_all=True)
# Uploading a file or creating a folder to\in BIMXD
bim_xd.library.create_library_item(None, int(input("Please insert the number of folder for the uploading file(s)!, -1 otherwise:")), True)
bim_xd.library.list_library_items(list_all=True)
# Downloading a file from BIMXD
# bim_xd.library.download_library_item([2], save_to="C:\\Users\\thau_local\\Desktop")
# Uploading project results
# bim_xd.library.upload_project_results(path)

# BCF
bim_xd.setup_bcf()
bim_xd.bcf.get_issue_boards()
bim_xd.bcf.get_topics(1)
# Creating a BCF issue
# bim_xd.bcf.create_topics(
#     issue_board_no=1,
#     bcf_name="BCF_Workshop_<Preparation>",
#     bcf_type="Warning",
#     bcf_status="Open",
#     bcf_description="This BCF is for testing purposes only. It has no real meaning.",
#     bcf_labels=["Drone", "Thermal Drone"],
#     assigned_to="thau@zhaw.ch",
#     creation_author="thau@zhaw.ch"
# )
# Deleting a BCF issue
# bim_xd.bcf.delete_topics(1, [1])

