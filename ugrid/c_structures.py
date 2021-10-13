from __future__ import annotations

from ctypes import POINTER, Structure, c_char_p, c_double, c_int

import numpy as np
from numpy.ctypeslib import as_ctypes

from ugrid.py_structures import UGridContacts, UGridMesh1D, UGridMesh2D, UGridNetwork1D


def decode_byte_vector_to_string(byte_vector: bytes, ncolumns: int) -> str:
    """From byte vector to string"""
    return byte_vector[:ncolumns].decode("ASCII").strip()


def decode_byte_vector_to_list_of_strings(
    byte_vector: bytes, nrows: int, str_size: int
) -> list:
    """From byte vector to a vector of strings"""
    return [
        byte_vector[str_size * r : str_size * (r + 1)].decode("ASCII").strip()
        for r in range(nrows)
    ]


def pad_and_join_list_of_strings(string_list: list, str_size: int):
    """Pad each entry  to a defined size and join the padded entries into one string"""
    for i in range(len(string_list)):
        string_list[i] = string_list[i].ljust(str_size)
    result = "".join(string_list)
    return result


def numpy_array_to_ctypes(arr):
    """Cast an array to ctypes only if its len is not 0"""
    if len(arr) == 0:
        return None
    return as_ctypes(arr)


class CUGridNetwork1D(Structure):
    """C-structure intended for internal use only.
    It represents a Network1d struct as described by the UGrid API.

    Used for communicating with the UGrid dll.

    Attributes:
        name (c_char_p): The network name.
        node_x (POINTER(c_double)): The x-coordinates of the network node.
        node_y (POINTER(c_double)): The y-coordinates of the network node.
        node_id (c_char_p): The node names ids.
        node_long_name (c_char_p): The node long names.
        edge_node (POINTER(c_int)): The nodes defining each branch.
        edge_length (POINTER(c_double)): The edge lengths.
        edge_order (POINTER(c_int)): The order of the branches.
        edge_id (c_char_p): The name of the branches.
        edge_long_name (c_char_p): The long name of the branches.
        geometry_nodes_x (POINTER(c_double)): The geometry nodes x coordinates.
        geometry_nodes_y (POINTER(c_double)): The geometry nodes y coordinates.
        num_edges_geometry_nodes (POINTER(c_int)): The number of geometry nodes for each branch.
        num_geometry_nodes (c_int): The number of geometry nodes.
        num_nodes (c_int): The number of network1d nodes.
        num_edges (c_int): The number of network1d branches.
        is_spherical (c_int): 1 if the coordinates are in a spherical system, 0 otherwise .
        start_index (c_int): The start index used in arrays using indices, such as in the branch_node array.
    """

    _fields_ = [
        ("name", c_char_p),
        ("node_x", POINTER(c_double)),
        ("node_y", POINTER(c_double)),
        ("node_id", c_char_p),
        ("node_long_name", c_char_p),
        ("edge_node", POINTER(c_int)),
        ("edge_length", POINTER(c_double)),
        ("edge_order", POINTER(c_int)),
        ("edge_id", c_char_p),
        ("edge_long_name", c_char_p),
        ("geometry_nodes_x", POINTER(c_double)),
        ("geometry_nodes_y", POINTER(c_double)),
        ("num_edges_geometry_nodes", POINTER(c_int)),
        ("num_geometry_nodes", c_int),
        ("num_nodes", c_int),
        ("num_edges", c_int),
        ("is_spherical", c_int),
        ("start_index", c_int),
    ]

    @staticmethod
    def from_py_structure(
        ugrid_network1D: UGridNetwork1D, name_size: int, name_long_size: int
    ) -> CUGridNetwork1D:
        """Creates a new CMesh instance from a given Mesh2d instance.

        Args:
            ugrid_network1D (UGridNetwork1D): Class of numpy instances owning the state.

        Returns:
            CMesh2d: The created CMesh2d instance.
        """

        name_padded = ugrid_network1D.name.ljust(name_long_size)

        node_id = pad_and_join_list_of_strings(ugrid_network1D.node_id, name_size)
        node_long_name = pad_and_join_list_of_strings(
            ugrid_network1D.node_long_name, name_long_size
        )

        edge_id = pad_and_join_list_of_strings(ugrid_network1D.edge_id, name_size)
        edge_long_name = pad_and_join_list_of_strings(
            ugrid_network1D.edge_long_name, name_long_size
        )

        c_ugrid_network = CUGridNetwork1D()

        # Set the pointers
        c_ugrid_network.name = c_char_p(name_padded.encode("ASCII"))
        c_ugrid_network.node_x = numpy_array_to_ctypes(ugrid_network1D.node_x)
        c_ugrid_network.node_y = numpy_array_to_ctypes(ugrid_network1D.node_y)
        c_ugrid_network.node_id = c_char_p(node_id.encode("ASCII"))
        c_ugrid_network.node_long_name = c_char_p(node_long_name.encode("ASCII"))
        c_ugrid_network.edge_node = numpy_array_to_ctypes(ugrid_network1D.edge_node)
        c_ugrid_network.edge_length = numpy_array_to_ctypes(ugrid_network1D.edge_length)
        c_ugrid_network.edge_order = numpy_array_to_ctypes(ugrid_network1D.edge_order)
        c_ugrid_network.edge_id = c_char_p(edge_id.encode("ASCII"))
        c_ugrid_network.edge_long_name = c_char_p(edge_long_name.encode("ASCII"))
        c_ugrid_network.geometry_nodes_x = numpy_array_to_ctypes(
            ugrid_network1D.geometry_nodes_x
        )
        c_ugrid_network.geometry_nodes_y = numpy_array_to_ctypes(
            ugrid_network1D.geometry_nodes_y
        )

        # Set the sizes
        c_ugrid_network.num_geometry_nodes = ugrid_network1D.geometry_nodes_x.size
        c_ugrid_network.num_nodes = ugrid_network1D.node_x.size
        c_ugrid_network.num_edges = ugrid_network1D.edge_node.size // 2
        c_ugrid_network.is_spherical = ugrid_network1D.is_spherical
        c_ugrid_network.start_index = ugrid_network1D.start_index

        return c_ugrid_network

    def allocate_memory(self, name_size: int, name_long_size: int) -> UGridNetwork1D:
        """Allocate data according to the parameters with the "num_" prefix.
        The pointers are then set to the freshly allocated memory.
        The memory is owned by the Network1D instance which is returned by this method.

        Args:
            name_size (int): The size of the names.
            name_long_size (int): The size of the long names.

        Returns:
            UGridNetwork1D: The object owning the allocated memory.
        """

        name = " " * name_long_size
        node_x = np.empty(self.num_nodes, dtype=np.double)
        node_y = np.empty(self.num_nodes, dtype=np.double)
        node_id = " " * self.num_nodes * name_size
        node_long_name = " " * self.num_nodes * name_long_size
        edge_node = np.empty(self.num_nodes, dtype=np.int)
        edge_length = np.empty(self.num_edges, dtype=np.double)
        edge_order = np.empty(self.num_edges, dtype=np.int)
        edge_id = " " * self.num_edges * name_size
        edge_long_name = " " * self.num_edges * name_long_size
        geometry_nodes_x = np.empty(self.num_geometry_nodes, dtype=np.double)
        geometry_nodes_y = np.empty(self.num_geometry_nodes, dtype=np.double)
        num_edge_geometry_nodes = np.empty(self.num_edges, dtype=np.int)

        self.name = c_char_p(name.encode("ASCII"))
        self.node_x = numpy_array_to_ctypes(node_x)
        self.node_y = numpy_array_to_ctypes(node_y)
        self.node_id = c_char_p(node_id.encode("ASCII"))
        self.node_long_name = c_char_p(node_long_name.encode("ASCII"))
        self.edge_node = numpy_array_to_ctypes(edge_node)
        self.edge_length = numpy_array_to_ctypes(edge_length)
        self.edge_order = numpy_array_to_ctypes(edge_order)
        self.edge_id = c_char_p(edge_id.encode("ASCII"))
        self.edge_long_name = c_char_p(edge_long_name.encode("ASCII"))
        self.geometry_nodes_x = numpy_array_to_ctypes(geometry_nodes_x)
        self.geometry_nodes_y = numpy_array_to_ctypes(geometry_nodes_y)
        self.num_edge_geometry_nodes = numpy_array_to_ctypes(num_edge_geometry_nodes)

        return UGridNetwork1D(
            name=name,
            node_x=node_x,
            node_y=node_y,
            edge_node=edge_node,
            edge_length=edge_length,
            edge_order=edge_order,
            geometry_nodes_x=geometry_nodes_x,
            geometry_nodes_y=geometry_nodes_y,
            num_edge_geometry_nodes=num_edge_geometry_nodes,
        )


