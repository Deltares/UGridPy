from __future__ import annotations

from ctypes import POINTER, Structure, c_double, c_int, c_char_p

import numpy as np
from numpy.ctypeslib import as_ctypes

from ugrid.py_structures import Network1D, Mesh1D, Mesh2D, Contacts


def decode_byte_vector_to_string(byte_vector: bytes, ncolumns: int) -> str:
    return byte_vector[:ncolumns].decode("UTF-8").strip()


def decode_byte_vector_to_list_of_strings(
        byte_vector: bytes, nrows: int, str_size: int
) -> list:
    return [
        byte_vector[str_size * r: str_size * (r + 1)].decode("UTF-8").strip()
        for r in range(nrows)
    ]


def pad_and_join_list_of_strings(string_list: list, str_size: int):
    for i in range(len(string_list)):
        string_list[i] = string_list[i].ljust(str_size)
    result = "".join(string_list)
    return result


def numpy_array_to_ctypes(arr):
    if len(arr) == 0:
        return None
    return as_ctypes(arr)


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
    def from_py_structure(
            network1D: Network1D, name_size: int, name_long_size: int
    ) -> CNetwork1D:
        """Creates a new CMesh instance from a given Mesh2d instance.

        Args:
            network1D (Network1D): Class of numpy instances owning the state.

        Returns:
            CMesh2d: The created CMesh2d instance.
        """

        name_padded = network1D.name.ljust(name_size)

        node_name_id = pad_and_join_list_of_strings(network1D.node_name_id, name_size)
        node_name_long = pad_and_join_list_of_strings(
            network1D.node_name_long, name_long_size
        )

        branch_name_id = pad_and_join_list_of_strings(
            network1D.branch_name_id, name_size
        )
        branch_name_long = pad_and_join_list_of_strings(
            network1D.branch_name_long, name_long_size
        )

        c_network1d = CNetwork1D()

        # Set the pointers
        c_network1d.name = c_char_p(name_padded.encode("utf-8"))
        c_network1d.node_x = numpy_array_to_ctypes(network1D.node_x)
        c_network1d.node_y = numpy_array_to_ctypes(network1D.node_y)
        c_network1d.node_name_id = c_char_p(node_name_id.encode("utf-8"))
        c_network1d.node_name_long = c_char_p(node_name_long.encode("utf-8"))
        c_network1d.branch_node = numpy_array_to_ctypes(network1D.branch_node)
        c_network1d.branch_length = numpy_array_to_ctypes(network1D.branch_length)
        c_network1d.branch_order = numpy_array_to_ctypes(network1D.branch_order)
        c_network1d.branch_name_id = c_char_p(branch_name_id.encode("utf-8"))
        c_network1d.branch_name_long = c_char_p(branch_name_long.encode("utf-8"))
        c_network1d.geometry_nodes_x = numpy_array_to_ctypes(network1D.geometry_nodes_x)
        c_network1d.geometry_nodes_y = numpy_array_to_ctypes(network1D.geometry_nodes_y)

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
        The memory is owned by the Network1D instance which is returned by this method.

        Returns:
            Network1D: The object owning the allocated memory.
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

        self.name = c_char_p(name.encode("utf-8"))
        self.node_x = numpy_array_to_ctypes(node_x)
        self.node_y = numpy_array_to_ctypes(node_y)
        self.node_name_id = c_char_p(node_name_id.encode("utf-8"))
        self.node_name_long = c_char_p(node_name_long.encode("utf-8"))
        self.branch_node = numpy_array_to_ctypes(branch_node)
        self.branch_length = numpy_array_to_ctypes(branch_length)
        self.branch_order = numpy_array_to_ctypes(branch_order)
        self.branch_name_id = c_char_p(branch_name_id.encode("utf-8"))
        self.branch_name_long = c_char_p(branch_name_long.encode("utf-8"))
        self.geometry_nodes_x = numpy_array_to_ctypes(geometry_nodes_x)
        self.geometry_nodes_y = numpy_array_to_ctypes(geometry_nodes_y)

        return Network1D(
            name=name,
            node_x=node_x,
            node_y=node_y,
            branch_node=branch_node,
            branch_length=branch_length,
            branch_order=branch_order,
            geometry_nodes_x=geometry_nodes_x,
            geometry_nodes_y=geometry_nodes_y,
        )


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
    def from_py_structure(
            mesh1d: Mesh1D, name_size: int, name_long_size: int
    ) -> CNetwork1D:
        """Creates a new CMesh instance from a given Mesh2d instance.

        Args:
            mesh1d (Mesh1D): Class of numpy instances owning the state.

        Returns:
            CMesh2d: The created CMesh2d instance.
        """

        c_mesh1d = CMesh1D()

        # Set the pointers
        mesh1d_name_padded = mesh1d.name.ljust(name_size)
        network1d_name_padded = mesh1d.network_name.ljust(name_size)
        node_name_id = pad_and_join_list_of_strings(mesh1d.node_name_id, name_size)
        node_name_long = pad_and_join_list_of_strings(
            mesh1d.node_name_long, name_long_size
        )

        c_mesh1d.name = c_char_p(mesh1d_name_padded.encode("utf-8"))
        c_mesh1d.network_name = c_char_p(network1d_name_padded.encode("utf-8"))
        c_mesh1d.node_x = numpy_array_to_ctypes(mesh1d.node_x)
        c_mesh1d.node_y = numpy_array_to_ctypes(mesh1d.node_y)
        c_mesh1d.edge_node = numpy_array_to_ctypes(mesh1d.edge_node)
        c_mesh1d.branch_id = numpy_array_to_ctypes(mesh1d.branch_id)
        c_mesh1d.branch_offset = numpy_array_to_ctypes(mesh1d.branch_offset)
        c_mesh1d.node_name_id = c_char_p(node_name_id.encode("utf-8"))
        c_mesh1d.node_name_long = c_char_p(node_name_long.encode("utf-8"))
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

    def allocate_memory(self, name_size: int, name_long_size: int) -> Mesh1D:
        """Allocate data according to the parameters with the "num_" prefix.
        The pointers are then set to the freshly allocated memory.
        The memory is owned by the Mesh1d instance which is returned by this method.

        Returns:
            Mesh1D: The object owning the allocated memory.
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

        self.name = c_char_p(name.encode("utf-8"))
        self.network_name = c_char_p(network_name.encode("utf-8"))
        self.node_x = numpy_array_to_ctypes(node_x)
        self.node_y = numpy_array_to_ctypes(node_y)
        self.edge_node = numpy_array_to_ctypes(edge_node)
        self.branch_id = numpy_array_to_ctypes(branch_id)
        self.branch_offset = numpy_array_to_ctypes(branch_offset)
        self.node_name_id = c_char_p(node_name_id.encode("utf-8"))
        self.node_name_long = c_char_p(node_name_long.encode("utf-8"))
        self.edge_edge_id = numpy_array_to_ctypes(edge_edge_id)
        self.edge_edge_offset = numpy_array_to_ctypes(edge_edge_offset)
        self.edge_x = numpy_array_to_ctypes(edge_x)
        self.edge_y = numpy_array_to_ctypes(edge_y)

        return Mesh1D(
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


class CMesh2D(Structure):
    """C-structure intended for internal use only.
    It represents a Mesh2D struct as described by the UGrid API.

    Used for communicating with the UGrid dll.

    Attributes:
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
    def from_py_structure(mesh2d: Mesh2D, name_size: int) -> CMesh2D:
        """Creates a new CMesh instance from a given Mesh2d instance.

        Args:
            mesh2d (Mesh2D): Class of numpy instances owning the state.

        Returns:
            CMesh2d: The created CMesh2d instance.
        """

        c_mesh2d = CMesh2D()

        # Required arrays
        mesh2d_name_padded = mesh2d.name.ljust(name_size)
        c_mesh2d.name = c_char_p(mesh2d_name_padded.encode("utf-8"))
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
        c_mesh2d.num_faces = mesh2d.num_faces
        c_mesh2d.num_layers = mesh2d.num_layers

        # Set other properties
        c_mesh2d.start_index = mesh2d.start_index
        c_mesh2d.num_face_nodes_max = mesh2d.num_face_nodes_max
        c_mesh2d.is_spherical = mesh2d.is_spherical
        c_mesh2d.double_fill_value = mesh2d.double_fill_value
        c_mesh2d.int_fill_value = mesh2d.int_fill_value

        return c_mesh2d

    def allocate_memory(self, name_size: int) -> Mesh2D:
        """Allocate data according to the parameters with the "num_" prefix.
        The pointers are then set to the freshly allocated memory.
        The memory is owned by the Mesh2D instance which is returned by this method.

        Returns:
            Mesh2D: The object owning the allocated memory.
        """

        name = " " * name_size
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

        self.name = c_char_p(name.encode("utf-8"))
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
        self.boundary_node_connectivity = numpy_array_to_ctypes(boundary_node_connectivity)
        self.volume_coordinates = numpy_array_to_ctypes(volume_coordinates)

        if self.num_layers > 1:
            interface_zs = np.empty(self.num_layers - 1, dtype=np.double)
            self.interface_zs = numpy_array_to_ctypes(interface_zs)
        else:
            interface_zs = None
            self.interface_zs = None

        return Mesh2D(
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


class CContacts(Structure):
    """C-structure intended for internal use only.
    It represents a Contacts struct as described by the UGrid API.

    Used for communicating with the UGrid dll.

    Attributes:
    """

    _fields_ = [
        ("name", c_char_p),
        ("contacts", POINTER(c_int)),
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
            contacts: Contacts, name_size: int, name_long_size: int
    ) -> CContacts:
        """Creates a new CContacts instance from a given Contacts instance.

        Args:
            contacts (Contacts): Class of numpy instances owning the state.

        Returns:
            CContacts: The created CContacts instance.
        """

        c_contacts = CContacts()

        # Set the pointers
        contacts_name_padded = contacts.name.ljust(name_size)
        mesh_from_name_padded = contacts.mesh_from_name.ljust(name_size)
        mesh_to_name_padded = contacts.mesh_to_name.ljust(name_size)

        contact_name_id = pad_and_join_list_of_strings(contacts.contact_name_id, name_size)
        contact_name_long = pad_and_join_list_of_strings(contacts.contact_name_long, name_long_size)

        c_contacts.name = c_char_p(contacts_name_padded.encode("utf-8"))
        c_contacts.contacts = numpy_array_to_ctypes(contacts.contacts)
        c_contacts.contact_type = numpy_array_to_ctypes(contacts.contact_type)
        c_contacts.mesh_from_name = c_char_p(mesh_from_name_padded.encode("utf-8"))
        c_contacts.mesh_to_name = c_char_p(mesh_to_name_padded.encode("utf-8"))
        c_contacts.contact_name_id = c_char_p(contact_name_id.encode("utf-8"))
        c_contacts.contact_name_long = c_char_p(contact_name_long.encode("utf-8"))
        c_contacts.mesh_from_location = contacts.mesh_from_location
        c_contacts.mesh_to_location = contacts.mesh_to_location

        # Set the size
        c_contacts.num_contacts = contacts.num_contacts

        return c_contacts

    def allocate_memory(self, name_size: int, name_long_size: int) -> Contacts:
        """Allocate data according to the parameters with the "num_" prefix.
        The pointers are then set to the freshly allocated memory.
        The memory is owned by the Contacts instance which is returned by this method.

        Returns:
            Contacts: The object owning the allocated memory.
        """

        name = " " * name_size
        contacts = np.empty(self.num_contacts * 2, dtype=np.int)
        mesh_from_name = " " * name_size
        mesh_to_name = " " * name_size
        contact_type = np.empty(self.num_contacts, dtype=np.int)
        contact_name_id = " " * self.num_contacts * name_size
        contact_name_long = " " * self.num_contacts * name_long_size

        self.name = c_char_p(name.encode("utf-8"))
        self.contacts = numpy_array_to_ctypes(contacts)
        self.contact_type = numpy_array_to_ctypes(contact_type)
        self.contact_name_id = c_char_p(contact_name_id.encode("utf-8"))
        self.contact_name_long = c_char_p(contact_name_long.encode("utf-8"))
        self.mesh_from_name = c_char_p(mesh_from_name.encode("utf-8"))
        self.mesh_to_name = c_char_p(mesh_to_name.encode("utf-8"))

        return Contacts(name=name,
                        contacts=contacts,
                        mesh_from_name=mesh_from_name,
                        mesh_to_name=mesh_to_name,
                        contact_type=contact_type,
                        contact_name_id=contact_name_id,
                        contact_name_long=contact_name_long)
