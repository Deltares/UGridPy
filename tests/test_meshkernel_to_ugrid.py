import numpy as np
from meshkernel import Mesh1d, Mesh2d
from test_utils import Mesh2dFactory

from ugrid import UGrid


def test_mesh2d_meshkernel_define_and_put():
    r"""Tests a meshkernel mesh2d is correctly converted to UGridMesh2D and written to file."""
    node_x = np.array([0.0, 1.0, 1.0, 0.0], dtype=np.double)
    node_y = np.array([0.0, 0.0, 1.0, 1.0], dtype=np.double)

    edge_nodes = np.array([0, 1, 1, 2, 2, 3, 2, 0], dtype=np.int32)

    face_nodes = np.array([0, 1, 2, 3], dtype=np.int32)
    nodes_per_face = np.array([4], dtype=np.int32)

    ugrid_mesh2d = Mesh2d(
        node_x=node_x,
        node_y=node_y,
        edge_nodes=edge_nodes,
        face_nodes=face_nodes,
        nodes_per_face=nodes_per_face,
    )

    ugrid_mesh2d = UGrid.from_meshkernel_mesh2d_to_ugrid_mesh2d(
        mesh2d=ugrid_mesh2d, name="mesh2d", is_spherical=False
    )
    with UGrid("./data/written_files/Mesh2DMesKernelWrite.nc", "w+") as ug:
        topology_id = ug.mesh2d_define(ugrid_mesh2d)
        assert topology_id == 0
        ug.mesh2d_put(topology_id, ugrid_mesh2d)


def test_mesh2d_meshkernel_factory_define_and_put():
    r"""Tests a meshkernel mesh2d is correctly converted to UGridMesh2D and written to file
    when Mesh2dFactory is used."""

    mesh2d_mesh_kernel = Mesh2dFactory.create(3, 7, origin_x=-0.1, origin_y=-1.5)

    ugrid_mesh2d = UGrid.from_meshkernel_mesh2d_to_ugrid_mesh2d(
        mesh2d=mesh2d_mesh_kernel, name="mesh2d", is_spherical=False
    )
    with UGrid("./data/written_files/Mesh2DMesKernelWithFactoryWrite.nc", "w+") as ug:
        topology_id = ug.mesh2d_define(ugrid_mesh2d)
        assert topology_id == 0
        ug.mesh2d_put(topology_id, ugrid_mesh2d)


def test_mesh1d_meshkernel_define_and_put():
    r"""Tests a meshkernel mesh1d is correctly converted to UGridMesh1D and written to file."""

    # create a meshkernel mesh1d
    node_x = np.array([0.0, 1.0, 2.0, 3.0], dtype=np.double)
    node_y = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.double)
    edge_nodes = np.array([0, 1, 1, 2, 2, 3], dtype=np.int32)
    mesh1d = Mesh1d(node_x=node_x, node_y=node_y, edge_nodes=edge_nodes)

    # all extra data required to instatiate a valid ugrid mesh1d
    branch_id = np.array([0, 1, 1, 2, 2, 3, 2, 0], dtype=np.int32)
    branch_offset = np.array([0, 1, 1, 2, 2, 3, 2, 0], dtype=np.double)
    node_name_id = ["branchname"]
    node_name_long = ["branchnamelong"]
    edge_edge_id = np.array([0, 0, 0], dtype=np.int32)
    edge_edge_offset = np.array([0.5, 1.5, 2.5], dtype=np.double)
    edge_x = np.array([0.5, 1.5, 2.5], dtype=np.double)
    edge_y = np.array([0.0, 0.0, 0.0], dtype=np.double)

    ugrid_mesh1d = UGrid.from_meshkernel_mesh1d_to_ugrid_mesh1d(
        mesh1d=mesh1d,
        name="mesh1d",
        network_name="network1d",
        node_edge_id=branch_id,
        node_edge_offset=branch_offset,
        node_name_id=node_name_id,
        node_name_long=node_name_long,
        edge_edge_id=edge_edge_id,
        edge_edge_offset=edge_edge_offset,
        edge_x=edge_x,
        edge_y=edge_y,
        double_fill_value=-999.0,
        int_fill_value=999,
    )

    with UGrid("./data/written_files/Mesh1DMesKernelWrite.nc", "w+") as ug:
        topology_id = ug.mesh1d_define(ugrid_mesh1d)
        assert topology_id == 0
        ug.mesh1d_put(topology_id, ugrid_mesh1d)
