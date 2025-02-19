import requests
import json
import os
from pybimscantools import textcolor

# MarkersBackend Class
class MarkersBackend:
    """Class to handle the communication with the MarkersBackend API."""

    _server = "https://humantech.dev/"
    _upload_markers_url = None
    _upload_relative_corners_url = None
    _get_relative_corners_url = None
    _get_relative_corners_type_url = None
    _delete_relative_corners_url = None

    def __init__(self, sitename : str, project_id: str) -> None:
        """Initializes the MarkersBackend class."""
        self.site_name = sitename
        self._upload_markers_url = f"project/{project_id}/markers/"
        self._upload_relative_corners_url = f"project/{project_id}/relative_corners/"
        self._get_relative_corners_url = f"project/{project_id}/relative_corners/"
        self._get_relative_corners_type_url = f"project/{project_id}/relative_corners/type/"
        self._delete_relative_corners_url = f"project/{project_id}/relative_corners/"
    
    def upload_markers(self) -> bool:
        """Uploads the markers to the MarkersBackend API.

        Returns:
            bool: True if the upload was successful, False otherwise.
        """
        file = os.path.join(self.site_name, "markers", "markers_ifc.xlsx")
        uploading_file = {'marker_file': open(file, 'rb')}

        try:
            response = requests.post(self._server + self._upload_markers_url, files=uploading_file, timeout=5)
            if response.status_code == 200:
                print(textcolor.colored_text(f"File ({file}) uploaded to the server", "Green"))
                return True
            elif response.status_code == 422:
                print(textcolor.colored_text(f"{response.status_code} Validation Error", "Red"))
                return False
            else:
                print(textcolor.colored_text(f"Failed to fetch data. Status code: {response.status_code}",
                "Red"))
                return False
        except Exception as e:
            print(textcolor.colored_text(f"{e}", "Red"))

    def upload_relative_corners(self,
                                corners_type: str,
                                file_name: str = "relative_corners_tag_chilli.xlsx") -> bool:
        """Uploads the markers to the MarkersBackend API.

        Args:
            corner_id: id that you will upload specific relative corner to the server.

        Returns:
            bool: True if the upload was successful, False otherwise.
        """
        file = os.path.join(self.site_name, "markers", file_name)
        uploading_file = {'corner_file': open(file, 'rb')}
        params = {'type': corners_type}
        try:
            response = requests.post(self._server + self._upload_relative_corners_url,
                                     params=params,
                                     files=uploading_file,
                                     timeout=5)
            # print(response.url)
            if response.status_code == 200:
                print(textcolor.colored_text(f"File ({file}) uploaded to the server", "Green"))
                return True
            elif response.status_code == 422:
                print(textcolor.colored_text(f"{response.status_code} Validation Error", "Red"))
                return False
            else:
                print(textcolor.colored_text(f"Failed to fetch data. Status code: {response.status_code}",
                "Red"))
                return False
        except Exception as e:
            print(textcolor.colored_text(f"{e}", "Red"))

    def get_relative_corners(self, corners_type: str) -> bool:
        """Reads the corners from the MarkersBackend API.

        Args:
            corner_id: id of the marker you want to get the info..

        Returns:
            bool: True if the request was successful, False otherwise.
        """
        params = {'type': corners_type}
        try:
            response = requests.get(self._server + self._get_relative_corners_url,
                                    params=params,
                                    timeout=5)
            
            if response.status_code == 200:
                print(textcolor.colored_text("Relative Corners read from the server", "Orange"))
                str_json = json.loads(response.content)
                str_json = json.dumps(str_json, indent=4, sort_keys=True)
                print(textcolor.colored_text(str_json , "Pale"))
                return True
            elif response.status_code == 422:
                print(textcolor.colored_text(f"{response.status_code} Validation Error", "Red"))
                return False
            else:
                print(textcolor.colored_text(f"Failed to fetch data. Status code: {response.status_code}",
                "Red"))
                return False
        except Exception as e:
            print(textcolor.colored_text(f"{e}", "Red"))
    
    def get_relative_corners_type(self) -> bool:
        """Reads what ids are already existing in the server.

        Returns:
            bool: True if the request was successful, False otherwise.
        """
        try:
            response = requests.get(self._server + self._get_relative_corners_type_url, timeout=5)
            if response.status_code == 200:
                print(textcolor.colored_text("Relative Corners read from the server", "Orange"))
                str_json = json.loads(response.content)
                str_json = json.dumps(str_json, indent=4, sort_keys=True)
                print(textcolor.colored_text(str_json , "Pale"))
                return True
            elif response.status_code == 422:
                print(textcolor.colored_text(f"{response.status_code} Validation Error", "Red"))
                return False
            else:
                print(textcolor.colored_text(f"Failed to fetch data. Status code: {response.status_code}",
                "Red"))
                return False
        except Exception as e:
            print(textcolor.colored_text(f"{e}", "Red"))
    
    def delete_relative_corners(self, corners_type: str = "relative_tag_corners") -> bool:
        """Deletes the corners according to the id specified from the server

        Args:
            corner_id: id of the marker you want to delete from the server.

        Returns:
            bool: True if the delete was successful, False otherwise.
        
        """
        params = {'type': corners_type}
        try:
            response = requests.delete(self._server + self._delete_relative_corners_url,
                                    params=params,
                                    timeout=5)
            
            if response.status_code == 200:
                print(textcolor.colored_text("Relative Corners deleted from the server", "Orange"))
                str_json = json.loads(response.content)
                str_json = json.dumps(str_json, indent=4, sort_keys=True)
                print(textcolor.colored_text(str_json , "Pale"))
                return True
            elif response.status_code == 422:
                print(textcolor.colored_text(f"{response.status_code} Validation Error", "Red"))
                return False
            else:
                print(textcolor.colored_text(f"Failed to fetch data. Status code: {response.status_code}",
                "Red"))
                return False
        except Exception as e:
            print(textcolor.colored_text(f"{e}", "Red"))