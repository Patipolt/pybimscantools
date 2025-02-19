""" 
This class manipulates the ifcConvert.exe from ifcopenshell
to convert IFC files to COLLADA files
"""

import subprocess
import os
from importlib.resources import files
from pybimscantools import textcolor as tc


class IfcConvert:
    """This class manipulates the ifcConvert.exe from ifcopenshell"""

    def __init__(self) -> None:
        """Constructor"""

    def convert_to_collada(self, ifc_path: str, collada_path: str) -> int:
        """Convert IFC file to COLLADA file"""

        ifcconvert = os.path.join('pybimscantools', 'ifcConvert.exe')
        if not os.path.exists(ifcconvert):
            ifcconvert = files('pybimscantools')/('ifcConvert.exe')


        # Check if the directories exist
        if not os.path.exists(collada_path):
            os.makedirs(collada_path)

        for file in os.listdir(ifc_path):
            print(tc.colored_text(f"Converting {file} to COLLADA", "Orange"))
            ### Getting rid of file extension for further use
            file = file.strip(".ifc")
            ### Run the subprocess
            ### Specify the command used in the subprocess
            cli = [ifcconvert, f"{ifc_path}/{file}.ifc", f"{collada_path}/{file}.dae"]
            # Start the command as a separate process
            process = subprocess.Popen(
                cli,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,  # Use text=True to get output as a string (Python 3.7+)
                bufsize=1,  # Use line-buffering to get real-time output
                universal_newlines=True,  # Use universal_newlines=True to handle newlines correctly
            )

            # Read the output and error streams in real-time
            for line in process.stdout:
                text = ""
                # Remove any weird whitespaces
                for count in range(0, len(line) - 1):
                    if line[count] != chr(0):
                        text = text + line[count]
                print(tc.colored_text(text, "Pink"))

            for line in process.stderr:
                err_str = ""
                # Remove any weird whitespaces
                for count in range(0, len(line) - 1):
                    if line[count] != chr(0):
                        err_str = err_str + line[count]
                print(err_str)

            # Wait for the process to complete
            process.wait()

            # Get the return code of the command
            return_code = process.returncode
            if return_code == 0:
                print(tc.colored_text(f"{file}.dae converted successfully.", "Green"))
                print(
                    tc.colored_text("########################################", "Green")
                )
            else:
                print(tc.colored_text("Error occurred!", "Red"))

    def seconds_to_minute(self, seconds):
        """This function converts seconds to minutes"""
        minute = seconds // 60
        res_seconds = seconds % 60
        minute = "%.0f" % minute
        if res_seconds < 10:
            res_seconds = "0" + "%.0f" % res_seconds
        else:
            res_seconds = "%.0f" % res_seconds

        return f"{minute}:{res_seconds}"
