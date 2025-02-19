""" 
This ISOCoC class contains an algorithm used to convert the IFC file to a list of coordinates
isococ stands for (I)fc (S)lab to (O)uter-most (Co)ordinates (C)onversion
This algorithm is inspired by IfcOpenShell library.
thau (Patipol Thanuphol), ZHAW, NOV 2023 
"""

import time
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpltPath
import alphashape
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from scipy.spatial import ConvexHull
from shapely.geometry import GeometryCollection, Polygon, MultiPolygon, MultiPoint
from shapely.ops import unary_union
from pybimscantools import textcolor
from pybimscantools import coordinatelist as cl
from pybimscantools import coordinatemodel as cm


class ISOCoC:
    """This class manipulates the IFC slab object"""

    def __init__(self, resolution: int = 0.001,
                 z_span: float = 1,
                 z_resolution: float = 1,
                 alpha: float = 0.01625,
                 threshold: float = 0.1) -> None:
        self.ifc_file = None
        self.vertices = None
        self.resolution = resolution   
        self.z_span = z_span
        self.z_resolution = z_resolution
        self.alpha = alpha
        self.threshold = threshold
        self.coordinate_list = None
        self.coordinate_model = None

    def read_from_file(
        self,
        file_name: str,
        min_value: int,
        max_value: int,
        verbose: bool = False,
        plot: bool = True,
        indvi_plot: bool = False) -> (np.array([]), "matplotlib.pyplot", list):
        """
        Read the IFC file and return the vertices of all slabs
        in a sorted manner ()
        """

        if plot:
            # Configure for plotting if individual slabs are needed
            if indvi_plot is False:
                color_count = 0
                fig = plt.figure()
                ax = fig.add_subplot(111, projection="3d")

        # Open the IFC file
        self.ifc_file = ifcopenshell.open(file_name)
        initial = 0
        counting = 0
        all_vertices = np.array([])
        all_edges = []

        # Read all IFCSLAB classes in the file until it can not be read anymore
        while True:
            try:
                element = self.ifc_file.by_type("IFCSLAB")[initial]
            except:
                print(textcolor.colored_text("End of file reached", "Green"))
                break
            print(
                textcolor.colored_text(
                    f"Reading IFCSLAB class at IFCSLAB-{initial}-th element", "Orange"
                )
            )

            # Working with geometry
            settings = ifcopenshell.geom.settings()
            # If shape can not be created, skip the current element
            # by going to the next iteration of the while loop
            shape = None
            try:
                shape = ifcopenshell.geom.create_shape(settings, element)
            except Exception as e:
                if verbose:
                    print(textcolor.colored_text(e, "Red"))
                    print(
                        textcolor.colored_text(
                            f"Error creating shape at element {initial}\n", "Red"
                        ),
                        textcolor.colored_text(f"ID: {shape.id}", "Red"),
                    )
                initial += 1
                continue

            # The GUID of the element we processed
            if verbose:
                print(textcolor.colored_text("Shape GUID:\n", "Orange"), shape.guid)
                print(textcolor.colored_text("Shape ID:\n", "Orange"), shape.id)

            # The transformation matrix of the element we processed
            # matrix = shape.transformation.matrix.data
            matrix = ifcopenshell.util.shape.get_shape_matrix(shape)
            if verbose:
                print(textcolor.colored_text("Shape Matrix:\n", "Orange"), matrix)

            # Getting the vertices out of the shape
            grouped_verts = ifcopenshell.util.shape.get_vertices(shape.geometry)

            # Do the transformation here
            # Add another column of 1s to the grouped_verts matrix
            grouped_verts = np.hstack((grouped_verts, np.ones((len(grouped_verts), 1))))
            for i, element in enumerate(grouped_verts):
                grouped_verts[i] = matrix.dot(element)

            # If the vertices are not above level specified, skip the current element
            # by going to the next iteration of the while loop
            if (
                np.min(grouped_verts[:, 2]) < min_value
                or np.max(grouped_verts[:, 2]) > max_value
            ):
                if verbose:
                    print(
                        textcolor.colored_text(
                            "Vertices are out of specified range!", "Red"
                        )
                    )
                initial += 1
                continue

            # Add counting to the number of elements that are read
            grouped_verts = np.hstack(
                (grouped_verts, np.ones((len(grouped_verts), 1)) * counting)
            )
            counting += 1
            # Add the shape.id number to grouped_verts
            grouped_verts = np.hstack(
                (grouped_verts, np.ones((len(grouped_verts), 1)) * shape.id)
            )
            # Add the vertices to all_vertices array
            if len(all_vertices) == 0:
                all_vertices = grouped_verts
            else:
                all_vertices = np.vstack((all_vertices, grouped_verts))

            initial += 1

            # Getting the edges out of the shape
            grouped_edges = ifcopenshell.util.shape.get_edges(shape.geometry)

            # Add the edges to all_edges array
            all_edges.append(grouped_edges)

            # Now all_vertices is sorted based on the counting column
            # let's sort it again based on the x column by still keeping all corresponding y,z and
            # the counting column sorted
            # indices = np.lexsort((all_vertices[:, 0], all_vertices[:, 4]))
            # all_vertices = all_vertices[indices]

            if plot:

                if indvi_plot is True:
                    color_count = 0
                    fig = plt.figure()
                    ax = fig.add_subplot(111, projection="3d")

                # Edges and faces
                grouped_edges = ifcopenshell.util.shape.get_edges(shape.geometry)
                grouped_faces = ifcopenshell.util.shape.get_faces(shape.geometry)

                # Plotting
                # Plot the vertices and configure the scatter plot points
                ax.scatter3D(
                    grouped_verts[:, 0], grouped_verts[:, 1], grouped_verts[:, 2], s=3
                )
                # Edges and sides
                edges = grouped_verts[grouped_edges]
                sides = grouped_verts[grouped_faces]
                # Get rid of the last column of 1s
                edges = edges[:, :, 0:3]
                sides = sides[:, :, 0:3]

                # Plot the sides
                # ax.add_collection3d(
                #     Poly3DCollection(
                #         sides, facecolors="cyan", linewidths=1, edgecolors="r", alpha=0.25
                #     )
                # )

                if color_count < len(textcolor.HEX_COLOR_LIST) - 1:
                    color_count += 1
                    color = "#" + textcolor.HEX_COLOR_LIST[color_count]
                else:
                    color_count = 0
                    color = "#" + textcolor.HEX_COLOR_LIST[color_count]

                # Plot the edges
                edge_collection = Line3DCollection(
                    edges, colors=color, linewidths=2, linestyles="-", alpha=0.4
                )
                ax.add_collection3d(edge_collection)

        if len(all_vertices) == 0:
            print(textcolor.colored_text("No vertices found in the IFC file!", "Red"))
            return (None, None, None)

        if plot:
            fig2 = plt.figure()
            ax2 = fig2.add_subplot(111, projection="3d")
            points = all_vertices[:, 0:3]

            # Compute the convex hull
            hull = ConvexHull(points)

            # Plot the points
            ax2.scatter(points[:, 0], points[:, 1], points[:, 2])

            # Plot the convex hull
            for simplex in hull.simplices:
                # The hull.simplices are the simplices that form the convex hull
                # We plot a line between each pair of points for each simplex
                simplex = np.append(
                    simplex, simplex[0]
                )  # Make sure the simplex is closed
                ax2.plot(
                    points[simplex, 0], points[simplex, 1], points[simplex, 2], "k-"
                )

            # Set labels for ax
            ax.set_title("IFCSLAB Classes")
            ax.set_xlabel("X Label")
            ax.set_ylabel("Y Label")
            ax.set_zlabel("Z Label")
            ax.set_aspect("equal")
            # limit z axis
            ax.set_zlim(min_value, max_value)
            # Set labels for ax2
            ax2.set_title("IFCSLAB Classes with Convex Hull")
            ax2.set_xlabel("X Label")
            ax2.set_ylabel("Y Label")
            ax2.set_zlabel("Z Label")

            # plt.show()

        return (all_vertices, plt, all_edges)

    def sort_slabs(self, vertices: np.array([]), verbose: bool = False) -> np.array([]):
        """
        vertices: list of vertices of all slabs containing
        x, y, z, 1, slab_index, slab_id
        Sort the vertices of the slabs such that the output array
        contains [slab number, number of points in the slab]
        """
        print(textcolor.colored_text("Sorting the slabs!", "Orange"))
        self.vertices = vertices
        # Find how many points are in each slab by looking at the slab_index columnm
        slab_points = np.array([])
        max_slab_no = int(np.max(self.vertices[:, 4]))
        for i in range(0, max_slab_no + 1):
            count = 0
            for j in range(len(self.vertices)):
                if self.vertices[j, 4] == i:
                    count += 1
            # Add the slab number and the number of points in the slab to the slab_points array
            slab_points = (
                np.vstack((slab_points, np.array([i, count])))
                if len(slab_points) != 0
                else np.array([[i, count]])
            )
        # Get rid of the row that has 0 points in the slab
        slab_points = slab_points[slab_points[:, 1] != 0]
        if verbose:
            print(slab_points)
        # Sort the slab_points array based on the number of points in the slab
        # and then based on the slab number
        sorting_indices = np.lexsort((slab_points[:, 0], slab_points[:, 1]))
        slab_points = slab_points[sorting_indices]
        if verbose:
            print(slab_points)

        print(textcolor.colored_text("End of sorting the slabs!", "Green"))

        # Return the sorted slab_points array
        return slab_points

    def group_slabs(
        self, vertices: np.array([]), slab_points: np.array([]), verbose: bool = False
    ) -> list:
        """
        Sort the vertices of the slabs to find the same slabs
        that are on top of each other based on their x and y values with
        a tolerance of some uncertainty specified and return a list containing the indices of the
        same slabs
        """
        print(textcolor.colored_text("Grouping the slabs!", "Orange"))

        # Take the number of points in the slab from the first row of the slab_points array
        # to use it as a reference to find the slabs that have the same number of points
        # Then pick up the slab number from the first row of the slab_points array
        # and iterate through the vertices array to find the slabs that are on top of each other
        # based on their x and y values with a tolerance of some uncertainty specified
        shape_array = []
        while len(slab_points) != 0:
            # Print checking message
            if verbose:
                print(textcolor.colored_text("Checking for same slabs!", "Orange"))

            slab_num_ref = slab_points[0][0]
            num_point = slab_points[0][1]
            append_list = []

            # Add the index of the slab to the append_list
            append_list.append(slab_points[0, 0])

            for i in range(1, len(slab_points)):
                # If num_point is equal to the number of points in the slab
                # It can be the same slab (stacked on top of each other)
                # or a slab that has the same number of points or shape
                # but completely different slab
                if slab_points[i][1] == num_point:
                    # Create two arrays to store the vertices of the two slabs
                    ref_array = np.array([])
                    test_array = np.array([])
                    for j, each_element in enumerate(vertices):
                        if each_element[4] == slab_num_ref:
                            ref_array = (
                                np.vstack((ref_array, each_element))
                                if len(ref_array) != 0
                                else np.array([each_element])
                            )
                    for j, each_element in enumerate(vertices):
                        if each_element[4] == slab_points[i][0]:
                            test_array = (
                                np.vstack((test_array, each_element))
                                if len(test_array) != 0
                                else np.array([each_element])
                            )
                    # print(textcolor.colored_text("ref_array", "Violet"), ref_array)
                    # print(textcolor.colored_text("test_array", "Violet"), test_array)

                    # Create a variable to check if the two slabs are the same
                    check = 0
                    # Compare all the x and y values of the two slabs
                    # If they are within some uncertainty of each other, they are the same slab
                    for j in range(num_point):
                        if (
                            abs(ref_array[j][0] - test_array[j][0]) < self.resolution
                            and abs(ref_array[j][1] - test_array[j][1])
                            < self.resolution
                        ):
                            check += 1
                    # If all the x and y values of the two slabs are within 0.1 of each other
                    # They are the same slab
                    if check == num_point:
                        # Add the index of the slab to the append_list
                        append_list.append(slab_points[i][0])
                        if verbose:
                            print(textcolor.colored_text("Same slab found!", "Green"))
            # Check if there is any slab in the append_list
            if len(append_list) != 0:
                # Add the index of the slab from the append_list to the shape_array
                shape_array.append(append_list)
                # Remove the slab from the slab_points array where the first column is equal to
                # the slab number in the append_list
                for i in append_list:
                    slab_points = slab_points[slab_points[:, 0] != i]

        print(textcolor.colored_text("Slabs that have been grouped together", "Blue"))
        print(textcolor.colored_text(shape_array, "Blue"))
        print(textcolor.colored_text("End of grouping the slabs!", "Green"))

        return shape_array

    def save_to_file(self, file_name: str, vertices: np.array([])) -> None:
        """This function saves the vertices to a txt file"""
        # Save as txt file with "," as delimiter
        np.savetxt(file_name, vertices, delimiter=",", fmt="%s")

    def get_slab_coordinates(
            self, vertices: np.array([]),
            grouped_slab: list,
            edges: list,
            rearrange_points: bool = False,
            verbose: bool = False) -> (cl.CoordinateList, cm.CoordinateModel):
        """
        This function cuts the points which are lying inside the outer-most shape in case
        there are many shapes in one slab and returns the coordinates of the outer-most shape
        """

        # Check if grouped_slab has length more than 1
        if len(grouped_slab) > 1:
            # Find the outermost and indepedent polygons in the grouped_slab
            outermost_grouped_slab = self.find_outermost_polygons_among_grouped_slabs(
                grouped_slab, vertices, edges, verbose=verbose
            )
            print(textcolor.colored_text("Slabs that are outermost and independent", "Pink"))
            print(textcolor.colored_text(outermost_grouped_slab, "Pink"))

            # If the length of outermost_grouped_slab is more than 1
            #     - create a CoordinateModel object
            #     - iterate through each element in outermost_grouped_slab
            #          - create a CoordinateList object
            #          - find the slab with the highest z and also find max_z
            #          - collect the vertices of the slab with the highest z
            #          - find the outermost polygon in the same slab
            #          - rearrange the vertices_element array to form a good polygon out of it
            #          - append the coordinates to the CoordinateList object
            #          - set the height of the CoordinateList object
            #          - append the CoordinateList object to the CoordinateModel object
            #     - return the CoordinateModel object
            # If the length of outermost_grouped_slab is equal to 1
            #     - create a CoordinateList object
            #     - iterate through each element in outermost_grouped_slab
            #          - find the slab with the highest z and also find max_z
            #          - collect the vertices of the slab with the highest z
            #          - find the outermost polygon in the same slab
            #          - rearrange the vertices_element array to form a good polygon out of it
            #          - append the coordinates to the CoordinateList object
            #          - set the height of the CoordinateList object
            #     - return the CoordinateList object
            if len(outermost_grouped_slab) > 1:
                # Create a CoordinateModel object
                self.coordinate_model = cm.CoordinateModel()

                # Iterate through outermost_grouped_slab
                for i, each_outermost_grouped_slab in enumerate(outermost_grouped_slab):
                    # Reset the CoordinateList object
                    self.coordinate_list = cl.CoordinateList()

                    # Find the slab with the highest z
                    highest_slab = 0
                    max_z = -9999  # Set the max_z to a very small number
                    for j in each_outermost_grouped_slab:
                        for k, each_element in enumerate(vertices):
                            if each_element[4] == j:
                                if each_element[2] > max_z:
                                    max_z = each_element[2]
                                    highest_slab = j

                    """Find the outermost polygon in the same slab"""
                    print(textcolor.colored_text(f"Getting exterior points of slab no. {highest_slab}", "Orange"))
                    # Find the vertices element corresponding to the slab_num
                    vertices_element = vertices[vertices[:, 4] == highest_slab]

                    # find the outermost polygon in the same slab
                    # just take the first element in grouped_slab
                    # because they are the same slab
                    separated_polygons = self.separate_polygons(
                        slab_num=each_outermost_grouped_slab[0], edges_array=edges
                    )
                    outermost_polygon, hull = self.find_outermost_polygon_in_same_slab(
                        separated_polygons, num_slab=each_outermost_grouped_slab[0],
                        vertices=vertices,
                        verbose=False
                    )

                    if hull is False:
                        if rearrange_points is False:
                            # Instead of rearranging the vertices_element array to form a good polygon out of it
                            # just use Concave Hull to find the outermost_polygon
                            # take only the x, y values of the vertices_element indexed by outermost_polygon
                            points = []
                            for i in outermost_polygon[0]:
                                points.append(vertices_element[i][0:2])
                            # Compute the concave hull (alpha shape)
                            alpha_value = self.alpha  # Adjust alpha based on your dataset for best fit
                            concave_hull = alphashape.alphashape(points, alpha_value)
                            if isinstance(concave_hull, MultiPolygon):
                                print(textcolor.colored_text("Concave hull is multipolygon", "Red"))
                                print(textcolor.colored_text("Reducing alpha value is recommended to fit a polygon", "Red"))
                                # Stop the program
                                exit(0)
                            elif isinstance(concave_hull, Polygon):
                                print(textcolor.colored_text("Concave hull is polygon", "Yellow"))
                                # Find the vertices number in the vertices array corresponding to the concave_hull exterior
                                # and append them to the outermost_polygon list
                                extracted_outermost_polygon = []
                                polygon = []
                                for i, each_element in enumerate(concave_hull.exterior.coords):
                                    for j, each_point in enumerate(points):
                                        if each_element[0] == each_point[0] and each_element[1] == each_point[1]:
                                            polygon.append(j)
                                extracted_outermost_polygon.append(polygon)
                            else:
                                print(textcolor.colored_text("Concave hull is not a polygon or multipolygon!", "Red"))
                                # Stop the program
                                exit(0)
                            rearranged_selected_point = extracted_outermost_polygon[0]
                        else:
                            """Rearrange the vertices_element array to form a good polygon out of it"""
                            rearranged_selected_point = self.rearrange_vertices(vertices_element=vertices_element,
                                                                                outermost_polygon=outermost_polygon,
                                                                                each_outermost_grouped_slab=each_outermost_grouped_slab,
                                                                                edges=edges,
                                                                                max_z=max_z,
                                                                                resolution=self.resolution,
                                                                                verbose=False)
                            """End of Rearrange the vertices_element array to form a good polygon out of it"""
                        # and append them to the CoordinateList object in the order of
                        # rearranged_selected_point
                        # This is to make sure that the polygon is not a mess like a line or something
                        if verbose:
                            print(textcolor.colored_text(f"Rearrange is done! for slab no. {highest_slab}", "Green"))
                        if len(rearranged_selected_point) > 2:
                            # for i in rearranged_selected_point:
                            #     if abs(vertices_element[i][2] - max_z) < self.resolution:
                            #         self.coordinate_list.append(
                            #             [vertices_element[i][0], vertices_element[i][1], max_z]
                            #         )
                            for i in rearranged_selected_point:
                                self.coordinate_list.append(
                                    [vertices_element[i][0], vertices_element[i][1], max_z]
                                )
                    else:
                        rearranged_selected_point = outermost_polygon[0]
                        for i in rearranged_selected_point:
                            self.coordinate_list.append(
                                [vertices_element[i][0], vertices_element[i][1], max_z]
                            )
                    if verbose:
                        print(textcolor.colored_text(f"Appending is done for slab no. {highest_slab}", "Green"))
                    print(textcolor.colored_text(f"End of Getting exterior points of slab no. {highest_slab}", "Green"))
                    """End of find the outermost polygon in the same slab"""

                    # Set the height of the CoordinateList object
                    self.coordinate_list.set_height(max_z)

                    # Add the CoordinatesList to the CoordinateModel object
                    self.coordinate_model.append(self.coordinate_list)

                # Return the CoordinateModel object
                return self.coordinate_model

            else:
                # Create a CoordinateList object
                self.coordinate_list = cl.CoordinateList()

                # Find the slab with the highest z
                highest_slab = 0
                max_z = -9999  # Set the max_z to a very small number
                for i in outermost_grouped_slab[0]:
                    for j, each_element in enumerate(vertices):
                        if each_element[4] == i:
                            if each_element[2] > max_z:
                                max_z = each_element[2]
                                highest_slab = i

                """Find the outermost polygon in the same slab"""
                print(textcolor.colored_text(f"Getting exterior points of slab no. {highest_slab}", "Orange"))
                # Find the vertices element corresponding to the slab_num
                vertices_element = vertices[vertices[:, 4] == highest_slab]

                # find the outermost polygon in the same slab
                # just take the first element in grouped_slab
                # because they are the same slab
                separated_polygons = self.separate_polygons(
                    slab_num=outermost_grouped_slab[0][0], edges_array=edges
                )
                outermost_polygon, hull = self.find_outermost_polygon_in_same_slab(
                    separated_polygons, num_slab=outermost_grouped_slab[0][0],
                    vertices=vertices,
                    verbose=False
                )
    
                if hull is False:
                    if rearrange_points is False:
                        # Instead of rearranging the vertices_element array to form a good polygon out of it
                        # just use Concave Hull to find the outermost_polygon
                        # take only the x, y values of the vertices_element indexed by outermost_polygon
                        points = []
                        for i in outermost_polygon[0]:
                            points.append(vertices_element[i][0:2])
                        # Compute the concave hull (alpha shape)
                        alpha_value = self.alpha  # Adjust alpha based on your dataset for best fit
                        concave_hull = alphashape.alphashape(points, alpha_value)
                        if isinstance(concave_hull, MultiPolygon):
                            print(textcolor.colored_text("Concave hull is multipolygon", "Red"))
                            print(textcolor.colored_text("Reducing alpha value is recommended to fit a polygon", "Red"))
                            # Stop the program
                            exit(0)
                        elif isinstance(concave_hull, Polygon):
                            print(textcolor.colored_text("Concave hull is polygon", "Yellow"))
                            # Find the vertices number in the vertices array corresponding to the concave_hull exterior
                            # and append them to the outermost_polygon list
                            extracted_outermost_polygon = []
                            polygon = []
                            for i, each_element in enumerate(concave_hull.exterior.coords):
                                for j, each_point in enumerate(points):
                                    if each_element[0] == each_point[0] and each_element[1] == each_point[1]:
                                        polygon.append(j)
                            extracted_outermost_polygon.append(polygon)
                        else:
                            print(textcolor.colored_text("Concave hull is not a polygon or multipolygon!", "Red"))
                            # Stop the program
                            exit(0)
                        rearranged_selected_point = extracted_outermost_polygon[0]
                    else:
                        """Rearrange the vertices_element array to form a good polygon out of it"""
                        rearranged_selected_point = self.rearrange_vertices(vertices_element=vertices_element,
                                                                            outermost_polygon=outermost_polygon,
                                                                            each_outermost_grouped_slab=outermost_grouped_slab[0],
                                                                            edges=edges,
                                                                            max_z=max_z,
                                                                            resolution=self.resolution,
                                                                            verbose=False)
                        """End of Rearrange the vertices_element array to form a good polygon out of it"""
                    # and append them to the CoordinateList object in the order of
                    # rearranged_selected_point
                    # This is to make sure that the polygon is not a mess like a line or something
                    if verbose:
                        print(textcolor.colored_text(f"Rearrange is done! for slab no. {highest_slab}", "Green"))
                    if len(rearranged_selected_point) > 2:
                        # for i in rearranged_selected_point:
                        #     if abs(vertices_element[i][2] - max_z) < self.resolution:
                        #         self.coordinate_list.append(
                        #             [vertices_element[i][0], vertices_element[i][1], max_z]
                        #         )
                        for i in rearranged_selected_point:
                            self.coordinate_list.append(
                                [vertices_element[i][0], vertices_element[i][1], max_z]
                            )
                else:
                    rearranged_selected_point = outermost_polygon[0]
                    for i in rearranged_selected_point:
                        self.coordinate_list.append(
                            [vertices_element[i][0], vertices_element[i][1], max_z]
                        )
                if verbose:
                    print(textcolor.colored_text(f"Appending is done for slab no. {highest_slab}", "Green"))
                print(textcolor.colored_text(f"End of Getting exterior points of slab no. {highest_slab}", "Green"))
                """End of find the outermost polygon in the same slab"""

                # Set the height of the CoordinateList object
                self.coordinate_list.set_height(max_z)

                # Return the CoordinateList object
                return self.coordinate_list

        # If grouped_slab has length equal to 1
        #     - create a CoordinateList object
        #     - find the slab with the highest z and also find max_z
        #     - collect the vertices of the slab with the highest z
        #     - find the outermost polygon in the same slab
        #     - rearrange the vertices_element array to form a good polygon out of it
        #     - append the coordinates to the CoordinateList object
        #     - set the height of the CoordinateList object
        #     - return the CoordinateList object
        else:
            # Create a CoordinateList object
            self.coordinate_list = cl.CoordinateList()

            # Find the slab with the highest z
            highest_slab = 0
            max_z = -9999  # Set the max_z to a very small number
            for i in grouped_slab[0]:
                for j, each_element in enumerate(vertices):
                    if each_element[4] == i:
                        if each_element[2] > max_z:
                            max_z = each_element[2]
                            highest_slab = i

            """Find the outermost polygon in the same slab"""
            print(textcolor.colored_text(f"Getting exterior points of slab no. {highest_slab}", "Orange"))
            # Find the vertices element corresponding to the slab_num
            vertices_element = vertices[vertices[:, 4] == highest_slab]

            # find the outermost polygon in the same slab
            # just take the first element in grouped_slab
            # because they are the same slab
            separated_polygons = self.separate_polygons(
                slab_num=grouped_slab[0][0], edges_array=edges
            )
            outermost_polygon, hull = self.find_outermost_polygon_in_same_slab(
                separated_polygons, num_slab=grouped_slab[0][0],
                vertices=vertices,
                verbose=False
            )
    
            if hull is False:
                if rearrange_points is False:
                    # Instead of rearranging the vertices_element array to form a good polygon out of it
                    # just use Concave Hull to find the outermost_polygon
                    # take only the x, y values of the vertices_element indexed by outermost_polygon
                    points = []
                    for i in outermost_polygon[0]:
                        points.append(vertices_element[i][0:2])
                    # Compute the concave hull (alpha shape)
                    alpha_value = self.alpha  # Adjust alpha based on your dataset for best fit
                    concave_hull = alphashape.alphashape(points, alpha_value)
                    if isinstance(concave_hull, MultiPolygon):
                        print(textcolor.colored_text("Concave hull is multipolygon", "Red"))
                        print(textcolor.colored_text("Reducing alpha value is recommended to fit a polygon", "Red"))
                        # Stop the program
                        exit(0)
                    elif isinstance(concave_hull, Polygon):
                        print(textcolor.colored_text("Concave hull is polygon", "Yellow"))
                        # Find the vertices number in the vertices array corresponding to the concave_hull exterior
                        # and append them to the outermost_polygon list
                        extracted_outermost_polygon = []
                        polygon = []
                        for i, each_element in enumerate(concave_hull.exterior.coords):
                            for j, each_point in enumerate(points):
                                if each_element[0] == each_point[0] and each_element[1] == each_point[1]:
                                    polygon.append(j)
                        extracted_outermost_polygon.append(polygon)
                    else:
                        print(textcolor.colored_text("Concave hull is not a polygon or multipolygon!", "Red"))
                        # Stop the program
                        exit(0)
                    rearranged_selected_point = extracted_outermost_polygon[0]
                else:
                    """Rearrange the vertices_element array to form a good polygon out of it"""
                    rearranged_selected_point = self.rearrange_vertices(vertices_element=vertices_element,
                                                                        outermost_polygon=outermost_polygon,
                                                                        each_outermost_grouped_slab=grouped_slab[0],
                                                                        edges=edges,
                                                                        max_z=max_z,
                                                                        resolution=self.resolution,
                                                                        verbose=False)
                    """End of Rearrange the vertices_element array to form a good polygon out of it"""
                # and append them to the CoordinateList object in the order of
                # rearranged_selected_point
                # This is to make sure that the polygon is not a mess like a line or something
                if verbose:
                    print(textcolor.colored_text(f"Rearrange is done! for slab no. {highest_slab}", "Green"))
                if len(rearranged_selected_point) > 2:
                    # for i in rearranged_selected_point:
                    #     if abs(vertices_element[i][2] - max_z) < self.resolution:
                    #         self.coordinate_list.append(
                    #             [vertices_element[i][0], vertices_element[i][1], max_z]
                    #         )
                    for i in rearranged_selected_point:
                        self.coordinate_list.append(
                            [vertices_element[i][0], vertices_element[i][1], max_z]
                        )
            else:
                rearranged_selected_point = outermost_polygon[0]
                for i in rearranged_selected_point:
                    self.coordinate_list.append(
                        [vertices_element[i][0], vertices_element[i][1], max_z]
                    )
            if verbose:
                print(textcolor.colored_text(f"Appending is done for slab no. {highest_slab}!", "Green"))
            print(textcolor.colored_text(f"End of Getting exterior points of slab no. {highest_slab}", "Green"))
            """End of find the outermost polygon in the same slab"""

            # Set the height of the CoordinateList object
            self.coordinate_list.set_height(max_z)

            # Return the CoordinateList object
            return self.coordinate_list

    def separate_polygons(self, slab_num: int, edges_array: list) -> list:
        """This function separates the polygons in the same slab"""
        separated_polygons = [[]]
        current = 0
        # Take the edge element corresponding to the slab_num
        edge_element = edges_array[slab_num]
        # Begin different shapes detection
        for i, each_element in enumerate(edge_element):
            check = 0
            for j, each_separated_polygon in enumerate(separated_polygons):
                if each_separated_polygon == []:
                    each_separated_polygon.append(each_element[0])
                    each_separated_polygon.append(each_element[1])
                    check += 1
                    continue
                else:
                    if each_element[0] in each_separated_polygon:
                        # Check if the other point is already in the test_shape
                        if each_element[1] in each_separated_polygon:
                            check += 1
                        else:
                            each_separated_polygon.append(each_element[1])
                            check += 1
                    elif each_element[1] in each_separated_polygon:
                        # Check if the other point is already in the test_shape
                        if each_element[0] in each_separated_polygon:
                            check += 1
                        else:
                            each_separated_polygon.append(each_element[0])
                            check += 1
            if check == 0:
                current += 1
                separated_polygons.append([])
                separated_polygons[current].append(each_element[0])
                separated_polygons[current].append(each_element[1])
        separated_polygons = self.reduce_same_edge(separated_polygons)

        return separated_polygons

    def reduce_same_edge(self, separated_polygon: list) -> list:
        """This function reduces the same points in the separated_polygon"""
        # Sort each sublist to ensure that identical lists with different orders are recognized as duplicates
        sorted_sublists = [sorted(sublist) for sublist in separated_polygon]

        # Convert each sorted sublist to a tuple
        tuple_set = set(tuple(sublist) for sublist in sorted_sublists)

        # Convert the unique tuples back to lists
        unique_lists = [list(t) for t in tuple_set]

        return unique_lists

    def find_outermost_polygon_in_same_slab(
        self,
        separated_polygon: list,
        num_slab: int,
        vertices: list,
        verbose: bool = False,
    ) -> (list, bool):
        """This function removes the inside points of the same slab"""
    
        hull = False

        # Take the vertices element corresponding to the slab_num
        vertices_element = vertices[vertices[:, 4] == num_slab]

        # Create a numpy array containing the result of the ConvexHull
        results = np.zeros([len(separated_polygon), len(separated_polygon)])
        # Testing if all the vertices indexed by each separated_polygon are inside of
        # each other or not by using ConvexHull
        for i, tester_polygon in enumerate(separated_polygon):
            # Create a list of points that are in the tester_polygon
            tester_points = []
            # append only x, y values of the elements indexed by tester_polygon to tester_points
            for j, each_element in enumerate(tester_polygon):
                tester_points.append(vertices_element[each_element][0:2])
            # Create a numpy array of the points
            tester_points = np.array(tester_points)
            # Compute the convex hull
            tester_hull = ConvexHull(tester_points)

            for j, testing_polygon in enumerate(separated_polygon):
                # if i == j then skip the iteration. If not, do the ConvexHull
                if i == j:
                    results[i][j] = 0
                else:
                    # Create a list of points that are in the testing_polygon
                    testing_points = []
                    # append only x, y values of the elements indexed by testing_polygon to testing_points
                    for k, each_element in enumerate(testing_polygon):
                        testing_points.append(vertices_element[each_element][0:2])
                    # Create a numpy array of the points
                    testing_points = np.array(testing_points)
                    # Compute the convex hull
                    testing_hull = ConvexHull(testing_points)

                    # Check if the testing_hull is inside the tester_hull
                    # If yes, add 1 to the results array
                    # If no, add 0 to the results array

                    # Create a path object for the larger hull
                    path_larger_hull = mpltPath.Path(
                        tester_points[tester_hull.vertices]
                    )

                    # Check if all points of the smaller hull are within the larger hull
                    # Use the path object to test if points are inside the convex hull
                    contained = all(
                        path_larger_hull.contains_point(point)
                        for point in testing_points[testing_hull.vertices]
                    )
                    results[i][j] = contained
                    # if verbose:
                    #     print("Smaller hull is inside the larger hull:", contained)
                    #     print(results)

        # Find the outermost polygon
        # Find the sum of each column if the sum is 0 then it is the outermost polygon
        outermost_polygon = []
        for i in range(len(results)):
            if np.sum(results[:, i]) == 0:
                outermost_polygon.append(separated_polygon[i])

        # Check if the outermost_polygon has more than 1 element,
        # meaning that this slab is formed in a special case, which may be a multi-polygon
        if len(outermost_polygon) > 1:
            hull = True
            if verbose:
                print(textcolor.colored_text(f"Special case detected for slab no. {num_slab}", "Orange"))
                # print(outermost_polygon)
                print(textcolor.colored_text(f"Slab no. {num_slab} has outermost polygon length of: {len(outermost_polygon)}", "Pale"))
            # Use Concave Hull to find the outermost_polygon
            points = vertices_element[:, 0:2]
            # Compute the concave hull (alpha shape)
            alpha_value = self.alpha  # Adjust alpha based on your dataset for best fit
            concave_hull = alphashape.alphashape(points, alpha_value)

            if isinstance(concave_hull, MultiPolygon):
                
                print(textcolor.colored_text("Concave hull for slab no. {num_slab} is multipolygon", "Red"))
                print(textcolor.colored_text("Reducing alpha value is recommended to fit a polygon", "Red"))
                # Stop the program
                exit(0)
            elif isinstance(concave_hull, Polygon):
                if verbose:
                    print(textcolor.colored_text(f"Concave hull for slab no. {num_slab} is a polygon", "Yellow"))
                # Find the vertices number in the vertices array corresponding to the concave_hull exterior
                # and append them to the outermost_polygon list
                outermost_polygon = []
                polygon = []
                for i, each_element in enumerate(concave_hull.exterior.coords):
                    for j, each_point in enumerate(points):
                        if each_element[0] == each_point[0] and each_element[1] == each_point[1]:
                            polygon.append(j)
                outermost_polygon.append(polygon)
            else:
                print(textcolor.colored_text("Concave hull is not a polygon or multipolygon!", "Red"))
                # Stop the program
                exit(0)
        else:
            if verbose:
                print(textcolor.colored_text(f"Slab no. {num_slab} has outermost polygon length of: {len(outermost_polygon)}", "Pale"))

        # OLD CODE
        # # Check it the outermost_polygon has more than 1 element,
        # # meaning that this slab is formed in a special case, which is not a polygon
        # # If yes, just take the outermost points by using ConvexHull of vertices_element
        # if len(outermost_polygon) > 1:
        #     """Actually, this is not well implemented yet. Because of the convex hull.
        #     If the slabs are very non-convex like VIAS building in Spain, it will not work.
        #     Because it can not find the outermost points of the slab. It will just find the
        #     outermost points of the convex hull. So, it is better to find the outermost points
        #     by using the concave hull of the vertices_element. However, concave hull is rather
        #     complex and it requires some random algorithms to find the concave hull."""
        #     # Create a list of points containing only x, y values of the vertices_element
        #     # and compute the convex hull of all points to find the outermost_polygon
        #     # then, return the outermost points in term of indices of points in vertices_element

        #     # all_points = []
        #     # for i, each_element in enumerate(vertices_element):
        #     #     all_points.append(each_element[0:2])
        #     # all_points = np.array(all_points)
        #     # # Compute the convex hull
        #     # hull = ConvexHull(all_points)
        #     # outermost_polygon = []
        #     # # Get the exterior points of the hull
        #     # for i in hull.vertices:
        #     #     outermost_polygon.append(i)
        #     # outermost_polygon = [outermost_polygon]

        #     if False:
        #         plt.figure()
        #         # To complete the polygon, add the first point at the end
        #         hull_polygon = np.append(outermost_polygon[0], [outermost_polygon[0][0]], axis=0)
        #         # Plot the original points
        #         plt.scatter(all_points[:, 0], all_points[:, 1], color='blue', label='Original Points')
        #         # Plot the convex hull as a polygon
        #         plt.plot(all_points[hull_polygon, 0], all_points[hull_polygon, 1], 'r--', lw=2, label='Convex Hull Polygon')
        #         # Adding labels and legend
        #         plt.xlabel('X')
        #         plt.ylabel('Y')
        #         plt.title('Convex Hull Polygon')
        #         plt.legend()
        #         # Show plot
        #         plt.show()

        return outermost_polygon, hull

    def find_outermost_polygons_among_grouped_slabs(
        self, grouped_slab: list, vertices: np.array([]), edges: list, verbose: bool = False) -> list:
        """This function outputs the grouped_slab that are independent from each other
        and the outermost polygons in each grouped_slab"""

        print(textcolor.colored_text("Finding independent outermost slabs among groupped slabs!", "Orange"))
        # First, find the outermost polygons in each grouped_slab
        outermost_polygons = []
        for i, each_grouped_slab in enumerate(grouped_slab):
            # find the outermost polygon in the same slab
            separated_polygons = self.separate_polygons(
                slab_num=each_grouped_slab[0], edges_array=edges
            )
            outermost_polygon, hull = self.find_outermost_polygon_in_same_slab(
                separated_polygons,
                num_slab=each_grouped_slab[0],
                vertices=vertices,
                verbose=verbose,
            )
            # Add the outermost_polygon to the outermost_polygons list
            outermost_polygons.append(outermost_polygon[0])

            # # Redundant code in find_outermost_polygon_in_same_slab
            # # Check if the outermost_polygon has more than 1 element,
            # # meaning that this slab is formed in a special case, which may be a multi-polygon
            # if len(outermost_polygon) > 1:
            #     # Use Concave Hull to find the outermost_polygon
            #     points = vertices[vertices[:, 4] == each_grouped_slab[0]]
            #     points = points[:, 0:2]
            #     # Compute the concave hull (alpha shape)
            #     alpha_value = 0.01625  # Adjust alpha based on your dataset for best fit
            #     concave_hull = alphashape.alphashape(points, alpha_value)

            #     if isinstance(concave_hull, MultiPolygon):
            #         print(textcolor.colored_text("Concave hull is multipolygon", "Red"))
            #         print(textcolor.colored_text("Reducing alpha value is recommended to fit a polygon", "Red"))
            #         # Stop the program
            #         exit(0)
            #     elif isinstance(concave_hull, Polygon):
            #         print(textcolor.colored_text("Concave hull is polygon", "Yellow"))
            #         # Find the vertices number in the vertices array corresponding to the concave_hull exterior
            #         # and append them to the outermost_polygon list
            #         outermost_polygon = []
            #         for i, each_element in enumerate(concave_hull.exterior.coords):
            #             for j, each_point in enumerate(points):
            #                 if each_element[0] == each_point[0] and each_element[1] == each_point[1]:
            #                     outermost_polygon.append(j)
            #         outermost_polygons.append(outermost_polygon)
            #     else:
            #         print(textcolor.colored_text("Concave hull is not a polygon or multipolygon!", "Red"))
            #         # Stop the program
            #         exit(0)
            # else:
            #     # Add the outermost_polygon to the outermost_polygons list
            #     outermost_polygons.append(outermost_polygon[0])

        # Second, find the outermost polygons among the outermost_polygons
        # Create a numpy array containing the result of the ConvexHull
        results = np.zeros([len(outermost_polygons), len(outermost_polygons)])
        # Testing if all the vertices indexed by each grouped_slab are inside of
        # each other or not based on their outer-most calculated points in
        # outerrmost_polygon by using ConvexHull
        for i, tester_polygon in enumerate(outermost_polygons):
            # Create a list of points that are in the tester_polygon
            tester_points = []
            # Get the vertices element corresponding to the slab_num
            vertices_element = vertices[vertices[:, 4] == grouped_slab[i][0]]
            # append only x, y values of the elements indexed by tester_polygon to tester_points
            for j, each_element in enumerate(tester_polygon):
                tester_points.append(vertices_element[each_element][0:2])

            # Create a numpy array of the points
            tester_points = np.array(tester_points)
            # Compute the convex hull
            tester_hull = ConvexHull(tester_points)

            for j, testing_polygon in enumerate(outermost_polygons):
                # Get the vertices element corresponding to the slab_num
                vertices_element_testing = vertices[vertices[:, 4] == grouped_slab[j][0]]
                # if i == j then skip the iteration. If not, do the ConvexHull
                if i == j:
                    results[i][j] = 0
                else:
                    # Create a list of points that are in the testing_polygon
                    testing_points = []
                    # append only x, y values of the elements indexed by testing_polygon to testing_points
                    for k, each_element in enumerate(testing_polygon):
                        testing_points.append(vertices_element_testing[each_element][0:2])
                    # Create a numpy array of the points
                    testing_points = np.array(testing_points)
                    # Compute the convex hull
                    testing_hull = ConvexHull(testing_points)

                    # Check if the testing_hull is inside the tester_hull
                    # If yes, add 1 to the results array
                    # If no, add 0 to the results array

                    # Create a path object for the larger hull
                    path_larger_hull = mpltPath.Path(
                        tester_points[tester_hull.vertices]
                    )

                    # Check if all points of the smaller hull are within the larger hull
                    # Use the path object to test if points are inside the convex hull
                    contained = all(
                        path_larger_hull.contains_point(point)
                        for point in testing_points[testing_hull.vertices]
                    )
                    results[i][j] = contained
                    # if verbose:
                    #     print("Smaller hull is inside the larger hull:", contained)
                    #     print(results)

        # print(results)
        # Find the outermost polygon
        # Find the sum of each column if the sum is 0 then it is the outermost polygon
        outermost_independent_slab = []
        for i in range(len(results)):
            if np.sum(results[:, i]) == 0:
                outermost_independent_slab.append(grouped_slab[i])
        
        print(textcolor.colored_text("End of finding independent outermost slabs among groupped slabs!", "Green"))

        return outermost_independent_slab

    def rearrange_vertices(self,
            vertices_element: np.array([]),
            outermost_polygon: list,
            each_outermost_grouped_slab: list,
            edges: list,
            max_z: float,
            resolution: float,
            verbose: bool) -> list:
        """This function rearranges the vertices to form a good polygon out of it"""

        # Take only the index i in vertices_element indexed by
        # outermost_polygon, which has the same height as max_z
        # and append to the selected-point list such that we can rearrange
        # the vertices_element array later according to the edges array
        # to form a good polygon out of it, otherwise the polygon will be
        # a mess (there will be some intersections in the polygon)
        selected_points = []
        for i, each_element in enumerate(vertices_element):
            if (
                i in outermost_polygon[0]
                and abs(each_element[2] - max_z) < resolution
            ):
                selected_points.append(i)

        # Rearrange the vertices_element array according to the edges array
        # to form a good polygon out of it
        if verbose:
            print(textcolor.colored_text("Selected Points:", "Orange"), selected_points)
            print(textcolor.colored_text("Outermost Polygon:", "Orange"), outermost_polygon[0])
            print(edges[each_outermost_grouped_slab[0]])

        # Iterate through the edges array at the index of the slab number
        # defined by each_outermost_grouped_slab[0] to find the edges that
        # are connected to the selected_point
        selected_edges = []
        for i, each_element in enumerate(edges[each_outermost_grouped_slab[0]]):
            # find the edges that both points are in the selected_point
            if each_element[0] in selected_points and each_element[1] in selected_points:
                selected_edges.append(each_element)

        # Rearrange the selected_point array according to the selected_edges array
        # to form a good polygon out of it
        rearranged_selected_points = []
        # Add the first two points of the selected_edges array to the rearranged_selected_point
        rearranged_selected_points.append(selected_edges[0][0])
        rearranged_selected_points.append(selected_edges[0][1])
        # Remove the first element of the selected_edges array
        selected_edges.pop(0)
        # Now iterate through the selected_edges array to find the next point
        ctrl = 0
        while len(selected_edges) != 0:
            # Find the next point
            for i, each_element in enumerate(selected_edges):
                if each_element[0] == rearranged_selected_points[-1]:
                    rearranged_selected_points.append(each_element[1])
                    selected_edges.pop(i)
                    ctrl = 0
                    continue
            for i, each_element in enumerate(selected_edges):
                if each_element[1] == rearranged_selected_points[-1]:
                    rearranged_selected_points.append(each_element[0])
                    selected_edges.pop(i)
                    ctrl = 0
                    continue

            ctrl += 1
            
            if ctrl > 2:
                print(textcolor.colored_text("Error: The polygon is not closed!", "Red"))
                break

        # This is to protect the case where the polygon is not closed
        if len(rearranged_selected_points) > 2 and ctrl < 2:
            rearranged_selected_points.pop(-1)
        if verbose:
            print(textcolor.colored_text("Rearranged Selected Points:", "Green"), rearranged_selected_points)

        return rearranged_selected_points

    def return_unioned_shape(self, coordinate: (cl.CoordinateList, cm.CoordinateModel)) -> Polygon:
        """This function returns the unioned shape of the coordinate"""
        # If the coordinate is a CoordinateList
        if isinstance(coordinate, cl.CoordinateList):
            if coordinate.len() != 0:
                # This is already the biggest polygon. So, just return it
                read_out_coor = []
                for i in range(0, coordinate.len()):
                    read_out_coor.append(coordinate.get_coordinate(i))
                read_out_polygon = Polygon([(x, y) for x, y, _ in read_out_coor])
                return read_out_polygon
            else:
                print(textcolor.colored_text("CoordinateList is empty", "Red"))
                return None
        # If the coordinate is a CoordinateModel
        elif isinstance(coordinate, cm.CoordinateModel):
            if coordinate.len() != 0:
                # Loop through all the coordinate lists in the coordinate model
                # and make polygons out of them and union them together
                unioned_polygon = None
                for i in range(0, coordinate.len()):
                    read_out_coor = []
                    for j in range(0, coordinate.get_coordinate_list(i).len()):
                        read_out_coor.append(coordinate.get_coordinate_list(i).get_coordinate(j))
                    read_out_polygon = Polygon([(x, y) for x, y, _ in read_out_coor])
                    if i == 0:
                        unioned_polygon = read_out_polygon
                    else:
                        try:
                            unioned_polygon = unioned_polygon.union(read_out_polygon)
                        except Exception as e:
                            print(textcolor.colored_text(f"Error: {e}", "Red"))
                            # rearrange the self-intersected polygon by using the convex hull
                            # and union them again
                            hull = MultiPoint([(x, y) for x, y in read_out_polygon.exterior.coords]).convex_hull
                            unioned_polygon = unioned_polygon.union(hull)

                # Check if the unioned polygon is a GeometryCollection
                if isinstance(unioned_polygon, GeometryCollection):
                    # Extract the polygons from the unioned polygon when the type is GeometryCollection
                    combined_polygon = None
                    polygons = []
                    for geom in unioned_polygon.geoms:
                        if isinstance(geom, (Polygon, MultiPolygon)):
                            polygons.append(geom)
                    combined_polygon = unary_union(polygons)
                    return combined_polygon
                else:
                    return unioned_polygon
            else:
                print(textcolor.colored_text("CoordinateModel is empty", "Red"))
                return None
        else:
            print(textcolor.colored_text("Coordinate is not a CoordinateList nor CoordinateModel", "Red"))
            return None

    def plot_unioned_shape(self, unioned_shape: Polygon) -> None:
        """This function plots the unioned shape"""
        fig = plt.figure()
        ax =  fig.add_subplot(111)
        if unioned_shape.geom_type == 'Polygon':
            x, y = unioned_shape.exterior.xy
            ax.fill(x, y, alpha=0.5, linewidth=2, color='#02a60d')
        elif unioned_shape.geom_type == 'MultiPolygon':
            for polygon in unioned_shape.geoms:
                x, y = polygon.exterior.xy
                ax.fill(x, y, alpha=0.5, linewidth=2, color='#02a60d')

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title('Union of Projected 2D Shapes')
        ax.grid(True)
        ax.axis('equal')
        plt.show()

    def polygons_to_coordinates(self, polygons: Polygon) -> (cl.CoordinateList, cm.CoordinateModel):
        """This function converts the unioned polygons to either coordinatelist or coordinatemodel"""
        # If the unioned polygons is a Polygon
        if polygons.geom_type == 'Polygon':
            # Create a CoordinateList object
            coordinate_list = cl.CoordinateList()
            # Add the coordinates of the polygon to the CoordinateList object
            for x, y in polygons.exterior.coords:
                coordinate_list.append([x, y, 0.0])
            return coordinate_list
        # If the unioned polygons is a MultiPolygon
        elif polygons.geom_type == 'MultiPolygon':
            # Create a CoordinateModel object
            coordinate_model = cm.CoordinateModel()
            # Loop through all the polygons in the MultiPolygon
            for polygon in polygons.geoms:
                # Create a CoordinateList object
                coordinate_list = cl.CoordinateList()
                # Add the coordinates of the polygon to the CoordinateList object
                for x, y in polygon.exterior.coords:
                    coordinate_list.append([x, y, 0.0])
                # Add the CoordinateList object to the CoordinateModel object
                coordinate_model.append(coordinate_list)
            return coordinate_model
        else:
            print(textcolor.colored_text("The unioned polygons is neither a Polygon nor a MultiPolygon", "Red"))
            return None

    def scan_through(self, ifc_file: str, min_height: float, max_height: int, plot: bool, rearrange_points: bool = False, verbose: bool = False) -> list:
        """This function scans through the ifc_file in the range of min_height to the max_value.
        This will find different unioned shapes within z_span specified in the class and
        adding up with the z_resolution until the max_value reached.
        If there are different stories, which have different shapes in terms of area for 
        more than a threshold specified, then it will return the different unioned shapes 
        in the form of either CoordinateList or CoordinateModel."""

        if min_height >= max_height:
            print(textcolor.colored_text("min_height is greater than or equal to max_value", "Red"))
            return None
        
        min_scan = float(min_height)
        max_scan = float(min_height) + self.z_span
        comparing_area = 0.0
        unioned_shape_list = []
        min_max_list = []

        # Read all the slab vertices and edges in the range of min_height to max_height
        (all_slab_vertices, slab_plot, all_slab_edges) = self.read_from_file(
                ifc_file,
                min_value=min_height,
                max_value=max_height,
                plot=False,
                indvi_plot=False,
                verbose=False
            )

        while min_scan <= max_height - self.z_resolution:
            print(textcolor.colored_text("\n#######################################", "Orange"))
            print(textcolor.colored_text(f"Scanning through the range of {min_scan} to {max_scan}", "Orange"))
            print(textcolor.colored_text("#######################################\n", "Orange"))
            # Extract the slab number in the all_slab_vertices
            slab_num = []
            if all_slab_vertices is not None:
                for i, each_element in enumerate(all_slab_vertices):
                    if each_element[4] not in slab_num:
                        slab_num.append(each_element[4])
            else:
                print(textcolor.colored_text("No slab is detected", "Red"))
                # stop the program
                break
            # For each slab number, find the corresponding vertices in the all_slab_vertices
            # and if ALL the vertices with the same slab number are in the scanning window,
            # then add them to the scanning_window_slab_vertices
            scanning_window_slab_vertices = np.array([])
            for i, each_slab_num in enumerate(slab_num):
                slab_vertices = all_slab_vertices[all_slab_vertices[:, 4] == each_slab_num]
                if len(slab_vertices) != 0:
                    # Check if all the vertices are in the scanning window
                    if all(slab_vertices[:, 2] >= min_scan) and all(slab_vertices[:, 2] <= max_scan):
                        if len(scanning_window_slab_vertices) == 0:
                            scanning_window_slab_vertices = slab_vertices
                        else:
                            scanning_window_slab_vertices = np.vstack((scanning_window_slab_vertices, slab_vertices))

            if scanning_window_slab_vertices.shape[0] > 0:
                # Sort the vertices and group the same slabs
                sorted_slabs = self.sort_slabs(scanning_window_slab_vertices)
                grouped_slab = self.group_slabs(scanning_window_slab_vertices, sorted_slabs, verbose=False)     
                
                # Get the coordinates of the slabs
                coordinates = self.get_slab_coordinates(
                    scanning_window_slab_vertices, grouped_slab, all_slab_edges, rearrange_points=rearrange_points, verbose=verbose)

                # plot each coordinates for testing
                # if isinstance(coordinates, cl.CoordinateList):
                #     coordinates.plot_coordinates()
                # elif isinstance(coordinates, cm.CoordinateModel):
                #     for i in range(0, coordinates.len()):
                #         coordinates.get_coordinate_list(i).plot_coordinates()

                # Continue with the coordinatelist or coordinatemodel obtained from the algorithm
                unioned_shape = self.return_unioned_shape(coordinates)
                # self.plot_unioned_shape(unioned_shape)

                # if the unioned_shape area is different from the comparing_area for more than a threshold
                # in percentage, then add the unioned_shape to the unioned_shape_list
                if comparing_area == 0.0:
                    comparing_area = unioned_shape.area
                    unioned_shape_list.append(unioned_shape)
                    min_max_list.append([min_scan, max_scan])
                else:
                    if abs(unioned_shape.area - comparing_area) > self.threshold * comparing_area:
                        unioned_shape_list.append(unioned_shape)
                        comparing_area = unioned_shape.area
                        min_max_list.append([min_scan, max_scan])

                print(textcolor.colored_text(f"Unioned Polygon has a length of {len(unioned_shape_list)}", "Pink"))
                # update the min and max
                min_scan += self.z_resolution
                max_scan = min_scan + self.z_span
            else:
                print(textcolor.colored_text("No slab is detected", "Red"))
                break
        min_max_list.append([min_scan, max_scan])   # append the last min and max
        print(unioned_shape_list)
        # If the unioned_shape_list has more than 1 element, then return the unioned_shape_list
        if len(unioned_shape_list) > 1:
            coormodel = cm.CoordinateModel()
            print(textcolor.colored_text("Different unioned shapes are detected", "Green"))
            for i, each_unioned_shape in enumerate(unioned_shape_list):
                print(textcolor.colored_text(f"Unioned Shape no. {i+1}", "Green"))
                points = []
                coorlist = cl.CoordinateList()
                if isinstance(each_unioned_shape, Polygon):
                    polygon = Polygon(each_unioned_shape)
                elif isinstance(each_unioned_shape, MultiPolygon):
                    for j, each_polygon in enumerate(each_unioned_shape.geoms):
                        polygon = Polygon(each_polygon)
                        for k, each_point in enumerate(polygon.exterior.coords):
                            points.append(each_point)
                for j, each_point in enumerate(polygon.exterior.coords):
                    points.append(each_point)
                multi_point = MultiPoint(points)
                hull = multi_point.convex_hull
                outermost_points = list(hull.exterior.coords)
                # append the points to the coordinate list
                for each_point in outermost_points:
                    coorlist.append([each_point[0], each_point[1], min_max_list[i+1][0]]) # i+1 because the next is where the shape is different
                coorlist.set_height(min_max_list[i+1][0])
                coorlist.print()
                coormodel.append(coorlist)
                print(textcolor.colored_text(f"MIN is {min_max_list[i][0]} and MAX is {min_max_list[i][1]}", "Pink"))
                self.plot_unioned_shape(each_unioned_shape)

            return coormodel
        
        if len(unioned_shape_list) == 1:
            print(textcolor.colored_text("No different unioned shapes are detected", "Red"))
            points = []
            coorlist = cl.CoordinateList()
            polygon = Polygon(unioned_shape_list[0])
            for j, each_point in enumerate(polygon.exterior.coords):
                points.append(each_point[j])
            multi_point = MultiPoint(points)
            hull = multi_point.convex_hull
            outermost_points = list(hull.exterior.coords)
            # append the points to the coordinate list
            for each_point in outermost_points:
                coorlist.append([each_point[0], each_point[1], min_max_list[i+1][0]])  # i+1 because the next is where the shape is different
            coorlist.set_height(min_max_list[i+1][0])
            coorlist.print()    
            print(textcolor.colored_text(f"MIN is {min_max_list[0][0]} and MAX is {min_max_list[0][1]}", "Pink"))
            self.plot_unioned_shape(unioned_shape_list[0])

            return coorlist
        
        else:
            print(textcolor.colored_text("No unioned shape is detected", "Red"))

            return None

