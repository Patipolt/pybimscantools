"""
Catenda Hub (Bimsync) REST API V2 Module Python Class created by 
Thanuphol Patipol (TP), thau on 29 SEP 2023 to do all the jobs 
relating to communication tasks done with Catenda Hub Server 
herein after referred as BIM_XD
"""

import json
import threading
import time

import requests

from pybimscantools import bimxdbcf
from pybimscantools import bimxdlibrary
from pybimscantools import captureauthcode
from pybimscantools import textcolor

# Catenda Hub user related information
CLIENT_ID = ""
CLIENT_SECRET = ""
REDIRECT_URI = "http://127.0.0.1:5000/callback"

# Catenda Hub project related information
TEST_PROJECT_1_ID = ""
TEST_PROJECT_2_ID = ""
TEST_PROJECT_3_ID = ""
TEST_PROJECT_4_ID = ""


# BIM_XD Class
class BimXd:
    """BimXd class for doing all the jobs relating to communication tasks"""

    _authorize_url = "https://api.catenda.com/oauth2/authorize?"
    _token_url = "https://api.catenda.com/oauth2/token"
    _base_url = "https://api.catenda.com/v2/projects/"

    def __init__(self, project: str = "project1") -> None:
        projects = {
            "project1": TEST_PROJECT_1_ID,
            "project2": TEST_PROJECT_2_ID,
            "project3": TEST_PROJECT_3_ID,
            "project4": TEST_PROJECT_4_ID,
            
        }
        if project not in projects:
            project_id = None
            print(textcolor.colored_text(f"Project {project} not found", "Red"))
        else:
            project_id = projects[project]

        self.p_client_id = CLIENT_ID  # setter method
        self.p_client_secret = CLIENT_SECRET  # setter method
        self.p_redirect_uri = REDIRECT_URI  # setter methodำ
        self.p_project_id = project_id  # setter method
        self.p_access_token = None  # setter method, initialize to None
        self.p_authorization_code = None  # setter method, initialize to None
        self.library = None
        self.bcf = None

    # @property decorator and setter shouldn't be called recursively.
    @property
    def p_client_id(self):  # Method of accessing this variable
        return self.client_id  # Variable

    @p_client_id.setter
    def p_client_id(self, value):  # Method of setting this variable
        self.client_id = value  # Variable

    @property
    def p_client_secret(self):
        return self.client_secret

    @p_client_secret.setter
    def p_client_secret(self, value):
        self.client_secret = value

    @property
    def p_redirect_uri(self):
        return self.redirect_uri

    @p_redirect_uri.setter
    def p_redirect_uri(self, value):
        self.redirect_uri = value

    @property
    def p_project_id(self):
        return self.project_id

    @p_project_id.setter
    def p_project_id(self, value):
        self.project_id = value

    @property
    def p_access_token(self):
        return self.access_token

    @p_access_token.setter
    def p_access_token(self, value):
        self.access_token = value

    @property
    def p_authorization_code(self):
        return self.authorization_code

    @p_authorization_code.setter
    def p_authorization_code(self, value):
        self.authorization_code = value

    @property
    def p_base_url(self):
        return self._base_url

    @p_base_url.setter
    def p_base_url(self, value):
        self._base_url = value

    @staticmethod
    def convert_to_string(data_input: dict) -> str:
        """Function for converting a python dictionary to a JSON-formatted string"""
        str_json = json.dumps(data_input, indent=4, sort_keys=True)
        return str_json

    @staticmethod
    def convert_to_json(data_input: str) -> dict:
        """Function for converting a JSON to a JSON-formatted dictionary"""
        json_data = json.loads(data_input)
        return json_data

    @staticmethod
    def replace_double_quote(data_input: str) -> str:
        """Function for replacing double quotes with single quotes"""
        ret_data = data_input.replace('"', "'")
        return ret_data

    @staticmethod
    def replace_single_quote(data_input: str) -> str:
        """Function for replacing single quotes with double quotes"""
        ret_data = data_input.replace("'", '"')
        return ret_data

    def client_credentials_grant(self) -> str:
        """Function for getting the access token without user authorization"""
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        body = (
            f"grant_type=client_credentials&"
            f"client_id={self.p_client_id}&"
            f"client_secret={self.p_client_secret}&"
        )
        try:
            response = requests.post(
                self._token_url, headers=header, data=body, timeout=5
            )
        except Exception as e:
            print(textcolor.colored_text(f"{e}", "Red"))

        if response.status_code == 200:
            ret_json = response.json()
            self.p_access_token = ret_json["access_token"]
            print(
                textcolor.colored_text(
                    f"Access Code ({self.p_access_token}) Received", "Green"
                )
            )
            # if successful, return Access_Token
            return self.p_access_token
        else:
            print(textcolor.colored_text(f"{response.status_code} Bad Request", "Red"))
            # if unsuccessful, return 0 and print out error
            return 0

    def get_authorization_code(self) -> None:
        """Function for getting the authorization code"""
        call_url = (
                self._authorize_url
                + "client_id="
                + self.p_client_id
                + "&response_type=code&redirect_uri="
                + self.p_redirect_uri
        )
        # print the url for the user to click and open an external web browser
        # to do the authorization
        print(
            textcolor.colored_text(
                "Click the link below to open up a web-browser for"
                "authorization process!\nAfter authorization, "
                "the web-browser can be closed!\n↓",
                "Yellow",
            )
        )
        print(textcolor.colored_text(call_url, "Violet"))

        def run_flask_app(flask_app: captureauthcode.CaptureAuthCode) -> None:
            """Masking the function for threading"""
            try:
                flask_app.run()
            except Exception as e:
                print(textcolor.colored_text(f"{e}", "Red"))

        # Creating an object from a CaptureAuthCode
        flask_app_obj = captureauthcode.CaptureAuthCode()

        # Define a thread and run
        t = threading.Thread(target=run_flask_app, args=(flask_app_obj,))
        t.start()

        # Wait until auth_code is set
        while flask_app_obj.authorization_code is None:
            time.sleep(1)
        self.authorization_code = flask_app_obj.authorization_code

        # This function gets the authorization code by running a flask app
        # and listening to a specific endpoint. When the user gives permission
        # to the application, the server will send a feedback to the specific
        # place which in this case is http://127.0.0.1:5000/callback, which is
        # the place where the flask is listening to. Usually setting place
        # where server responses can be set on the server's application side.

    def get_access_token(self) -> str:
        """Function for getting the access token"""
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        body = (
            f"grant_type=authorization_code&"
            f"code={self.p_authorization_code}&"
            f"redirect_uri={self.p_redirect_uri}&"
            f"client_id={self.p_client_id}&"
            f"client_secret={self.p_client_secret}&"
        )
        try:
            response = requests.post(
                self._token_url, headers=header, data=body, timeout=5
            )
        except Exception as e:
            print(textcolor.colored_text(f"{e}", "Red"))

        if response.status_code == 200:
            ret_json = response.json()
            self.p_access_token = ret_json["access_token"]
            print(
                textcolor.colored_text(
                    f"Access Code ({self.p_access_token}) Received", "Green"
                )
            )
            # if successful, return Access_Token
            return self.p_access_token
        else:
            print(textcolor.colored_text(f"{response.status_code} Bad Request", "Red"))
            # if unsuccessful, return 0 and print out error
            return 0

        # After creating an instance of BimXD and a calling of get_authorization_code(),
        # first thing that needs to be called is this get_access_token
        # in order to get the token for further requests.

    def setup_library(self, project: str = "HT_Bridge_Inspection") -> None:
        """This function binds up the library class to the BimXD class"""
        projects = {
            "project1": TEST_PROJECT_1_ID,
            "project2": TEST_PROJECT_2_ID,
            "project3": TEST_PROJECT_3_ID,
            "project4": TEST_PROJECT_4_ID,
        }
        if project not in projects:
            library_id = None
            print(textcolor.colored_text(f"Project {project} not found", "Red"))
        else:
            library_id = projects[project]
            self.library = bimxdlibrary.Library(library_id, self)

    def setup_bcf(self) -> None:
        """This function binds up the BCF class to the BimXD class"""
        self.bcf = bimxdbcf.BCF(self)
