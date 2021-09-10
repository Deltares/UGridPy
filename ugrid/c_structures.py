from __future__ import annotations

from ctypes import POINTER, Structure, c_double, c_int, c_char_p

import numpy as np
from numpy.ctypeslib import as_ctypes

from ugrid.py_structures import Network1D, Mesh1D


def decode_byte_vector_to_string(byte_vector: bytes, ncolumns: int) -> str:
    return byte_vector[:ncolumns].decode("UTF-8").strip()


def decode_byte_vector_to_list_of_string(
        byte_vector: bytes, nrows: int, str_size: int
) -> list:
    return [
        byte_vector[str_size * r: str_size * (r + 1)].decode("UTF-8").strip() for r in range(nrows)
    ]


def pad_and_join_list_of_strings(string_list: list, str_size: int):
    for i in range(len(string_list)):
        string_list[i] = string_list[i].ljust(str_size)
    result = "".join(string_list)
    return result


class CNetwork1D(Structure):
    """C-structure intended for internal use only.
    It represents a Network1d struct as described by the UGrid API.

    Used for communicating with the UGrid dll.

    Attributes:
    """

    _fields_ = [
        ("name", c_char_p),
        ("node_x", POINTER(c_double)),
        ("node_y", POINTER(c_double)),
        ("node_name_id", c_char_p),
        ("node_name_long", c_char_p),
        ("branch_node", POINTER(c_int)),
        ("branch_length", POINTER(c_double)),
        ("branch_order", POINTER(c_int)),
        ("branch_name_id", c_char_p),
        ("branch_name_long", c_char_p),
        ("geometry_nodes_x", POINTER(c_double)),
        ("geometry_nodes_y", POINTER(c_double)),
        ("num_geometry_nodes", c_int),
        ("num_nodes", c_int),
        ("num_branches", c_int),
        ("is_spherical", c_int),
        ("start_index", c_int),
    ]

    @staticmethod
    def from_py_structure(network1D: Network1D, name_size: int, name_long_size: int) -> CNetwork1D:
        """Creates a new CMesh instance from a given Mesh2d instance.

        Args:
            network1D (Network1D): Class of numpy instances owning the state.

        Returns:
            CMesh2d: The created CMesh2d instance.
        """

        name_padded = network1D.name.ljust(name_size)

        node_name_id = pad_and_join_list_of_strings(network1D.node_name_id, name_size)
        node_name_long = pad_and_join_list_of_strings(network1D.node_name_long, name_long_size)

        branch_name_id = pad_and_join_list_of_strings(network1D.branch_name_id, name_size)
        branch_name_long = pad_and_join_list_of_strings(network1D.branch_name_long, name_long_size)

        c_network1d = CNetwork1D()

        # Set the pointers
        c_network1d.name = c_char_p(name_padded.encode('utf-8'))
        c_network1d.node_x = as_ctypes(network1D.node_x)
        c_network1d.node_y = as_ctypes(network1D.node_y)
        c_network1d.node_name_id = c_char_p(node_name_id.encode('utf-8'))
        c_network1d.node_name_long = c_char_p(node_name_long.encode('utf-8'))
        c_network1d.branch_node = as_ctypes(network1D.branch_node)
        c_network1d.branch_length = as_ctypes(network1D.branch_length)
        c_network1d.branch_order = as_ctypes(network1D.branch_order)
        c_network1d.branch_name_id = c_char_p(branch_name_id.encode('utf-8'))
        c_network1d.branch_name_long = c_char_p(branch_name_long.encode('utf-8'))
        c_network1d.geometry_nodes_x = as_ctypes(network1D.geometry_nodes_x)
        c_network1d.geometry_nodes_y = as_ctypes(network1D.geometry_nodes_y)

        # Set the sizes
        c_network1d.num_geometry_nodes = network1D.geometry_nodes_x.size
        c_network1d.num_nodes = network1D.node_x.size
        c_network1d.num_branches = network1D.branch_node.size // 2
        c_network1d.is_spherical = network1D.is_spherical
        c_network1d.start_index = network1D.start_index

        return c_network1d

    def allocate_memory(self, name_size: int, name_long_size: int) -> Network1D:
        """Allocate data according to the parameters with the "num_" prefix.
        The pointers are then set to the freshly allocated memory.
        The memory is owned by the Mesh2d instance which is returned by this method.

        Returns:
            Mesh2d: The object owning the allocated memory.
        """

        name = " " * name_size
        node_x = np.empty(self.num_nodes, dtype=np.double)
        node_y = np.empty(self.num_nodes, dtype=np.double)
        node_name_id = " " * self.num_nodes * name_size
        node_name_long = " " * self.num_nodes * name_long_size
        branch_node = np.empty(self.num_nodes, dtype=np.int)
        branch_length = np.empty(self.num_branches, dtype=np.double)
        branch_order = np.empty(self.num_branches, dtype=np.int)
        branch_name_id = " " * self.num_branches * name_size
        branch_name_long = " " * self.num_branches * name_long_size
        geometry_nodes_x = np.empty(self.num_geometry_nodes, dtype=np.double)
        geometry_nodes_y = np.empty(self.num_geometry_nodes, dtype=np.double)

        self.name = c_char_p(name.encode('utf-8'))
        self.node_x = as_ctypes(node_x)
        self.node_y = as_ctypes(node_y)
        self.node_name_id = c_char_p(node_name_id.encode('utf-8'))
        self.node_name_long = c_char_p(node_name_long.encode('utf-8'))
        self.branch_node = as_ctypes(branch_node)
        self.branch_length = as_ctypes(branch_length)
        self.branch_order = as_ctypes(branch_order)
        self.branch_name_id = c_char_p(branch_name_id.encode('utf-8'))
        self.branch_name_long = c_char_p(branch_name_long.encode('utf-8'))
        self.geometry_nodes_x = as_ctypes(geometry_nodes_x)
        self.geometry_nodes_y = as_ctypes(geometry_nodes_y)

        return Network1D(
            node_x,
            node_y,
            branch_node,
            branch_length,
            branch_order,
            geometry_nodes_x,
            geometry_nodes_y)