###################################################
###################################################
""" From IfcOpenShell Documentation """

# import ifcopenshell
# import ifcopenshell.geom
# import ifcopenshell.util.shape

# ifc_file = ifcopenshell.open('model.ifc')
# element = ifc_file.by_type('IfcWall')[0]

# settings = ifcopenshell.geom.settings()
# shape = ifcopenshell.geom.create_shape(settings, element)

# # The GUID of the element we processed
# print(shape.guid)

# # The ID of the element we processed
# print(shape.id)

# # The element we are processing
# print(ifc_file.by_guid(shape.guid))

# # A unique geometry ID, useful to check whether or not two geometries are
# # identical for caching and reuse. The naming scheme is:
# # IfcShapeRepresentation.id{-layerset-LayerSet.id}{-material-Material.id}{-openings-[Opening n.id ...]}{-world-coords}
# print(shape.geometry.id)

# # A 4x4 matrix representing the location and rotation of the element, in the form:
# # [ [ x_x, y_x, z_x, x   ]
# #   [ x_y, y_y, z_y, y   ]
# #   [ x_z, y_z, z_z, z   ]
# #   [ 0.0, 0.0, 0.0, 1.0 ] ]
# # The position is given by the last column: (x, y, z)
# # The rotation is described by the first three columns, by explicitly specifying the local X, Y, Z axes.
# # The first column is a normalised vector of the local X axis: (x_x, x_y, x_z)
# # The second column is a normalised vector of the local Y axis: (y_x, y_y, y_z)
# # The third column is a normalised vector of the local Z axis: (z_x, z_y, z_z)
# # The axes follow a right-handed coordinate system.
# # Objects are never scaled, so the scale factor of the matrix is always 1.
# matrix = shape.transformation.matrix.data

