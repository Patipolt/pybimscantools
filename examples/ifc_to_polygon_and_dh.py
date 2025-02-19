"""
This example shows how to use the (I)fc (S)lab to (O)uter-most (Co)ordinates (C)onversion algorithm
to extract the union shape of the slabs from an IFC file and upload it to Drone Harmony.
"""

import os

from pybimscantools import droneharmony
from pybimscantools import isococ
from pybimscantools import coordinatelist as cl
from pybimscantools import coordinatemodel as cm
from from pybimscantools import transformations


# name of the project directory
project_name = "KSA"

# create relative path to the project
path = os.path.join(os.path.join(os.path.dirname(os.getcwd()), "Data", project_name))


# Set up the algorithm
alg = isococ.ISOCoC(resolution=0.01,
                    z_span=30,
                    z_resolution=2.5,
                    alpha= 0.0,
                    threshold=0.05)

# Read the IFC file, extract and show the ifc slabs
file_name = "KSA_FAS_51_XX_200_43_240123.ifc"
(all_slab_vertices, slab_plot, all_slab_edges) = alg.read_from_file(
                os.path.join(path, "models\ifc", file_name),
                min_value=6,
                max_value=42,
                plot=True,
                indvi_plot=False,
                verbose=False
            )
slab_plot.show()

# save the returned vertices list and edges list as txt
# alg.save_to_file(os.path.join(path, "models\ifc\slab_vertices.txt"), all_slab_vertices)
# with open(os.path.join(path, "models\ifc\slab_edges.txt"), "w") as f:
#     for item in all_slab_edges:
#         f.write("%s\n" % item)

# Algorithm to scan through the IFC file and extract the union shape
union_shape = alg.scan_through(os.path.join(path, "models\ifc", file_name),
                 min_height=6,
                 max_height=42,
                 plot=True,
                 rearrange_points=False,
                 verbose=False)


# Since the height of the polygon is defined by Z values already, we can set all the heights to 0 for google earth
union_shape_google_earth = union_shape.copy()
if isinstance(union_shape_google_earth, cm.CoordinateModel):
    union_shape_google_earth.set_height_all(0)
else:
    union_shape_google_earth.set_height(0)

# Transformation matrix from IFC to LV95
transformation_file_name = "points_for_transformation_ifc_to_lv95.xlsx"
T = transformations.read_transformation_matrix_from_points_from_xlsx(path, transformation_file_name)
transformations.print_transformation_matrix_for_cloud_compare(T)
union_shape.apply_transformation_matrix(T)
union_shape_google_earth.apply_transformation_matrix(T)
union_shape_google_earth.transform_from_lv95_to_google_earth()
union_shape_google_earth.create_kml_for_google_earth(path, file_name.split(".")[0] + ".kml")


# Set up the Drone Harmony API
API_KEY = "2c3bd2fb273e10b139f214f5a372e12c"  # Obtained from Drone Harmony (Contact them via email)
# Can be anything but if it contains special character, it needs to be encoded according to DH API
CLIENT_USER_ID = "patipol"

dh = droneharmony.DroneHarmony(API_KEY, CLIENT_USER_ID)

# Upload CoordinateModel
ret_data = dh.prepare_geo_json(union_shape, site_name="KSA", color="Gold", scene_name="Hospital")
Response = dh.post_site(ret_data)
dh.read_through()