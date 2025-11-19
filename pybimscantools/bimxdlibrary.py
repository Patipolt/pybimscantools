"""
Library Class supporting the Bimsync Library REST API V2 Module
"""

import os

import requests
import json

from pybimscantools import bimxd
from pybimscantools import textcolor


class Library:
    """ Library Class supporting the Bimsync Library REST API V2 Module """

    # Constructor
    def __init__(self, library_no: str, parent: 'bimxd.BimXd') -> None:
        self.library_id = library_no
        self.parent = parent  # Passing the parent class into this class initialization
        self.library_array = []
        self.num_items = 0
        self.counting = 0
        self.old_parent_id = None
        self.pageSize = 100

    def list_library_items(self, list_all: bool = False, verbose: bool = True) -> int:
        """ List all the items in the library if list_all is True, otherwise list only the folder """
        # Resetting the variables
        self.library_array = []
        self.num_items = 0
        self.counting = 0
        self.old_parent_id = None

        def print_folder(name: str, number: int, rank: int) -> None:
            """ Print the folder name with the number and rank """
            print(f"{number}", end="")
            for i in range(0, rank):
                print("\t", end="")
            print(f"[+]{name}")

        def print_file(name: str, number: int, rank: int) -> None:
            """ Print the file name with the number and rank """
            print(f"{number}", end="")
            for i in range(0, rank):
                print("\t", end="")
            print(f"{name}")

        def list_library_with_parent_id(ret_json: list, parent_id: str, rank: int = 0) -> int:
            """ Recursive function for listing items in the library
                It should list the items in a tree-view manner specified by rank """
            for i in range(0, self.num_items):
                if ret_json[i]["parentId"] == parent_id:
                    document = ret_json[i]["document"]
                    if document["type"] == "folder":
                        # Check if the parent_id is the same as the old_parent_id
                        if self.old_parent_id == parent_id:
                            # if yes, increase the rank by 1
                            rank += 1
                        item_id = ret_json[i]["id"]
                        name = ret_json[i]["name"]
                        # listing related info in self.Library_Array
                        self.library_array.append(
                            [self.counting, name, item_id, parent_id, rank]
                        )
                        self.counting += 1
                        if verbose:
                            print_folder(name, self.counting, rank)
                        # Update the old_parent_id to the current one
                        self.old_parent_id = item_id
                        # recall the same function again to find sub items inside the folder
                        list_library_with_parent_id(ret_json, item_id, rank)
                    elif document["type"] == "file":
                        if list_all:
                            # Check if the parent_id is the same as the old_parent_id
                            if self.old_parent_id == parent_id:
                                # if yes, increase the rank by 1
                                rank += 1
                            name = ret_json[i]["name"]
                            item_id = ret_json[i]["id"]
                            # listing related info in self.Library_Array
                            self.library_array.append(
                                [self.counting, name, item_id, parent_id, rank]
                            )
                            self.counting += 1
                            if verbose:
                                print_file(name, self.counting, rank)
                            # Update the old_parent_id to the current one
                            self.old_parent_id = item_id
        page = 1
        acc_json = json.loads("[]")
        while True:
            call_url = (
                    self.parent.p_base_url
                    + self.parent.p_project_id
                    + "/libraries/"
                    + self.library_id
                    + "/items"
                    # + "?pageSize="
                    # + str(self.pageSize)    
            )
            header = {
                "Authorization": f"Bearer {self.parent.p_access_token}",
                "Content-Type": "application/json",
            }
            params = {
                    "pageSize": str(self.pageSize),
                    "page": page
                    }

            try:
                # in GET request, the json, body is not typically used, use params instead to send the body
                response = requests.get(call_url, headers=header, params=params, timeout=5)
            except Exception as e:
                print(textcolor.colored_text(f"{e}", "Red"))

            if response.status_code == 200:
                ret_json = response.json()  # Assuming the response contains JSON data
                # print(self.parent.convert_to_string(ret_json))
                self.num_items = len(ret_json)
                if verbose:
                    print(textcolor.colored_text(f"Number of items: {self.num_items} in page {page}", "Orange"))
                # Accumulate the ret_json data
                if page == 1:
                    acc_json = ret_json
                else:
                    acc_json += ret_json
                if self.num_items < self.pageSize:
                    break
                page += 1
                # print(self.Library_Array)
                # if successful, return 1 and list all the items contained in the library
                
            elif response.status_code == 400:
                print(
                    textcolor.colored_text(
                        f"{response.status_code} Bad Request", "Red"
                    )
                )
                # if unsuccessful, return 0 and print out error
                return 0
            elif response.status_code == 403:
                print(
                    textcolor.colored_text(
                        f"{response.status_code} Not Found", "Red"
                    )
                )
                # if unsuccessful, return 0 and print out error
                return 0
            else:
                print(
                    textcolor.colored_text(
                        f"Failed to fetch data. Status code: {response.status_code}",
                        "Red",
                    )
                )
                print(textcolor.colored_text(f"{response.content}", "Red"))
                # if unsuccessful, return 0 and print out error
                return 0
        if verbose:
            print(textcolor.colored_text("List of the library", "Orange"))
        # for debugging purpose, write the combined json to a file
        # with open('combined.json', 'w') as outfile:
        #     json.dump(acc_json, outfile, indent=4)
        self.num_items = len(acc_json)
        list_library_with_parent_id(acc_json, None, rank=0)
        # if successful, return 1 and list all the items contained in the library
        return 1

    def download_library_item(self, number: list, save_to: str = os.getcwd()) -> int:
        """ Get the id-specified item from the server and save it to the specified directory """
        # Finding the item_id from the Library_Array
        for index in number:
            # print(f"index is {index}")
            index -= 1  # index starts from 0
            item_id = self.library_array[index][2]
            name = self.library_array[index][1]
            print(
                textcolor.colored_text(f"Downloading {name} to {save_to}", "Orange")
            )

            # Constructing the call_url
            call_url = (
                    self.parent.p_base_url
                    + self.parent.p_project_id
                    + "/libraries/"
                    + self.library_id
                    + "/items/"
                    + item_id
            )
            header = {
                "Authorization": f"Bearer {self.parent.p_access_token}",
                "Accept": "application/octet-stream",
            }
            try:
                # Get octet-stream data from the server
                response = requests.get(call_url, headers=header, timeout=60)
                if response.status_code == 200:
                    file = response.content
                    # Save the file to the specified directory
                    with open(save_to + "/" + name, "wb") as f:
                        f.write(file)
                    print(
                        textcolor.colored_text(
                            f"File {name} saved to {save_to}", "Green"
                        )
                    )
                    # if successful, return 1 and print out success
                    return 1
                elif response.status_code == 400:
                    print(
                        textcolor.colored_text(
                            f"{response.status_code} Bad Request", "Red"
                        )
                    )
                    # if unsuccessful, return 0 and print out error
                    return 0
                elif response.status_code == 404:
                    print(
                        textcolor.colored_text(
                            f"{response.status_code} Not Found", "Red"
                        )
                    )
                    # if unsuccessful, return 0 and print out error
                    return 0
                else:
                    print(
                        textcolor.colored_text(
                            f"Failed to fetch data. Status code: {response.status_code}",
                            "Red",
                        )
                    )
            except Exception as e:
                print(textcolor.colored_text(f"{e}", "Red"))

    def create_library_item(self, file: str = None, folder_id: int = -1, create_folder: bool = False, folder_name: str = "New Folder") -> int:
        """ Create library item with binary data or create a folder """
        if not create_folder:
            # Extract only the name of the file form the path
            name = os.path.basename(file)
            # Constructing the Bimsync_Params
            bimsync_params = None
            if folder_id == -1:
                bimsync_params = '{"parentId": null, "name": "' + name + '", '
                bimsync_params += '"document": { "type": "file", "filename": "'
                bimsync_params += name
                bimsync_params += '"}}'
            else:
                # Finding the item_id (folder_id) from the library_array
                folder_id -= 1  # index starts from 0
                parent_id = self.library_array[folder_id][2]
                bimsync_params = (
                        '{"parentId": "' + parent_id + '", "name": "' + name + '", '
                )
                bimsync_params += '"document": { "type": "file", "filename": "'
                bimsync_params += name
                bimsync_params += '"}}'
            header = {
                "Authorization": f"Bearer {self.parent.p_access_token}",
                "Content-Type": "application/octet-stream",
                "Bimsync-Params": bimsync_params,
            }
        else:
            header = {
                    "Authorization": f"Bearer {self.parent.p_access_token}",
                    "Content-Type": "application/json",
                }
            if folder_id == -1:
                body =  (
                            '{"name": "' + folder_name + '",' +
                            '"parentId": null,' +
                            '"document": { "type": "folder"}}'
                )
            else:
                # Finding the item_id (folder_id) from the library_array
                folder_id -= 1  # index starts from 0
                parent_id = self.library_array[folder_id][2]
                body =  (
                            '{"name": "' + folder_name + '",' +
                            '"parentId": "' + parent_id + '",' +
                            '"document": { "type": "folder"}}'
                )
        
        # Constructing the call_url
        call_url = (
                self.parent.p_base_url
                + self.parent.p_project_id
                + "/libraries/"
                + self.library_id
                + "/items"
        )
        # Start uploading the file
        try:
            if not create_folder:
                # Upload data to the server
                with open(file, "rb") as f:
                    uploading_file = f.read()
                response = requests.post(call_url, headers=header, data=uploading_file, timeout=60)
            else:
                response = requests.post(call_url, headers=header, json=body, timeout=5)
            if response.status_code == 200:
                if not create_folder:
                    print(
                        textcolor.colored_text(
                            f"File ({file}) uploaded to the server", "Green"
                        )
                    )
                else:
                    print(
                        textcolor.colored_text(
                            f"Folder ({folder_name}) created", "Green"
                        )
                    )
                # if successful, return 1 and print out success
                return 1
            elif response.status_code == 400:
                print(
                    textcolor.colored_text(
                        f"{response.status_code} Bad Request", "Red"
                    )
                )
                # if unsuccessful, return 0 and print out error
                return 0
            elif response.status_code == 403:
                print(
                    textcolor.colored_text(
                        f"{response.status_code} Forbidden", "Red"
                    )
                )
                # if unsuccessful, return 0 and print out error
                return 0
            elif response.status_code == 404:
                print(
                    textcolor.colored_text(
                        f"{response.status_code} Not Found", "Red"
                    )
                )
                # if unsuccessful, return 0 and print out error
                return 0
            else:
                print(
                    textcolor.colored_text(
                        f"Failed to fetch data. Status code: {response.status_code}",
                        "Red",
                    )
                )
        except Exception as e:
            print(textcolor.colored_text(f"{e}", "Red"))
            return 0

    def create_library_item_with_parent_id(self, file: str, parent_id: str) -> int:
        """ Create library item with binary data with parent_id """
        name = os.path.basename(file)
        bimsync_params = (
                        '{"parentId": "' + parent_id + '", "name": "' + name + '", '
                )
        bimsync_params += '"document": { "type": "file", "filename": "'
        bimsync_params += name
        bimsync_params += '"}}'
        header = {
                "Authorization": f"Bearer {self.parent.p_access_token}",
                "Content-Type": "application/octet-stream",
                "Bimsync-Params": bimsync_params,
            }
        # Constructing the call_url
        call_url = (
                self.parent.p_base_url
                + self.parent.p_project_id
                + "/libraries/"
                + self.library_id
                + "/items"
        )
        # Start uploading the file
        try:
            # Upload data to the server
            with open(file, "rb") as f:
                uploading_file = f.read()
            response = requests.post(call_url, headers=header, data=uploading_file, timeout=60)
            if response.status_code == 200:
                print(
                    textcolor.colored_text(
                        f"File ({file}) uploaded to the server", "Green"
                    )
                )
                # if successful, return 1 and print out success
                return 1
            elif response.status_code == 400:
                print(
                    textcolor.colored_text(
                        f"{response.status_code} Bad Request", "Red"
                    )
                )
                # if unsuccessful, return 0 and print out error
                return 0
            elif response.status_code == 403:
                print(
                    textcolor.colored_text(
                        f"{response.status_code} Forbidden", "Red"
                    )
                )
                # if unsuccessful, return 0 and print out error
                return 0
            elif response.status_code == 404:
                print(
                    textcolor.colored_text(
                        f"{response.status_code} Not Found", "Red"
                    )
                )
                # if unsuccessful, return 0 and print out error
                return 0
            else:
                print(
                    textcolor.colored_text(
                        f"Failed to fetch data. Status code: {response.status_code}",
                        "Red",
                    )
                )
        except Exception as e:
            print(textcolor.colored_text(f"{e}", "Red"))
            return 0

    def upload_project_results(self, path: str) -> int:
        """ Upload all the project results to the library (depth maps, pose image, point clouds) """
        # Crate the folders for the project results
        project_folder_id = None
        images_folder_id = None
        depth_rendered_folder_id = None
        pose_embedded_folder_id = None
        point_clouds_folder_id = None
        transformed_folder_id = None
        # Ask the user which parent folder to upload the files
        if self.list_library_items(list_all=False, verbose=True):
            index_project_folder = int(input("Please insert the index of folder for the uploading file(s)!, -1 otherwise:"))
            project_folder_id = self.library_array[index_project_folder-1][2]  # index starts from 0
            # creating the images folder under the selected folder
            if self.create_library_item(None, index_project_folder, True, "images"):
                # list the library items to refresh the library_array
                self.list_library_items(list_all=False, verbose=False)
                index_images_folder = index_project_folder + 1
                images_folder_id = self.library_array[index_images_folder-1][2]
                # creating the subfolders for depth_rendered and pose_embedded
                if self.create_library_item(None, index_images_folder, True, "depth_rendered"):
                    # list the library items to refresh the library_array
                    self.list_library_items(list_all=False, verbose=False)
                    index_depth_rendered_folder = index_project_folder + 2
                    depth_rendered_folder_id = self.library_array[index_depth_rendered_folder-1][2]
                    if self.create_library_item(None, index_images_folder, True, "pose_embedded"):
                        # list the library items to refresh the library_array
                        self.list_library_items(list_all=False, verbose=False)
                        index_pose_embedded_folder = index_project_folder + 3
                        pose_embedded_folder_id = self.library_array[index_pose_embedded_folder-1][2]
                        if self.create_library_item(None, index_project_folder, True, "pointclouds"):
                            # list the library items to refresh the library_array
                            self.list_library_items(list_all=False, verbose=False)
                            index_point_clouds_folder = index_project_folder + 4
                            point_clouds_folder_id = self.library_array[index_point_clouds_folder-1][2]
                            if self.create_library_item(None, index_point_clouds_folder, True, "transformed"):
                                # list the library items to refresh the library_array
                                self.list_library_items(list_all=False, verbose=False)
                                index_transformed_folder = index_project_folder + 5
                                transformed_folder_id = self.library_array[index_transformed_folder-1][2]
                            else:
                                textcolor.colored_text("Failed to create the \"transformed\" folder", "Red")
                                return 0
                        else:
                            textcolor.colored_text("Failed to create the \"pointclouds\" folder", "Red")
                            return 0
                    else:
                        textcolor.colored_text("Failed to create the \"pose_embedded\" folder", "Red")
                        return 0
                else:
                    textcolor.colored_text("Failed to create the \"depth_rendered\" folder", "Red")
                    return 0
            else:
                textcolor.colored_text("Failed to create the \"images\" folder", "Red")
                return 0
        else:
            textcolor.colored_text("Failed to list the library items", "Red")
            return 0
        
        # Upload the project results
        # Upload the images inside the depth_rendered folder (only file)
        for file in os.listdir(os.path.join(path, "images/depth_rendered")):
            if os.path.isfile(os.path.join(path, "images/depth_rendered", file)):
                if not self.create_library_item_with_parent_id(os.path.join(path, "images/depth_rendered", file), depth_rendered_folder_id):
                    textcolor.colored_text(f"Failed to upload {file} to the depth_rendered folder", "Red")
                    return 0
        # Upload the images inside the pose_embedded folder (only file)
        for file in os.listdir(os.path.join(path, "images/pose_embedded")):
            if os.path.isfile(os.path.join(path, "images/pose_embedded", file)):
                if not self.create_library_item_with_parent_id(os.path.join(path, "images/pose_embedded", file), pose_embedded_folder_id):
                    textcolor.colored_text(f"Failed to upload {file} to the pose_embedded folder", "Red")
                    return 0
        # Upload the point clouds inside the point_clouds folder (only file)
        for file in os.listdir(os.path.join(path, "pointclouds")):
            if os.path.isfile(os.path.join(path, "pointclouds", file)):
                if not self.create_library_item_with_parent_id(os.path.join(path, "pointclouds", file), point_clouds_folder_id):
                    textcolor.colored_text(f"Failed to upload {file} to the pointclouds folder", "Red")
                    return 0
        # Upload the transformed point clouds inside the transformed folder (only file)
        for file in os.listdir(os.path.join(path, "pointclouds/transformed")):
            if os.path.isfile(os.path.join(path, "pointclouds/transformed", file)):
                if not self.create_library_item_with_parent_id(os.path.join(path, "pointclouds/transformed", file), transformed_folder_id):
                    textcolor.colored_text(f"Failed to upload {file} to the transformed folder", "Red")
                    return 0
        return 1

