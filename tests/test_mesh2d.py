import numpy as np
from numpy.testing import assert_array_equal

from ugrid import UGrid, Mesh2D


def create_mesh2d():
    r"""Create a mesh2d"""

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

    mesh2d = Mesh2D(
        name=name,
        node_x=node_x,
        node_y=node_y,
        edge_node=edge_node,
        face_x=face_x,
        face_y=face_y,
        face_node=face_node,
    )
    return mesh2d


def test_mesh2d_get():
    r"""Tests `mesh2d_get_num_topologies` and `network1d_get` to read a network1d from file."""

    with UGrid("./data/OneMesh2D.nc", "r") as ug:
        num_mesh2d_topologies = ug.mesh2d_get_num_topologies()
        mesh2d = ug.mesh2d_get(num_mesh2d_topologies - 1)

        expected_mesh2d = create_mesh2d()

        assert expected_mesh2d.name == mesh2d.name

        assert_array_equal(mesh2d.node_x, expected_mesh2d.node_x)
        assert_array_equal(mesh2d.node_y, expected_mesh2d.node_y)
        assert_array_equal(mesh2d.edge_node, expected_mesh2d.edge_node)

        assert_array_equal(mesh2d.face_x, expected_mesh2d.face_x)
        assert_array_equal(mesh2d.face_y, expected_mesh2d.face_y)
        assert_array_equal(mesh2d.face_node, expected_mesh2d.face_node)


def test_mesh2d_define_and_put():
    r"""Tests `mesh2d_define` and `mesh2d_put` to define and write a mesh2d to file."""

    with UGrid("./data/written_files/Mesh2DWrite.nc", "w+") as ug:
        mesh2d = create_mesh2d()
        topology_id = ug.mesh2d_define(mesh2d)
        assert topology_id == 0
        ug.mesh2d_put(topology_id, mesh2d)
