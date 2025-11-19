"""
BCF Class supporting the Bimsync Library REST API V2 Module
"""

import requests

from pybimscantools import bimxd
from pybimscantools import textcolor


class BCF:
    """BCF Class supporting the Bimsync Library REST API V2 Module"""

    _based_url = "https://api.catenda.com/opencde/bcf/2.1/projects"

    # Constructor
    def __init__(self, parent: "bimxd.BimXd") -> None:
        self.parent = parent  # Passing the parent class into this class initialization
        self.issue_array = []
        self.topic_array = []

    def get_issue_boards(self) -> int:
        """This function gets issue boards from Bimsync"""

        def list_issue_board(ret_json: list) -> None:
            """Helper function to list issue boards"""
            self.issue_array = []
            for i, element in enumerate(ret_json):
                print(f"{i + 1}\t{element['name']}")
                self.issue_array.append(
                    [i + 1, element["name"], element["project_id"]])

        call_url = self._based_url + "?bimsync_project_id=" + self.parent.p_project_id
        header = {
            "Authorization": f"Bearer {self.parent.p_access_token}",
            "Content-Type": "application/json",
        }

        # Start getting the issue boards
        try:
            response = requests.get(call_url, headers=header, timeout=5)
            if response.status_code == 200:
                ret_json = response.json()  # Assuming the response contains JSON data
                print(textcolor.colored_text("List of issue boards", "Orange"))
                # print(textcolor.colored_text(f"{self.parent.convert_to_string(ret_json)}", "Green"))
                list_issue_board(ret_json)
                # if successful, return 1 and list all the issue boards contained in the project
                return 1
            elif response.status_code == 400:
                print(
                    textcolor.colored_text(
                        f"{response.status_code} Bad Request", "Red")
                )
                # if unsuccessful, return 0 and print out error
                return 0
            elif response.status_code == 403:
                print(
                    textcolor.colored_text(
                        f"{response.status_code} Not Found", "Red")
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
        except Exception as e:
            print(textcolor.colored_text(f"{e}", "Red"))

    def create_issue_board(self, issue_name: str = "Board") -> int:
        """Create issue board (Works but the returned JSON seems to be wrong (ask Dag)"""
        call_url = self._based_url
        header = {
            "Authorization": f"Bearer {self.parent.p_access_token}",
            "Content-Type": "application/json",
        }
        body = (
                '{"name": "'
                + issue_name
                + '",\
                "bimsync_project_id": "'
                + self.parent.p_project_id
                + '"}'
        )

        # Start creating the issue board
        try:
            response = requests.post(
                call_url, headers=header, data=body, timeout=5)
            if response.status_code == 200 or response.status_code == 201:
                # print(textcolor.colored_text(f"{response.text}", "Green"))
                print(
                    textcolor.colored_text(
                        f"Issue board ({issue_name}) created and re-listing the issue board",
                        "Green",
                    )
                )
                self.get_issue_boards()
                # if successful, return 1 and print out success
                return 1
            elif response.status_code == 400:
                print(
                    textcolor.colored_text(
                        f"{response.status_code} Bad Request", "Red")
                )
                # if unsuccessful, return 0 and print out error
                return 0
            elif response.status_code == 403:
                print(
                    textcolor.colored_text(
                        f"{response.status_code} Forbidden", "Red")
                )
                # if unsuccessful, return 0 and print out error
                return 0
            elif response.status_code == 404:
                print(
                    textcolor.colored_text(
                        f"{response.status_code} Not Found", "Red")
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

    def get_topics(self, issue_board_no: int = 1) -> int:  # This is to list BCF issues
        """Get topics (BCF issues)"""

        def list_bcf_issues(ret_json: list) -> None:
            """Helper function to list BCF issues"""
            self.topic_array = []
            for i, element in enumerate(ret_json):
                print(f"{i + 1}\t{element['title']}")
                self.topic_array.append(
                    [i + 1, element["title"], element["guid"]])

        if 1 <= issue_board_no <= len(self.issue_array):
            print(textcolor.colored_text("List of BCF issues", "Orange"))
            # Finding the project_id from the Issue_Array
            issue_board_no -= 1  # index starts from 0
            issue_board_id = self.issue_array[issue_board_no][2]

            call_url = self._based_url + "/" + issue_board_id + "/topics"
            header = {
                "Authorization": f"Bearer {self.parent.p_access_token}",
                "Content-Type": "application/json",
            }

            # Start getting the topics
            try:
                response = requests.get(call_url, headers=header, timeout=5)
                if response.status_code == 200:
                    ret_json = (
                        response.json()
                    )  # Assuming the response contains JSON data
                    list_bcf_issues(ret_json)
                    # if successful, return 1 and list bcf issues
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
        else:
            print(textcolor.colored_text("issue_board_no is out of range", "Red"))

    def create_topics(
            self,
            issue_board_no: int = 1,
            bcf_name: str = "",
            bcf_type: str = "",
            bcf_status: str = "",
            bcf_description: str = "",
            bcf_labels: list = None,
            assigned_to: str = "",
            creation_author: str = "",
    ) -> int:
        """Create topic (BCF issue) works, but the returned JSON seems to be wrong (ask Dag)"""
        if 1 <= issue_board_no <= len(self.issue_array):
            issue_board_id = self.issue_array[issue_board_no - 1][2]
            call_url = self._based_url + "/" + issue_board_id + "/topics"
            header = {
                "Authorization": f"Bearer {self.parent.p_access_token}",
                "Content-Type": "application/json",
            }
            # String in JSON format
            body = '{"title": "' + bcf_name + '",\
                    "topic_type": "' + bcf_type + '",\
                    "topic_status": "' + bcf_status + '",\
                    "assigned_to": "' + assigned_to + '",\
                    "creation_author": "' + creation_author + '",\
                    "labels": ' + bimxd.BimXd.replace_single_quote(str(bcf_labels)) + ',\
                    "description": "' + bcf_description + '"}'

            # Start creating the topics
            try:
                response = requests.post(
                    call_url, headers=header, data=body, timeout=5)
                if response.status_code == 200 or response.status_code == 201:
                    # ret_json = response.json() # Assuming the response contains JSON data
                    # print(textcolor.colored_text(f"{ret_json}", "Green"))
                    print(
                        textcolor.colored_text(
                            f"Topic ({bcf_name}) created and re-listing the topics",
                            "Green",
                        )
                    )
                    self.get_topics(issue_board_no)
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
        else:
            print(textcolor.colored_text("issue_board_no is out of range", "Red"))

    def delete_topics(
            self, issue_board_no: int = 1, bcf_delete_list: list = None
    ) -> int:
        """Delete topic (BCF issue)"""
        if bcf_delete_list is None:
            bcf_delete_list = []
        issue_board_id = self.issue_array[issue_board_no - 1][2]
        for index in bcf_delete_list:
            if 1 <= index <= len(self.topic_array):
                index = int(index)
                index -= 1  # index starts from 0
                topic_id = self.topic_array[index][2]
                call_url = (
                        self._based_url + "/" + issue_board_id + "/topics/" + topic_id
                )
                header = {
                    "Authorization": f"Bearer {self.parent.p_access_token}",
                    "Content-Type": "application/json",
                }
                # print(index)
                # Start deleting the topics
                try:
                    response = requests.delete(
                        call_url, headers=header, timeout=5)
                    if response.status_code == 200 or response.status_code == 204:
                        # ret_json = response.json() # Assuming the response contains JSON data
                        # print(textcolor.colored_text(f"{ret_json}", "Green"))
                        print(
                            textcolor.colored_text(
                                "Topic(s) deleted", "Green"
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
            else:
                print(textcolor.colored_text(
                    "BCF issue is out of range", "Red"))
