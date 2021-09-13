import numpy as np
from numpy.testing import assert_array_equal

from ugrid import UGrid, Mesh1D


def create_mesh1d():
    r"""Create a mesh1d"""

    name = "1dmesh"
    network_name = "network"
    edge_node = np.array(
        [
            0,
            1,
            1,
            2,
            2,
            3,
            3,
            4,
            4,
            5,
            5,
            6,
            6,
            7,
            7,
            8,
            8,
            9,
            9,
            10,
            10,
            11,
            11,
            12,
            12,
            13,
            13,
            14,
            14,
            15,
            15,
            16,
            16,
            17,
            17,
            18,
            18,
            19,
            19,
            20,
            20,
            21,
            21,
            22,
            22,
            23,
            23,
            24,
        ],
        dtype=np.int,
    )
    branch_id = np.array(
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        dtype=np.int,
    )
    branch_offset = np.array(
        [
            0,
            49.65,
            99.29,
            148.92,
            198.54,
            248.09,
            297.62,
            347.15,
            396.66,
            446.19,
            495.8,
            545.44,
            595.08,
            644.63,
            694.04,
            743.52,
            793.07,
            842.65,
            892.26,
            941.89,
            991.53,
            1041.17,
            1090.82,
            1140.46,
            1165.29,
        ],
        dtype=np.double,
    )
    node_x = np.empty(branch_id.size, dtype=np.double)
    node_y = np.empty(branch_id.size, dtype=np.double)
    edge_edge_id = np.empty(edge_node.size // 2, dtype=np.int)
    edge_edge_offset = np.empty(edge_node.size // 2, dtype=np.double)
    edge_x = np.empty(edge_node.size // 2, dtype=np.double)
    edge_y = np.empty(edge_node.size // 2, dtype=np.double)

    node_name_id = []
    node_name_long = []
    for n in range(branch_id.size):
        node_name_id.append("meshnodeids")
        node_name_long.append("meshnodelongnames")

    mesh1d = Mesh1D(
        name=name,
        network_name=network_name,
        branch_id=branch_id,
        branch_offset=branch_offset,
        node_x=node_x,
        node_y=node_y,
        edge_node=edge_node,
        edge_edge_id=edge_edge_id,
        edge_edge_offset=edge_edge_offset,
        edge_x=edge_x,
        edge_y=edge_y,
        node_name_id=node_name_id,
        node_name_long=node_name_long,
    )
    return mesh1d


def test_mesh1d_get():
    r"""Tests `mesh1d_get_num_topologies` and `network1d_get` to read a network1d from file."""

    with UGrid("./data/AllUGridEntities.nc", "r") as ug:
        num_mesh1d_topologies = ug.mesh1d_get_num_topologies()
        mesh1d = ug.mesh1d_get(num_mesh1d_topologies - 1)

        expected_mesh1d = create_mesh1d()

        assert expected_mesh1d.name == mesh1d.name
        assert expected_mesh1d.network_name == mesh1d.network_name

        assert_array_equal(mesh1d.edge_node, expected_mesh1d.edge_node)
        assert_array_equal(mesh1d.branch_id, expected_mesh1d.branch_id)
        assert_array_equal(mesh1d.branch_offset, expected_mesh1d.branch_offset)

        assert_array_equal(mesh1d.node_name_id, expected_mesh1d.node_name_id)
        assert_array_equal(mesh1d.node_name_long, expected_mesh1d.node_name_long)


def test_mesh1d_define_and_put():
    r"""Tests `mesh1d_define` and `mesh1d_put` to define and write a mesh1d to file."""

    with UGrid("./data/written_files/Mesh1DWrite.nc", "w+") as ug:
        mesh1d = create_mesh1d()
        topology_id = ug.mesh1d_define(mesh1d)
        assert topology_id == 0
        ug.mesh1d_put(topology_id, mesh1d)