class CMesh1D(Structure):
    """C-structure intended for internal use only.
    It represents a Mesh1d struct as described by the UGrid API.

    Used for communicating with the UGrid dll.

    Attributes:
    """

    _fields_ = [
        ("name", c_char_p),
        ("network_name", c_char_p),
        ("node_x", POINTER(c_double)),
        ("node_y", POINTER(c_double)),
        ("edge_node", POINTER(c_int)),
        ("branch_id", POINTER(c_int)),
        ("branch_offset", POINTER(c_double)),
        ("node_name_id", c_char_p),
        ("node_name_long", c_char_p),
        ("edge_edge_id", POINTER(c_int)),
        ("edge_edge_offset", POINTER(c_double)),
        ("edge_x", POINTER(c_double)),
        ("edge_y", POINTER(c_double)),
        ("num_nodes", c_int),
        ("num_edges", c_int),
        ("is_spherical", c_int),
        ("start_index", c_int),
        ("double_fill_value", c_double),
        ("int_fill_value", c_int),
    ]

    @staticmethod
    def from_py_structure(mesh1d: Mesh1D, name_size: int, name_long_size: int) -> CNetwork1D:
        """Creates a new CMesh instance from a given Mesh2d instance.

        Args:
            mesh1d (Network1D): Class of numpy instances owning the state.

        Returns:
            CMesh2d: The created CMesh2d instance.
        """

        mesh1d_name_padded = mesh1d.name.ljust(name_size)
        network1d_name_padded = mesh1d.network_name.ljust(name_size)

        node_name_id = pad_and_join_list_of_strings(mesh1d.node_name_id, name_size)
        node_name_long = pad_and_join_list_of_strings(mesh1d.node_name_long, name_long_size)

        c_mesh1d = CMesh1D()

        # Set the pointers
        c_mesh1d.name = c_char_p(mesh1d_name_padded.encode('utf-8'))
        c_mesh1d.network_name = c_char_p(network1d_name_padded.encode('utf-8'))
        c_mesh1d.node_x = as_ctypes(mesh1d.node_x)
        c_mesh1d.node_y = as_ctypes(mesh1d.node_y)
        c_mesh1d.edge_node = as_ctypes(mesh1d.edge_node)
        c_mesh1d.branch_id = as_ctypes(mesh1d.branch_id)
        c_mesh1d.branch_offset = as_ctypes(mesh1d.branch_offset)
        c_mesh1d.node_name_id = c_char_p(node_name_id.encode('utf-8'))
        c_mesh1d.node_name_long = c_char_p(node_name_long.encode('utf-8'))
        c_mesh1d.edge_edge_id = as_ctypes(mesh1d.edge_edge_id)
        c_mesh1d.edge_edge_offset = as_ctypes(mesh1d.edge_edge_offset)
        c_mesh1d.edge_x = as_ctypes(mesh1d.edge_x)
        c_mesh1d.edge_y = as_ctypes(mesh1d.edge_y)

        # Set the sizes
        c_mesh1d.num_nodes = mesh1d.node_x.size
        c_mesh1d.num_edges = mesh1d.edge_node.size // 2
        c_mesh1d.is_spherical = mesh1d.is_spherical
        c_mesh1d.start_index = mesh1d.start_index
        c_mesh1d.double_fill_value = mesh1d.double_fill_value
        c_mesh1d.int_fill_value = mesh1d.int_fill_value

        return c_mesh1d

    def allocate_memory(self, name_size: int, name_long_size: int) -> Network1D:
        """Allocate data according to the parameters with the "num_" prefix.
        The pointers are then set to the freshly allocated memory.
        The memory is owned by the Mesh2d instance which is returned by this method.

        Returns:
            Mesh2d: The object owning the allocated memory.
        """

        name = " " * name_size
        network_name = " " * name_size
        node_x = np.empty(self.num_nodes, dtype=np.double)
        node_y = np.empty(self.num_nodes, dtype=np.double)
        edge_node = np.empty(self.num_edges * 2, dtype=np.int)
        branch_id = np.empty(self.num_nodes, dtype=np.int)
        branch_offset = np.empty(self.num_nodes, dtype=np.double)
        node_name_id = " " * self.num_nodes * name_size
        node_name_long = " " * self.num_nodes * name_long_size
        edge_edge_id = np.empty(self.num_edges, dtype=np.int)
        edge_edge_offset = np.empty(self.num_edges, dtype=np.double)
        edge_x = np.empty(self.num_edges, dtype=np.double)
        edge_y = np.empty(self.num_edges, dtype=np.double)

        self.name = c_char_p(name.encode('utf-8'))
        self.network_name = c_char_p(network_name.encode('utf-8'))
        self.node_x = as_ctypes(node_x)
        self.node_y = as_ctypes(node_y)
        self.edge_node = as_ctypes(edge_node)
        self.branch_id = as_ctypes(branch_id)
        self.branch_offset = as_ctypes(branch_offset)
        self.node_name_id = c_char_p(node_name_id.encode('utf-8'))
        self.node_name_long = c_char_p(node_name_long.encode('utf-8'))
        self.edge_edge_id = as_ctypes(edge_edge_id)
        self.edge_edge_offset = as_ctypes(edge_edge_offset)
        self.edge_x = as_ctypes(edge_x)
        self.edge_y = as_ctypes(edge_y)

        return Mesh1D(name=name,
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
                      node_name_long=node_name_long)