class CUGridMesh1D(Structure):
    """C-structure intended for internal use only.
    It represents a Mesh1d struct as described by the UGrid API.

    Used for communicating with the UGrid dll.

    Attributes:
        name (c_char_p): The mesh name.
        network_name (c_char_p): The x-coordinates of the network node.
        node_x (POINTER(c_double)):  The node x coordinate.
        node_y (POINTER(c_double)):  The node y coordinate.
        edge_node (POINTER(c_int)): The edge node connectivity.
        node_edge_id (POINTER(c_int)):  The network edge id where every node lies.
        branch_offset (POINTER(c_double)): The offset of each node on the network edge
        node_name_id (POINTER(c_int)): The node name.
        node_name_long (c_char_p): The node long name.
        edge_edge_id (c_char_p): The network edge id where every edge lies.
        edge_edge_offset (POINTER(c_double)): The offset of each edge on the network edge.
        edge_x (POINTER(c_double)): The edge x coordinate.
        edge_y (c_int): The edge y coordinate.
        num_nodes (c_int): The number of nodes.
        num_edges (c_int): The number of edges.
        is_spherical (c_int): 1 if coordinates are in a spherical system, 0 otherwise.
        start_index (c_int): The start index used in arrays using indices, such as in the branch_node array.
        double_fill_value (c_double): The fill value for array of doubles.
        int_fill_value (c_int): The fill value for array of integers.
    """

    _fields_ = [
        ("name", c_char_p),
        ("network_name", c_char_p),
        ("node_x", POINTER(c_double)),
        ("node_y", POINTER(c_double)),
        ("edge_node", POINTER(c_int)),
        ("node_edge_id", POINTER(c_int)),
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
    def from_py_structure(
        mesh1d: UGridMesh1D, name_size: int, name_long_size: int
    ) -> CUGridMesh1D:
        """Creates a new CMesh instance from a given Mesh2d instance.

        Args:
            name_size (int): The size of the names.
            name_long_size (int): The size of the long names.
            mesh1d (UGridMesh1D): Class of numpy instances owning the state.

        Returns:
            CMesh2d: The created CMesh2d instance.
        """

        c_mesh1d = CUGridMesh1D()

        # Set the pointers
        mesh1d_name_padded = mesh1d.name.ljust(name_long_size)
        network1d_name_padded = mesh1d.network_name.ljust(name_long_size)
        node_name_id = pad_and_join_list_of_strings(mesh1d.node_name_id, name_size)
        node_name_long = pad_and_join_list_of_strings(
            mesh1d.node_name_long, name_long_size
        )

        c_mesh1d.name = c_char_p(mesh1d_name_padded.encode("ASCII"))
        c_mesh1d.network_name = c_char_p(network1d_name_padded.encode("ASCII"))
        c_mesh1d.node_x = numpy_array_to_ctypes(mesh1d.node_x)
        c_mesh1d.node_y = numpy_array_to_ctypes(mesh1d.node_y)
        c_mesh1d.edge_node = numpy_array_to_ctypes(mesh1d.edge_node)
        c_mesh1d.node_edge_id = numpy_array_to_ctypes(mesh1d.node_edge_id)
        c_mesh1d.branch_offset = numpy_array_to_ctypes(mesh1d.node_edge_offset)
        c_mesh1d.node_name_id = c_char_p(node_name_id.encode("ASCII"))
        c_mesh1d.node_name_long = c_char_p(node_name_long.encode("ASCII"))
        c_mesh1d.edge_edge_id = numpy_array_to_ctypes(mesh1d.edge_edge_id)
        c_mesh1d.edge_edge_offset = numpy_array_to_ctypes(mesh1d.edge_edge_offset)
        c_mesh1d.edge_x = numpy_array_to_ctypes(mesh1d.edge_x)
        c_mesh1d.edge_y = numpy_array_to_ctypes(mesh1d.edge_y)

        # Set the sizes
        c_mesh1d.num_nodes = mesh1d.node_x.size
        c_mesh1d.num_edges = mesh1d.edge_node.size // 2

        # Set other properties
        c_mesh1d.is_spherical = mesh1d.is_spherical
        c_mesh1d.start_index = mesh1d.start_index

        return c_mesh1d

    def allocate_memory(self, name_size: int, name_long_size: int) -> UGridMesh1D:
        """Allocate data according to the parameters with the "num_" prefix.
        The pointers are then set to the freshly allocated memory.
        The memory is owned by the Mesh1d instance which is returned by this method.

        Args:
            name_size (int): The size of the names.
            name_long_size (int): The size of the long names.

        Returns:
            UGridMesh1D: The object owning the allocated memory.
        """

        name = " " * name_long_size
        network_name = " " * name_long_size
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

        self.name = c_char_p(name.encode("ASCII"))
        self.network_name = c_char_p(network_name.encode("ASCII"))
        self.node_x = numpy_array_to_ctypes(node_x)
        self.node_y = numpy_array_to_ctypes(node_y)
        self.edge_node = numpy_array_to_ctypes(edge_node)
        self.node_edge_id = numpy_array_to_ctypes(branch_id)
        self.branch_offset = numpy_array_to_ctypes(branch_offset)
        self.node_name_id = c_char_p(node_name_id.encode("ASCII"))
        self.node_name_long = c_char_p(node_name_long.encode("ASCII"))
        self.edge_edge_id = numpy_array_to_ctypes(edge_edge_id)
        self.edge_edge_offset = numpy_array_to_ctypes(edge_edge_offset)
        self.edge_x = numpy_array_to_ctypes(edge_x)
        self.edge_y = numpy_array_to_ctypes(edge_y)

        return UGridMesh1D(
            name=name,
            network_name=network_name,
            node_edge_id=branch_id,
            node_edge_offset=branch_offset,
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


class CUGridMesh2D(Structure):
    """C-structure intended for internal use only.
    It represents a Mesh2D struct as described by the UGrid API.

    Used for communicating with the UGrid dll.

    Attributes:
        name (c_char_p): The mesh name.
        edge_nodes (POINTER(c_int)): The nodes composing each mesh 2d edge.
        face_nodes (POINTER(c_int)): The nodes composing each mesh 2d face.
        nodes_per_face (POINTER(c_int)): The nodes composing each mesh 2d face.
        node_x (POINTER(c_double)): The x-coordinates of the nodes.
        node_y (POINTER(c_double)): The y-coordinates of the nodes.
        edge_x (POINTER(c_double)): The x-coordinates of the mesh edges' middle points.
        edge_y (POINTER(c_double)): The x-coordinates of the mesh edges' middle points.
        face_x (POINTER(c_double)): The x-coordinates of the mesh faces' mass centers.
        face_y (POINTER(c_double)): The y-coordinates of the mesh faces' mass centers.
        edge_face (POINTER(c_int)): The edges composing each face.
        face_edge (POINTER(c_int)): For each face, the edges composing it.
        face_face (POINTER(c_int)): For each face, the neighboring faces.
        node_z (POINTER(c_double)): The node z coordinates.
        edge_z (POINTER(c_double)): The edge z coordinates.
        face_z (POINTER(c_double)): The face z coordinates.
        layer_zs (POINTER(c_double)): The z coordinates of a layer.
        interface_zs (POINTER(c_double)): The z coordinates of a layer interface.
        boundary_node_connectivity (POINTER(c_double)): To be detailed.
        volume_coordinates (POINTER(c_double)): To be detailed.
        num_nodes (c_int): The number of mesh nodes.
        num_edges (c_int): The number of edges.
        num_faces (c_int): The number of faces.
        num_layers (c_int): The number of layers.
        start_index (c_int): The start index used in arrays using indices, such as in the branch_node array.
        num_face_nodes_max (c_int): 1 if coordinates are in a spherical system, 0 otherwise.
        is_spherical (c_int): 1 if coordinates are in a spherical system, 0 otherwise.
        double_fill_value (c_double): The fill value for array of doubles.
        int_fill_value (c_int): The fill value for array of integers.
    """

    _fields_ = [
        ("name", c_char_p),
        ("edge_node", POINTER(c_int)),
        ("face_node", POINTER(c_int)),
        ("node_x", POINTER(c_double)),
        ("node_y", POINTER(c_double)),
        ("edge_x", POINTER(c_double)),
        ("edge_y", POINTER(c_double)),
        ("face_x", POINTER(c_double)),
        ("face_y", POINTER(c_double)),
        ("edge_face", POINTER(c_int)),
        ("face_edge", POINTER(c_int)),
        ("face_face", POINTER(c_int)),
        ("node_z", POINTER(c_double)),
        ("edge_z", POINTER(c_double)),
        ("face_z", POINTER(c_double)),
        ("layer_zs", POINTER(c_double)),
        ("interface_zs", POINTER(c_double)),
        ("boundary_node_connectivity", POINTER(c_double)),
        ("volume_coordinates", POINTER(c_int)),
        ("num_nodes", c_int),
        ("num_edges", c_int),
        ("num_faces", c_int),
        ("num_layers", c_int),
        ("start_index", c_int),
        ("num_face_nodes_max", c_int),
        ("is_spherical", c_int),
        ("double_fill_value", c_double),
        ("int_fill_value", c_int),
    ]

    @staticmethod
    def from_py_structure(mesh2d: UGridMesh2D, name_long_size: int) -> CUGridMesh2D:
        """Creates a new CMesh instance from a given Mesh2d instance.

        Args:
            mesh2d (UGridMesh2D): Class of numpy instances owning the state.
            name_long_size (int): The size of the long names.

        Returns:
            CMesh2d: The created CMesh2d instance.
        """

        c_mesh2d = CUGridMesh2D()

        # Required arrays
        mesh2d_name_padded = mesh2d.name.ljust(name_long_size)
        c_mesh2d.name = c_char_p(mesh2d_name_padded.encode("ASCII"))
        c_mesh2d.edge_node = numpy_array_to_ctypes(mesh2d.edge_node)
        c_mesh2d.node_x = numpy_array_to_ctypes(mesh2d.node_x)
        c_mesh2d.node_y = numpy_array_to_ctypes(mesh2d.node_y)

        # Optional arrays
        c_mesh2d.edge_x = numpy_array_to_ctypes(mesh2d.edge_x)
        c_mesh2d.edge_y = numpy_array_to_ctypes(mesh2d.edge_y)
        c_mesh2d.face_x = numpy_array_to_ctypes(mesh2d.face_x)
        c_mesh2d.face_y = numpy_array_to_ctypes(mesh2d.face_y)
        c_mesh2d.edge_face = numpy_array_to_ctypes(mesh2d.edge_face)

        c_mesh2d.face_node = numpy_array_to_ctypes(mesh2d.face_node)
        c_mesh2d.face_edge = numpy_array_to_ctypes(mesh2d.face_edge)
        c_mesh2d.face_face = numpy_array_to_ctypes(mesh2d.face_face)

        c_mesh2d.node_z = numpy_array_to_ctypes(mesh2d.node_z)
        c_mesh2d.edge_z = numpy_array_to_ctypes(mesh2d.edge_z)
        c_mesh2d.face_z = numpy_array_to_ctypes(mesh2d.face_z)
        c_mesh2d.layer_zs = numpy_array_to_ctypes(mesh2d.layer_zs)
        c_mesh2d.interface_zs = numpy_array_to_ctypes(mesh2d.interface_zs)
        c_mesh2d.boundary_node_connectivity = numpy_array_to_ctypes(
            mesh2d.boundary_node_connectivity
        )
        c_mesh2d.volume_coordinates = numpy_array_to_ctypes(mesh2d.volume_coordinates)

        # Set the sizes
        c_mesh2d.num_nodes = mesh2d.node_x.size
        c_mesh2d.num_edges = mesh2d.edge_node.size // 2
        c_mesh2d.num_faces = mesh2d.face_x.size
        c_mesh2d.num_layers = mesh2d.layer_zs.size

        # Set other properties
        c_mesh2d.start_index = mesh2d.start_index
        c_mesh2d.num_face_nodes_max = mesh2d.num_face_nodes_max
        c_mesh2d.is_spherical = mesh2d.is_spherical
        c_mesh2d.double_fill_value = mesh2d.double_fill_value
        c_mesh2d.int_fill_value = mesh2d.int_fill_value

        return c_mesh2d

    def allocate_memory(self, name_long_size: int) -> UGridMesh2D:
        """Allocate data according to the parameters with the "num_" prefix.
        The pointers are then set to the freshly allocated memory.
        The memory is owned by the Mesh2D instance which is returned by this method.

        Args:
            name_long_size (int): The size of the long names.

        Returns:
            UGridMesh2D: The object owning the allocated memory.
        """

        name = " " * name_long_size
        node_x = np.empty(self.num_nodes, dtype=np.double)
        node_y = np.empty(self.num_nodes, dtype=np.double)
        edge_node = np.empty(self.num_edges * 2, dtype=np.int)

        node_z = np.empty(self.num_nodes, dtype=np.double)
        edge_x = np.empty(self.num_edges, dtype=np.double)
        edge_y = np.empty(self.num_edges, dtype=np.double)
        edge_z = np.empty(self.num_edges, dtype=np.double)
        edge_face = np.empty(self.num_edges * 2, dtype=np.int)

        face_node = np.empty(self.num_faces * self.num_face_nodes_max, dtype=np.int)
        face_edge = np.empty(self.num_faces * self.num_face_nodes_max, dtype=np.int)
        face_face = np.empty(self.num_faces * self.num_face_nodes_max, dtype=np.int)
        face_x = np.empty(self.num_faces, dtype=np.double)
        face_y = np.empty(self.num_faces, dtype=np.double)
        face_z = np.empty(self.num_faces, dtype=np.double)

        layer_zs = np.empty(self.num_layers, dtype=np.double)
        boundary_node_connectivity = np.empty(self.num_nodes, dtype=np.double)
        volume_coordinates = np.empty(self.num_faces, dtype=np.int)

        self.name = c_char_p(name.encode("ASCII"))
        self.edge_node = numpy_array_to_ctypes(edge_node)
        self.face_node = numpy_array_to_ctypes(face_node)
        self.node_x = numpy_array_to_ctypes(node_x)
        self.node_y = numpy_array_to_ctypes(node_y)
        self.edge_x = numpy_array_to_ctypes(edge_x)
        self.edge_y = numpy_array_to_ctypes(edge_y)
        self.face_x = numpy_array_to_ctypes(face_x)
        self.face_y = numpy_array_to_ctypes(face_y)
        self.edge_face = numpy_array_to_ctypes(edge_face)
        self.face_edge = numpy_array_to_ctypes(face_edge)
        self.face_face = numpy_array_to_ctypes(face_face)
        self.node_z = numpy_array_to_ctypes(node_z)
        self.edge_z = numpy_array_to_ctypes(edge_z)
        self.face_z = numpy_array_to_ctypes(face_z)

        self.layer_zs = numpy_array_to_ctypes(layer_zs)
        self.boundary_node_connectivity = numpy_array_to_ctypes(
            boundary_node_connectivity
        )
        self.volume_coordinates = numpy_array_to_ctypes(volume_coordinates)

        if self.num_layers > 1:
            interface_zs = np.empty(self.num_layers - 1, dtype=np.double)
            self.interface_zs = numpy_array_to_ctypes(interface_zs)
        else:
            interface_zs = None
            self.interface_zs = None

        return UGridMesh2D(
            name=name,
            node_x=node_x,
            node_y=node_y,
            edge_node=edge_node,
            face_node=face_node,
            edge_x=edge_x,
            edge_y=edge_y,
            face_x=face_x,
            face_y=face_y,
            edge_face=edge_face,
            face_edge=face_edge,
            face_face=face_face,
            node_z=node_z,
            edge_z=edge_z,
            face_z=face_z,
            layer_zs=layer_zs,
            interface_zs=interface_zs,
            boundary_node_connectivity=boundary_node_connectivity,
            volume_coordinates=volume_coordinates,
        )


class CUGridContacts(Structure):
    """C-structure intended for internal use only.
    It represents a Contacts struct as described by the UGrid API.

    Used for communicating with the UGrid dll.

    Attributes:
        name (c_char_p): The name of the contact entity.
        edges (POINTER(c_int)): The actual contacts, expressed as pair of indices from a mesh index
        to another mesh index.
        contact_type (POINTER(c_int)): For each contact its type.
        contact_name_id (c_char_p): The name of each contact.
        contact_name_long (c_char_p): The long name of each contact.
        mesh_from_name (c_char_p): The name of the mesh where the contacts start.
        mesh_to_name (c_char_p): The name of the mesh where the contacts ends.
        mesh_from_location (c_int): The location type (node, edge or face) at the contact start.
        mesh_to_location (c_int): The location type (node, edge or face) at the contact end.
        num_contacts (c_int): The number of contacts.
    """

    _fields_ = [
        ("name", c_char_p),
        ("edges", POINTER(c_int)),
        ("contact_type", POINTER(c_int)),
        ("contact_name_id", c_char_p),
        ("contact_name_long", c_char_p),
        ("mesh_from_name", c_char_p),
        ("mesh_to_name", c_char_p),
        ("mesh_from_location", c_int),
        ("mesh_to_location", c_int),
        ("num_contacts", c_int),
    ]

    @staticmethod
    def from_py_structure(
        contacts: UGridContacts, name_size: int, name_long_size: int
    ) -> CUGridContacts:
        """Creates a new CContacts instance from a given Contacts instance.

        Args:
            contacts (UGridContacts): Class of numpy instances owning the state.

        Returns:
            CUGridContacts: The created CContacts instance.
        """

        c_contacts = CUGridContacts()

        # Set the pointers
        contacts_name_padded = contacts.name.ljust(name_long_size)
        mesh_from_name_padded = contacts.mesh_from_name.ljust(name_long_size)
        mesh_to_name_padded = contacts.mesh_to_name.ljust(name_long_size)

        contact_name_id_padded = pad_and_join_list_of_strings(
            contacts.contact_name_id, name_size
        )
        contact_name_long_padded = pad_and_join_list_of_strings(
            contacts.contact_name_long, name_long_size
        )

        c_contacts.name = c_char_p(contacts_name_padded.encode("ASCII"))
        c_contacts.edges = numpy_array_to_ctypes(contacts.edges)
        c_contacts.contact_type = numpy_array_to_ctypes(contacts.contact_type)
        c_contacts.mesh_from_name = c_char_p(mesh_from_name_padded.encode("ASCII"))
        c_contacts.mesh_to_name = c_char_p(mesh_to_name_padded.encode("ASCII"))
        c_contacts.contact_name_id = c_char_p(contact_name_id_padded.encode("ASCII"))
        c_contacts.contact_name_long = c_char_p(
            contact_name_long_padded.encode("ASCII")
        )
        c_contacts.mesh_from_location = contacts.mesh_from_location
        c_contacts.mesh_to_location = contacts.mesh_to_location

        # Set the size
        c_contacts.num_contacts = contacts.edges.size // 2

        return c_contacts

    def allocate_memory(self, name_size: int, name_long_size: int) -> UGridContacts:
        """Allocate data according to the parameters with the "num_" prefix.
        The pointers are then set to the freshly allocated memory.
        The memory is owned by the Contacts instance which is returned by this method.

        Args:
            name_long_size (int): The size of the long names.

        Returns:
            UGridContacts: The object owning the allocated memory.
        """

        name = " " * name_long_size
        mesh_from_name = " " * name_long_size
        mesh_to_name = " " * name_long_size
        edges = np.empty(self.num_contacts * 2, dtype=np.int)
        contact_type = np.empty(self.num_contacts, dtype=np.int)
        contact_name_id = " " * self.num_contacts * name_size
        contact_name_long = " " * self.num_contacts * name_long_size

        self.name = c_char_p(name.encode("ASCII"))
        self.edges = numpy_array_to_ctypes(edges)
        self.contact_type = numpy_array_to_ctypes(contact_type)
        self.contact_name_id = c_char_p(contact_name_id.encode("ASCII"))
        self.contact_name_long = c_char_p(contact_name_long.encode("ASCII"))
        self.mesh_from_name = c_char_p(mesh_from_name.encode("ASCII"))
        self.mesh_to_name = c_char_p(mesh_to_name.encode("ASCII"))

        return UGridContacts(
            name=name,
            edges=edges,
            mesh_from_name=mesh_from_name,
            mesh_to_name=mesh_to_name,
            contact_type=contact_type,
            contact_name_id=contact_name_id,
            contact_name_long=contact_name_long,
        )
