"""
This example shows how to convert an IFC file to a COLLADA file.
It is assumed that within the project directory there is a subdirectory called "models" containing the IFC files and 
a subdirectory called "collada" where the COLLADA files will be saved. If the "collada" directory doesn't exist,
it will be created automatically.
"""

import os
import time
from pybimscantools import ifcconvert
from pybimscantools import textcolor

# name of the project directory
project_name = "KSA"

# create relative path to the project
path = os.path.join(os.path.join(os.path.dirname(os.getcwd()), "Data", project_name))

# IFC-to-collada conversion
Start_Time = time.time()
ifc_convert = ifcconvert.IfcConvert()
ifc_convert.convert_to_collada(os.path.join(path, "models\ifc"),  os.path.join(path, "models\collada"))
End_Time = time.time()
print(
    textcolor.colored_text(
        f"Elapsed time was {ifc_convert.seconds_to_minute(End_Time-Start_Time)} minutes",
        "Blue",
    )
)