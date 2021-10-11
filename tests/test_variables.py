import numpy as np
from numpy.testing import assert_array_equal

from ugrid import UGrid


def test_get_topology_attributes_names_and_values():
    r"""Tests `topology_get_attributes_names` and `topology_get_attributes_values` can read attributes names and
    values of a mesh2d topology."""

    with UGrid("./data/OneMesh2D.nc", "r") as ug:
        # Get the first mesh of the file
        ugrid_mesh2d = ug.mesh2d_get(0)
        attribute_names = ug.variable_get_attributes_names(ugrid_mesh2d.name)
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
