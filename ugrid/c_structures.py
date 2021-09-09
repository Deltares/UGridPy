from __future__ import annotations

from ctypes import POINTER, Structure, c_char, c_double, c_int

import numpy as np
from numpy.ctypeslib import as_ctypes

from ugrid.py_structures import Network1D


def decode_byte_vector_to_str(bvector: bytes, ncolumns: int) -> str:
    return bvector[:ncolumns].decode("UTF-8").strip()


def decode_byte_vector_to_list_of_str(
    bvector: bytes, nrows: int, ncolumns: int
) -> list:
    return [
        bvector[ncolumns * r : ncolumns * (r + 1)].decode("UTF-8").strip() for r in range(nrows)
    ]


class CNetwork1D(Structure):
    """C-structure intended for internal use only.
    It represents a Mesh2D struct as described by the MeshKernel API.

    Used for communicating with the MeshKernel dll.

    Attributes:
    """

    _fields_ = [
        ("name", POINTER(c_char)),
        ("node_x", POINTER(c_double)),
        ("node_y", POINTER(c_double)),
        ("node_name_id", POINTER(c_char)),
        ("node_name_long", POINTER(c_char)),
        ("branch_node", POINTER(c_int)),
        ("branch_length", POINTER(c_double)),
        ("branch_order", POINTER(c_int)),
        ("branch_name_id", POINTER(c_char)),
        ("branch_name_long", POINTER(c_char)),
        ("geometry_nodes_x", POINTER(c_double)),
        ("geometry_nodes_y", POINTER(c_double)),
        ("num_geometry_nodes", c_int),
        ("num_nodes", c_int),
        ("num_branches", c_int),
        ("is_spherical", c_int),
        ("start_index", c_int),
    ]

    @staticmethod
    def from_py_structure(network1D: Network1D) -> CNetwork1D:
        """Creates a new CMesh instance from a given Mesh2d instance.

        Args:
            network1D (Network1D): Class of numpy instances owning the state.

        Returns:
            CMesh2d: The created CMesh2d instance.
        """

        c_network1d = CNetwork1D()

        # Set the pointers
        c_network1d.name = as_ctypes(network1D.name)
        c_network1d.node_x = as_ctypes(network1D.node_x)
        c_network1d.node_y = as_ctypes(network1D.node_y)
        c_network1d.node_name_id = as_ctypes(network1D.node_name_id)
        c_network1d.node_name_long = as_ctypes(network1D.node_name_long)
        c_network1d.branch_node = as_ctypes(network1D.branch_node)
        c_network1d.branch_length = as_ctypes(network1D.branch_length)
        c_network1d.branch_order = as_ctypes(network1D.branch_order)
        c_network1d.branch_name_id = as_ctypes(network1D.branch_name_id)
        c_network1d.branch_name_long = as_ctypes(network1D.branch_name_long)
        c_network1d.geometry_nodes_x = as_ctypes(network1D.geometry_nodes_x)
        c_network1d.geometry_nodes_y = as_ctypes(network1D.geometry_nodes_y)

        # Set the sizes
        c_network1d.num_geometry_nodes = c_network1d.geometry_nodes_x.size
        c_network1d.num_nodes = network1D.node_x.size
        c_network1d.num_branches = network1D.branch_node.size // 2
        c_network1d.is_spherical = network1D.is_spherical
        c_network1d.start_index = network1D.start_index

        return c_network1d

    def allocate_memory(self, name_size, name_long_size) -> Network1D:
        """Allocate data according to the parameters with the "num_" prefix.
        The pointers are then set to the freshly allocated memory.
        The memory is owned by the Mesh2d instance which is returned by this method.

        Returns:
            Mesh2d: The object owning the allocated memory.
        """

        name = np.chararray(self.num_nodes * name_size)
        node_x = np.empty(self.num_nodes, dtype=np.double)
        node_y = np.empty(self.num_nodes, dtype=np.double)
        node_name_id = np.chararray(self.num_nodes * name_size)
        node_name_long = np.chararray(self.num_nodes * name_long_size)
        branch_node = np.empty(self.num_nodes, dtype=np.int)
        branch_length = np.empty(self.num_nodes, dtype=np.double)
        branch_order = np.empty(self.num_branches, dtype=np.int)
        branch_name_id = np.chararray(self.num_branches * name_size)
        branch_name_long = np.chararray(self.num_branches * name_long_size)
        geometry_nodes_x = np.empty(self.num_geometry_nodes, dtype=np.double)
        geometry_nodes_y = np.empty(self.num_geometry_nodes, dtype=np.double)

        self.name = name.ctypes.data_as(POINTER(c_char))
        self.node_x = as_ctypes(node_x)
        self.node_y = as_ctypes(node_y)
        self.node_name_id = node_name_id.ctypes.data_as(POINTER(c_char))
        self.node_name_long = node_name_long.ctypes.data_as(POINTER(c_char))
        self.branch_node = as_ctypes(branch_node)
        self.branch_length = as_ctypes(branch_length)
        self.branch_order = as_ctypes(branch_order)
        self.branch_name_id = branch_name_id.ctypes.data_as(POINTER(c_char))
        self.branch_name_long = branch_name_long.ctypes.data_as(POINTER(c_char))
        self.geometry_nodes_x = as_ctypes(geometry_nodes_x)
        self.geometry_nodes_y = as_ctypes(geometry_nodes_y)

        return Network1D(
            node_x,
            node_y,
            branch_node,
            branch_length,
            branch_order,
            geometry_nodes_x,
            geometry_nodes_y,
        )
