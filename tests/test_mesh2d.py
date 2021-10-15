import numpy as np
from numpy.testing import assert_array_equal

from ugrid import UGrid, UGridMesh2D


def create_ugrid_mesh2d():
    r"""Creates an instance of UGridMesh2D to be used for testing"""

    name = "mesh2d"
    node_x = np.array([0, 1, 0, 1, 0, 1, 0, 1, 2, 2, 2, 2, 3, 3, 3, 3], dtype=np.double)
    node_y = np.array([0, 0, 1, 1, 2, 2, 3, 3, 0, 1, 2, 3, 0, 1, 2, 3], dtype=np.double)
    edge_node = np.array(
        [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            2,
            9,
            4,
            10,
            6,
            11,
            8,
            12,
            9,
            13,
            10,
            14,
            11,
            15,
            12,
            16,
            1,
            3,
            3,
            5,
            5,
            7,
            2,
            4,
            4,
            6,
            6,
            8,
            9,
            10,
            10,
            11,
            11,
            12,
            13,
            14,
            14,
            15,
            15,
            16,
        ],
        dtype=np.int,
    )

    face_x = np.array([0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 2.5, 2.5, 2.5], dtype=np.double)
    face_y = np.array([0.5, 1.5, 2.5, 0.5, 1.5, 2.5, 0.5, 1.5, 2.5], dtype=np.double)
    face_node = np.array(
        [
            1,
            2,
            4,
            3,
            3,
            4,
            6,
            5,
            5,
            6,
            8,
            7,
            2,
            9,
            10,
            4,
            4,
            10,
            11,
            6,
            6,
            11,
            12,
            8,
            9,
            13,
            14,
            10,
            10,
            14,
            15,
            11,
            11,
            15,
            16,
            12,
        ],
        dtype=np.int,
    )

    ugrid_mesh2d = UGridMesh2D(
        name=name,
        node_x=node_x,
        node_y=node_y,
        edge_node=edge_node,
        face_x=face_x,
        face_y=face_y,
        face_node=face_node,
    )
    return ugrid_mesh2d


def test_ugrid_mesh2d_get():
    r"""Tests `mesh2d_get_num_topologies` and `mesh2d_get` to read a mesh2d from file."""

    with UGrid("./data/OneMesh2D.nc", "r") as ug:
        num_mesh2d_topologies = ug.mesh2d_get_num_topologies()
        ugrid_mesh2d = ug.mesh2d_get(num_mesh2d_topologies - 1)

        expected_ugrid_mesh2d = create_ugrid_mesh2d()

        assert expected_ugrid_mesh2d.name == ugrid_mesh2d.name

        assert_array_equal(ugrid_mesh2d.node_x, expected_ugrid_mesh2d.node_x)
        assert_array_equal(ugrid_mesh2d.node_y, expected_ugrid_mesh2d.node_y)
        assert_array_equal(ugrid_mesh2d.edge_node, expected_ugrid_mesh2d.edge_node)

        assert_array_equal(ugrid_mesh2d.face_x, expected_ugrid_mesh2d.face_x)
        assert_array_equal(ugrid_mesh2d.face_y, expected_ugrid_mesh2d.face_y)
        assert_array_equal(ugrid_mesh2d.face_node, expected_ugrid_mesh2d.face_node)