# # For convenience, you might want the matrix as a nested numpy array, so you can do matrix math.
# matrix = ifcopenshell.util.shape.get_shape_matrix(shape)

# # You can also extract the XYZ location of the matrix.
# location = matrix[:,3][0:3]

# # X Y Z of vertices in flattened list e.g. [v1x, v1y, v1z, v2x, v2y, v2z, ...]
# verts = shape.geometry.verts

# # Indices of vertices per edge e.g. [e1v1, e1v2, e2v1, e2v2, ...]
# # If the geometry is mesh-like, edges contain the original edges.
# # These may be quads or ngons and not necessarily triangles.
# edges = shape.geometry.edges

# # Indices of vertices per triangle face e.g. [f1v1, f1v2, f1v3, f2v1, f2v2, f2v3, ...]
# # Note that faces are always triangles.
# faces = shape.geometry.faces

# # Since the lists are flattened, you may prefer to group them like so depending on your geometry kernel
# # A nested numpy array e.g. [[v1x, v1y, v1z], [v2x, v2y, v2z], ...]
# grouped_verts = ifcopenshell.util.shape.get_vertices(shape.geometry)
# # A nested numpy array e.g. [[e1v1, e1v2], [e2v1, e2v2], ...]
# grouped_edges = ifcopenshell.util.shape.get_edges(shape.geometry)
# # A nested numpy array e.g. [[f1v1, f1v2, f1v3], [f2v1, f2v2, f2v3], ...]
# grouped_faces = ifcopenshell.util.shape.get_faces(shape.geometry)

# # A list of styles that are relevant to this shape
# styles = shape.geometry.materials

# for style in styles:
#     # Each style is named after the entity class if a default
#     # material is applied. Otherwise, it is named "surface-style-{SurfaceStyle.name}"
#     # All non-alphanumeric characters are replaced with a "-".
#     print(style.original_name())

#     # A more human readable name
#     print(style.name)

#     # Each style may have diffuse colour RGB codes
#     if style.has_diffuse:
#         print(style.diffuse)

#     # Each style may have transparency data
#     if style.has_transparency:
#         print(style.transparency)

# # Indices of material applied per triangle

###################################################
###################################################
