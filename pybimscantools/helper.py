import os


def does_file_name_exist_in_path(path: str, file_name: str) -> bool:
    """
    Function that takes a path and a file_name and checks if the file exists in the path
    """

    for file in os.listdir(path):
        if file == file_name:
            return True
    return False


def create_subdir_if_not_exists(path: str, sub_dir_name: str) -> str:
    """
    Function that takes a path and a sub_dir_name and creates a subdirectory if it does not exist
    """

    sub_dir = os.path.join(path, sub_dir_name)
    if not os.path.isdir(sub_dir):
        os.mkdir(sub_dir)
    return sub_dir

# def remove_and_create_subdir(path: str, sub_dir_name: str) -> str:
#     """
#     Function that takes a path and a sub_dir_name and creates a subdirectory if it does not exist
#     """
#
#     sub_dir = os.path.join(path, sub_dir_name)
#     if os.name == 'nt':  # windows
#         cmd = f'rm -rf "{sub_dir}"'
#     else:  # unix/linux
#         cmd = f'rm -rf "{sub_dir}"'
#     os.system(cmd)
#     os.mkdir(sub_dir)
#     return sub_dir
