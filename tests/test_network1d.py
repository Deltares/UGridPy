import numpy as np
from numpy.testing import assert_array_equal

from ugrid import UGrid, UGridNetwork1D


def create_network1d():
    r"""Creates an instance of UGridNetwork1D to be used for testing"""

    node_x = np.array([293.78, 538.89], dtype=np.double)
    node_y = np.array([27.48, 956.75], dtype=np.double)
    edge_node = np.array([0, 1], dtype=np.int)
    edge_length = np.array([1165.29], dtype=np.double)
    branch_order = np.array([0], dtype=np.int)

    geometry_nodes_x = np.array(
        [
            293.78,
            278.97,
            265.31,
            254.17,
            247.44,
            248.3,
            259.58,
            282.24,
            314.61,
            354.44,
            398.94,
            445,
            490.6,
            532.84,
            566.64,
            589.08,
            600.72,
            603.53,
            599.27,
            590.05,
            577.56,
            562.97,
            547.12,
            530.67,
            538.89,
        ],
        dtype=np.double,
    )

    geometry_nodes_y = np.array(
        [
            27.48,
            74.87,
            122.59,
            170.96,
            220.12,
            269.67,
            317.89,
            361.93,
            399.39,
            428.84,
            450.76,
            469.28,
            488.89,
            514.78,
            550.83,
            594.93,
            643.09,
            692.6,
            742.02,
            790.79,
            838.83,
            886.28,
            933.33,
            980.17,
            956.75,
        ],
        dtype=np.double,
    )

    num_branch_geometry_nodes = np.array([len(geometry_nodes_x)], dtype=np.int)

    network1d = UGridNetwork1D(
        name="network",
        node_x=node_x,
        node_y=node_y,
        edge_node=edge_node,
        edge_length=edge_length,
        edge_order=branch_order,
        geometry_nodes_x=geometry_nodes_x,
        geometry_nodes_y=geometry_nodes_y,
        num_edge_geometry_nodes=num_branch_geometry_nodes,
    )

    network1d.node_id = ["nodesids", "nodesids"]
    network1d.node_long_name = ["nodeslongNames", "nodeslongNames"]
    network1d.edge_id = ["branchids"]
    network1d.edge_long_name = ["branchlongNames"]

    return network1d


def test_network1d_get():
    r"""Tests `network1d_get_num_topologies` and `network1d_get` to read a network1d from file."""

    with UGrid("./data/AllUGridEntities.nc", "r") as ug:
        num_network_topologies = ug.network1d_get_num_topologies()
        network1d = ug.network1d_get(num_network_topologies - 1)

        expected_network1d = create_network1d()

        assert expected_network1d.name == network1d.name

        assert_array_equal(network1d.node_id, expected_network1d.node_id)
        assert_array_equal(network1d.node_long_name, expected_network1d.node_long_name)

        assert_array_equal(network1d.edge_id, expected_network1d.edge_id)
        assert_array_equal(network1d.edge_long_name, expected_network1d.edge_long_name)

        assert_array_equal(network1d.node_x, expected_network1d.node_x)
        assert_array_equal(network1d.node_y, expected_network1d.node_y)

        assert_array_equal(network1d.edge_node, expected_network1d.edge_node)
        assert_array_equal(network1d.edge_length, expected_network1d.edge_length)

        assert_array_equal(
            network1d.geometry_nodes_x, expected_network1d.geometry_nodes_x
        )
        assert_array_equal(
            network1d.geometry_nodes_y, expected_network1d.geometry_nodes_y
        )


def test_network1d_define_and_put():
    r"""Tests `network1d_define` and `network1d_put` to define and write a mesh1d to file."""

    with UGrid("./data/written_files/Network1DWrite.nc", "w+") as ug:
        network1d = create_network1d()
        topology_id = ug.network1d_define(network1d)
        assert topology_id == 0
        ug.network1d_put(topology_id, network1d)
