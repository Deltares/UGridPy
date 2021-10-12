import numpy as np
from meshkernel import Mesh2d, Mesh2dFactory

from ugrid import UGrid


def test_mesh2d_meshkernel_define_and_put():
    r"""Tests a meshkernel mesh2d is correctly converted to UGridMesh2D and written to file."""
    node_x = np.array([0.0, 1.0, 1.0, 0.0], dtype=np.double)
    node_y = np.array([0.0, 0.0, 1.0, 1.0], dtype=np.double)

    edge_nodes = np.array([0, 1, 1, 2, 2, 3, 2, 0], dtype=np.int)

    face_nodes = np.array([0, 1, 2, 3], dtype=np.int)
    nodes_per_face = np.array([4], dtype=np.int)

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

    mesh2d_mesh_kernel = Mesh2dFactory.create_rectilinear_mesh(
        3, 7, origin_x=-0.1, origin_y=-1.5
    )

    ugrid_mesh2d = UGrid.from_meshkernel_mesh2d_to_ugrid_mesh2d(
        mesh2d=mesh2d_mesh_kernel, name="mesh2d", is_spherical=False
    )
    with UGrid("./data/written_files/Mesh2DMesKernelWithFactoryWrite.nc", "w+") as ug:
        topology_id = ug.mesh2d_define(ugrid_mesh2d)
        assert topology_id == 0
        ug.mesh2d_put(topology_id, ugrid_mesh2d)
