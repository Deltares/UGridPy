import numpy as np
from numpy.testing import assert_array_equal

from ugrid import UGrid


def test_get_topology_attributes_names_and_values():
    r"""Tests `topology_get_attributes_names` and `topology_get_attributes_values` can read attributes names and
    values of a mesh2d topology."""

    with UGrid("./data/OneMesh2D.nc", "r") as ug:
        # 1. Get the first mesh2D
        ugrid_mesh2d = ug.mesh2d_get(0)
        # 2. Get the mesh2D attribute names
        attribute_names = ug.variable_get_attributes_names(ugrid_mesh2d.name)
        # 3. Get the mesh2D attribute values
        attribute_values = ug.variable_get_attributes_values(ugrid_mesh2d.name)
        assert_array_equal(
            attribute_names,
            [
                "cf_role",
                "edge_coordinates",
                "edge_dimension",
                "edge_node_connectivity",
                "face_coordinates",
                "face_dimension",
                "face_node_connectivity",
                "long_name",
                "max_face_nodes_dimension",
                "node_coordinates",
                "node_dimension",
                "topology_dimension",
            ],
        )
        assert_array_equal(
            attribute_values,
            [
                "mesh_topology",
                "mesh2d_edge_x mesh2d_edge_y",
                "mesh2d_nEdges",
                "mesh2d_edge_nodes",
                "mesh2d_face_x mesh2d_face_y",
                "mesh2d_nFaces",
                "mesh2d_face_nodes",
                "Topology data of 2D mesh",
                "mesh2d_nMax_face_nodes",
                "mesh2d_node_x mesh2d_node_y",
                "mesh2d_nNodes",
                "2",
            ],
        )


def test_get_data_double():
    r"""Tests `variable_get_data_double` gets double data."""

    with UGrid("./data/ResultFile.nc", "r") as ug:
        data_variable = ug.variable_get_data_double("mesh1d_s0")
        assert_array_equal(data_variable[:5], [-5.0, -5.0, -5.0, -5.0, -5.0])


def test_get_data_int():
    r"""Tests `variable_get_data_double` gets int data."""

    with UGrid("./data/ResultFile.nc", "r") as ug:
        data_variable = ug.variable_get_data_int("mesh1d_edge_nodes")
        assert_array_equal(data_variable[:5], [1, 2, 1, 3, 4])


def test_get_data_int():
    r"""Tests `variable_get_data_double` gets int data."""

    with UGrid("./data/ResultFile.nc", "r") as ug:
        data_variable = ug.variable_get_data_int("mesh1d_edge_nodes")
        assert_array_equal(data_variable[:5], [1, 2, 1, 3, 4])


def test_variable_int_with_attributes_define():
    r"""Tests `variable_int_with_attributes_define` for defining a coordinate reference system."""

    with UGrid("./data/written_files/CoordinateReferenceSystem.nc", "w+") as ug:
        attribute_dict = {
            "name": "Unknown projected",
            "epsg": np.array([0], dtype=int),
            "grid_mapping_name": "Unknown projected",
            "longitude_of_prime_meridian": np.array([0.0], dtype=float),
            "semi_major_axis": np.array([6378137.0], dtype=float),
            "semi_minor_axis": np.array([6356752.314245], dtype=float),
            "inverse_flattening": np.array([6356752.314245], dtype=float),
            "EPSG_code": "EPSG:0",
            "value": "value is equal to EPSG code",
        }
        ug.variable_int_with_attributes_define(
            "projected_coordinate_system", attribute_dict
        )


def test_variable_int_with_attributes_define():
    r"""Tests `variable_int_with_attributes_define` for defining a coordinate reference system."""

    with UGrid("./data/written_files/CoordinateReferenceSystem.nc", "w+") as ug:
        attribute_dict = {
            "name": "Unknown projected",
            "epsg": np.array([0], dtype=int),
            "grid_mapping_name": "Unknown projected",
            "longitude_of_prime_meridian": np.array([0.0], dtype=float),
            "semi_major_axis": np.array([6378137.0], dtype=float),
            "semi_minor_axis": np.array([6356752.314245], dtype=float),
            "inverse_flattening": np.array([6356752.314245], dtype=float),
            "EPSG_code": "EPSG:0",
            "value": "value is equal to EPSG code",
        }
        ug.variable_int_with_attributes_define(
            "projected_coordinate_system", attribute_dict
        )


def test_attribute_global_define():
    r"""Tests `attribute_global_define` for defining global attributes, such as the conventions."""

    with UGrid("./data/written_files/Conventions.nc", "w+") as ug:

        conventions = {
            "institution": "Deltares",
            "references": "Unknown",
            "source": "Unknown Unknown. Model: Unknown",
            "history": "Created on 2017-11-27T18:05:09+0100, Unknown",
            "Conventions": "CF-1.6 UGRID-1.0/Deltares-0.8",
        }
        ug.attribute_global_define(conventions)
