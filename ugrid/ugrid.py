import functools
import logging
import operator
import platform
from ctypes import CDLL, byref, c_char_p, c_int
from enum import IntEnum, unique
from pathlib import Path
from typing import Callable

import numpy as np
from meshkernel import Contacts, Mesh1d, Mesh2d
from numpy.ctypeslib import as_ctypes

from ugrid.c_structures import (
    CUGridContacts,
    CUGridMesh1D,
    CUGridMesh2D,
    CUGridNetwork1D,
    decode_byte_vector_to_list_of_strings,
    decode_byte_vector_to_string,
    numpy_array_to_ctypes,
)
from ugrid.errors import UGridError
from ugrid.py_structures import UGridContacts, UGridMesh1D, UGridMesh2D, UGridNetwork1D
from ugrid.version import __version__

logger = logging.getLogger(__name__)


@unique
class Status(IntEnum):
    SUCCESS = 0
    EXCEPTION = 1


class UGrid:
    """This class is the entry point for interacting with the UGridPy library"""

    def __init__(self, file_path, method):
        """Constructor of UGrid

        Raises:
            OSError: This gets raised in case UGrid is used within an unsupported OS.
        """

        # Determine OS
        system = platform.system()
        if system == "Windows":
            lib_path = Path(__file__).parent / "UGridApi.dll"
        elif system == "Linux":
            lib_path = Path(__file__).parent / "UGridApi.so"
        elif system == "Darwin":
            lib_path = Path(__file__).parent / "UGridApi.dylib"
        else:
            raise OSError(f"Unsupported operating system: {system}")

        self.lib = CDLL(str(lib_path))
        self.__open(file_path, method)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.__execute_function(self.lib.ug_file_close, self._file_id)
        error_message = self.__get_error()

        # Raise an exception if an error is present
        if error_message:
            raise UGridError(error_message)

    def __open(self, file_path: str, method: str) -> None:
        """Opens a NetCDF file containing a UGrid entities

        Comment

        Args:
            file_path (bool): The path of the file to open
            method (bool): The opening method ("r" for read, "w" for write, and "w+" for replace)
        """

        file_mode = c_int(0)
        if method == "r":
            self.__execute_function(self.lib.ug_file_read_mode, byref(file_mode))
        elif method == "w":
            self.__execute_function(self.lib.ug_file_write_mode, byref(file_mode))
        elif method == "w+":
            self.__execute_function(self.lib.ug_file_replace_mode, byref(file_mode))
        else:
            raise ValueError("Unsupported file mode")

        self._file_id = c_int(-1)

        file_path_bytes = bytes(file_path, encoding="utf8")
        self.__execute_function(
            self.lib.ug_file_open,
            file_path_bytes,
            file_mode,
            byref(self._file_id),
        )

    def __get_name_size(self):
        """Get the size of name strings"""
        name_size = c_int(0)
        self.__execute_function(self.lib.ug_name_get_length, byref(name_size))
        return name_size.value

    def __get_name_long_size(self):
        """Get the size of long name strings"""
        name_long_size = c_int(0)
        self.__execute_function(self.lib.ug_name_get_long_length, byref(name_long_size))
        return name_long_size.value

    def network1d_get_num_topologies(self) -> int:
        """Gets the number of network topologies contained in the file.

        Returns:
            int: The number of network topologies contained in the file.
        """

        topology_enum = self.topology_get_network1d_enum()

        topology_count = c_int(0)
        self.__execute_function(
            self.lib.ug_topology_get_count,
            self._file_id,
            c_int(topology_enum),
            byref(topology_count),
        )
        return topology_count.value

    def __network1d_inquire(self, topology_id) -> CUGridNetwork1D:
        """For internal use only.

        Inquires the network1d dimensions and names.

        Args:
            topology_id (int): The index of the network topology to inquire.

        Returns:
            CUGridNetwork1D: The network1d dimensions.
        """

        c_ugrid_network1d = CUGridNetwork1D()
        self.__execute_function(
            self.lib.ug_network1d_inq,
            self._file_id,
            c_int(topology_id),
            byref(c_ugrid_network1d),
        )
        return c_ugrid_network1d

    def network1d_get(self, topology_id) -> UGridNetwork1D:
        """Gets the network1d data.

        Args:
            topology_id (int): The index of the network1d topology to retrieve.

        Returns:
            UGridNetwork1D: The network1d (dimensions and data)
        """

        c_ugrid_network1d = self.__network1d_inquire(topology_id)
        name_size = self.__get_name_size()
        name_long_size = self.__get_name_long_size()

        ugrid_network1d = c_ugrid_network1d.allocate_memory(name_size, name_long_size)
        self.__execute_function(
            self.lib.ug_network1d_get,
            self._file_id,
            c_int(topology_id),
            byref(c_ugrid_network1d),
        )

        ugrid_network1d.is_spherical = bool(c_ugrid_network1d.is_spherical)
        ugrid_network1d.start_index = c_ugrid_network1d.start_index
        ugrid_network1d.name = decode_byte_vector_to_string(
            c_ugrid_network1d.name, name_size
        )
        ugrid_network1d.node_id = decode_byte_vector_to_list_of_strings(
            c_ugrid_network1d.node_id, c_ugrid_network1d.num_nodes, name_size
        )
        ugrid_network1d.node_long_name = decode_byte_vector_to_list_of_strings(
            c_ugrid_network1d.node_long_name,
            c_ugrid_network1d.num_nodes,
            name_long_size,
        )

        ugrid_network1d.edge_id = decode_byte_vector_to_list_of_strings(
            c_ugrid_network1d.edge_id,
            c_ugrid_network1d.num_edges,
            name_size,
        )
        ugrid_network1d.edge_long_name = decode_byte_vector_to_list_of_strings(
            c_ugrid_network1d.edge_long_name,
            c_ugrid_network1d.num_edges,
            name_long_size,
        )

        return ugrid_network1d

    def network1d_define(self, network1d: UGridNetwork1D) -> int:
        """Defines a new network1d in a UGrid file.

        Args:
            network1d (UGridNetwork1D): A network1d (dimensions and data)

        Returns:
            int: The index of the defined network topology.
        """

        name_size = self.__get_name_size()
        name_long_size = self.__get_name_long_size()

        c_ugrid_network = CUGridNetwork1D.from_py_structure(
            network1d, name_size, name_long_size
        )

        c_topology_id = c_int(-1)

        self.__execute_function(
            self.lib.ug_network1d_def,
            self._file_id,
            byref(c_ugrid_network),
            byref(c_topology_id),
        )

        return c_topology_id.value

    def network1d_put(self, topology_id: int, network1d: UGridNetwork1D) -> None:
        """Writes a new network1d to UGrid file.

        Args:
            topology_id (int): The index of the network1d topology to write.
            network1d (UGridNetwork1D): An instance of Network1D (with dimensions and data)
        """

        name_size = self.__get_name_size()
        name_long_size = self.__get_name_long_size()

        c_ugrid_network = CUGridNetwork1D.from_py_structure(
            network1d, name_size, name_long_size
        )

        self.__execute_function(
            self.lib.ug_network1d_put,
            self._file_id,
            c_int(topology_id),
            byref(c_ugrid_network),
        )

    def mesh1d_get_num_topologies(self) -> int:
        """Gets the number of mesh1d topologies contained in the file.

        Returns:
            int: The number of mesh1d topologies contained in the file.
        """

        topology_enum = self.topology_get_mesh1d_enum()

        topology_count = c_int(0)
        self.__execute_function(
            self.lib.ug_topology_get_count,
            self._file_id,
            c_int(topology_enum),
            byref(topology_count),
        )
        return topology_count.value

    def __mesh1d_inquire(self, topology_id) -> CUGridMesh1D:
        """For internal use only.

        Inquires the mesh1d dimensions and names.

        Args:
            topology_id (int): The index of the mesh1d topology to inquire.

        Returns:
            CUGridMesh1D: The mesh1d dimensions.

        """

        c_ugrid_mesh1d = CUGridMesh1D()
        self.__execute_function(
            self.lib.ug_mesh1d_inq,
            self._file_id,
            c_int(topology_id),
            byref(c_ugrid_mesh1d),
        )
        return c_ugrid_mesh1d

    def mesh1d_get(self, topology_id) -> UGridMesh1D:
        """Gets the mesh1d data.

        Args:
            topology_id (int): The index of the mesh1d topology to retrieve.

        Returns:
            UGridMesh1D: The mesh1d (dimensions and data)
        """

        c_mesh1d = self.__mesh1d_inquire(topology_id)
        name_size = self.__get_name_size()
        name_long_size = self.__get_name_long_size()

        ugrid_mesh1d = c_mesh1d.allocate_memory(name_size, name_long_size)

        self.__execute_function(
            self.lib.ug_mesh1d_get,
            self._file_id,
            c_int(topology_id),
            byref(c_mesh1d),
        )

        ugrid_mesh1d.is_spherical = bool(c_mesh1d.is_spherical)
        ugrid_mesh1d.start_index = c_mesh1d.start_index
        ugrid_mesh1d.double_fill_value = c_mesh1d.double_fill_value
        ugrid_mesh1d.int_fill_value = c_mesh1d.int_fill_value

        ugrid_mesh1d.name = decode_byte_vector_to_string(c_mesh1d.name, name_size)
        ugrid_mesh1d.network_name = decode_byte_vector_to_string(
            c_mesh1d.network_name, name_size
        )

        ugrid_mesh1d.node_name_id = decode_byte_vector_to_list_of_strings(
            c_mesh1d.node_name_id, c_mesh1d.num_nodes, name_size
        )
        ugrid_mesh1d.node_name_long = decode_byte_vector_to_list_of_strings(
            c_mesh1d.node_name_long, c_mesh1d.num_nodes, name_long_size
        )

        return ugrid_mesh1d

    def mesh1d_define(self, mesh1d: UGridMesh1D) -> int:
        """Defines a new mesh1d in a UGrid file.

        Args:
            mesh1d (UGridMesh1D): A mesh1d (dimensions and data)

        Returns:
            int: The index of the defined mesh1d topology.
        """

        name_size = self.__get_name_size()
        name_long_size = self.__get_name_long_size()

        c_ugrid_mesh1d = CUGridMesh1D.from_py_structure(
            mesh1d, name_size, name_long_size
        )

        c_topology_id = c_int(-1)

        self.__execute_function(
            self.lib.ug_mesh1d_def,
            self._file_id,
            byref(c_ugrid_mesh1d),
            byref(c_topology_id),
        )

        return c_topology_id.value

    def mesh1d_put(self, topology_id: int, mesh1d: UGridMesh1D) -> None:
        """Writes a new mesh1d to UGrid file.

        Args:
            topology_id (int): The index of the mesh1d topology to write.
            mesh1d (UGridMesh1D): An instance of mesh1d (with dimensions and data)
        """

        name_size = self.__get_name_size()
        name_long_size = self.__get_name_long_size()

        c_ugrid_mesh1d = CUGridMesh1D.from_py_structure(
            mesh1d, name_size, name_long_size
        )

        self.__execute_function(
            self.lib.ug_mesh1d_put,
            self._file_id,
            c_int(topology_id),
            byref(c_ugrid_mesh1d),
        )

    def mesh2d_get_num_topologies(self) -> int:
        """Description

        Gets the number of mesh2d topologies contained in the file.

        Returns:
            int: The number of mesh2d topologies contained in the file.

        """

        topology_enum = self.topology_get_mesh2d_enum()

        topology_count = c_int(0)
        self.__execute_function(
            self.lib.ug_topology_get_count,
            self._file_id,
            c_int(topology_enum),
            byref(topology_count),
        )
        return topology_count.value

    def __mesh2d_inquire(self, topology_id) -> CUGridMesh2D:
        """For internal use only.

        Inquires the mesh2d dimensions and names.

        Args:
            topology_id (int): The index of the mesh2d topology to inquire.

        Returns:
            CUGridMesh2D: The mesh2d dimensions.

        """

        c_ugrid_mesh2d = CUGridMesh2D()
        self.__execute_function(
            self.lib.ug_mesh2d_inq,
            self._file_id,
            c_int(topology_id),
            byref(c_ugrid_mesh2d),
        )
        return c_ugrid_mesh2d

    def mesh2d_get(self, topology_id) -> UGridMesh2D:
        """Gets the mesh2d data.

        Args:
            topology_id (int): The index of the mesh2d topology to retrieve.

        Returns:
            UGridMesh2D: The mesh2d (dimensions and data)
        """

        c_ugrid_mesh2d = self.__mesh2d_inquire(topology_id)
        long_name_size = self.__get_name_long_size()

        ugrid_mesh2d = c_ugrid_mesh2d.allocate_memory(long_name_size)
        self.__execute_function(
            self.lib.ug_mesh2d_get,
            self._file_id,
            c_int(topology_id),
            byref(c_ugrid_mesh2d),
        )

        ugrid_mesh2d.is_spherical = bool(c_ugrid_mesh2d.is_spherical)
        ugrid_mesh2d.start_index = c_ugrid_mesh2d.start_index
        ugrid_mesh2d.double_fill_value = c_ugrid_mesh2d.double_fill_value
        ugrid_mesh2d.int_fill_value = c_ugrid_mesh2d.int_fill_value

        ugrid_mesh2d.name = decode_byte_vector_to_string(
            c_ugrid_mesh2d.name, long_name_size
        )

        return ugrid_mesh2d

    def mesh2d_define(self, ugrid_mesh2d: UGridMesh2D) -> int:
        """Defines a new mesh2d in a UGrid file.

        Args:
            ugrid_mesh2d (UGridMesh2D): A mesh2d (dimensions and data)

        Returns:
            int: The index of the defined mesh2d topology.
        """

        long_name_size = self.__get_name_long_size()

        c_ugrid_mesh2d = CUGridMesh2D.from_py_structure(ugrid_mesh2d, long_name_size)

        c_topology_id = c_int(-1)

        self.__execute_function(
            self.lib.ug_mesh2d_def,
            self._file_id,
            byref(c_ugrid_mesh2d),
            byref(c_topology_id),
        )

        return c_topology_id.value

    def mesh2d_put(self, topology_id: int, ugrid_mesh2d: UGridMesh2D) -> None:
        """Writes a new mesh2d in a UGrid file.

        Args:
            topology_id (int): The index of the mesh2d topology to write.
            ugrid_mesh2d (UGridMesh2D): A mesh2d (dimensions and data)
        """

        name_size = self.__get_name_size()
        c_ugrid_mesh2d = CUGridMesh2D.from_py_structure(ugrid_mesh2d, name_size)

        self.__execute_function(
            self.lib.ug_mesh2d_put,
            self._file_id,
            c_int(topology_id),
            byref(c_ugrid_mesh2d),
        )

    @staticmethod
    def from_meshkernel_mesh2d_to_ugrid_mesh2d(
        mesh2d: Mesh2d, name: str, is_spherical: bool
    ) -> UGridMesh2D:
        """Converts a meshkernel mesh2d to ugrid mesh2d

        Args:
            mesh2d (Mesh2d): An instance of a meshkernel mesh2d
            name (str): The name of mesh2d
            is_spherical (bool): Spherical or cartesian coordinate system
        """

        num_faces = len(mesh2d.nodes_per_face)
        if num_faces > 0:
            num_face_nodes_max = np.max(mesh2d.nodes_per_face)
            face_nodes_array = np.full(
                num_faces * num_face_nodes_max, dtype=np.int, fill_value=-1
            )
            for index, (face_nodes, nodes_per_face) in enumerate(
                zip(mesh2d.face_nodes, mesh2d.nodes_per_face)
            ):
                face_nodes_array[
                    index * num_face_nodes_max : index * num_face_nodes_max
                    + nodes_per_face
                ] = face_nodes

            return UGridMesh2D(
                name=name,
                node_x=mesh2d.node_x,
                node_y=mesh2d.node_y,
                edge_node=mesh2d.edge_nodes,
                face_node=face_nodes_array,
                edge_x=mesh2d.edge_x,
                edge_y=mesh2d.edge_y,
                face_x=mesh2d.face_x,
                face_y=mesh2d.face_y,
                num_face_nodes_max=num_face_nodes_max,
                is_spherical=is_spherical,
                double_fill_value=-999.0,
                int_fill_value=-999,
            )

        return UGridMesh2D(
            name=name,
            node_x=mesh2d.node_x,
            node_y=mesh2d.node_y,
            edge_node=mesh2d.edge_nodes,
        )

    @staticmethod
    def from_meshkernel_mesh1d_to_ugrid_mesh1d(
        mesh1d: Mesh1d,
        name: str,
        network_name: str,
        node_edge_id: np.ndarray,
        node_edge_offset: np.ndarray,
        node_name_id: list,
        node_name_long: list,
        edge_edge_id: np.ndarray,
        edge_edge_offset: np.ndarray,
        edge_x: np.ndarray,
        edge_y: np.ndarray,
        double_fill_value: float,
        int_fill_value: int,
    ) -> UGridMesh1D:
        """Converts a meshkernel mesh1d to a ugrid mesh1d

        Args:
            mesh1d (Mesh1d): An instance of a meshkernel mesh1d
            network_name (c_char_p): The x-coordinates of the network node.
            node_x (ndarray):  The node x coordinate.
            node_y (ndarray):  The node y coordinate.
            node_edge_id (ndarray):  The network edge id where every node lies.
            node_edge_offset (ndarray): The offset of each node on the network edge
            node_name_id (list): A list of node names ids.
            node_name_long (c_char_p): A list of node long names.
            edge_edge_id (ndarray): The network edge id where every edge lies.
            edge_edge_offset (ndarray): The offset of each edge on the network edge.
            edge_x (ndarray): The edge x coordinate.
            edge_y (ndarray): The edge y coordinate.
            double_fill_value (c_double): The fill value for array of doubles.
            int_fill_value (c_int): The fill value for array of integers.
        """

        ugrid_mesh1d = UGridMesh1D(
            name=name,
            network_name=network_name,
            node_x=mesh1d.node_x,
            node_y=mesh1d.node_y,
            edge_node=mesh1d.edge_nodes,
            node_edge_id=node_edge_id,
            node_edge_offset=node_edge_offset,
            node_name_id=node_name_id,
            node_name_long=node_name_long,
            edge_edge_id=edge_edge_id,
            edge_edge_offset=edge_edge_offset,
            edge_x=edge_x,
            edge_y=edge_y,
            double_fill_value=double_fill_value,
            int_fill_value=int_fill_value,
        )

        return ugrid_mesh1d

    @staticmethod
    def from_meshkernel_contacts_to_ugrid_contacts(
        contacts: Contacts,
        name: str,
        contact_type: np.ndarray,
        contact_name_id: str,
        contact_name_long: str,
        mesh_from_name: str,
        mesh_to_name: str,
        mesh_from_location: int,
        mesh_to_location: int,
    ) -> UGridContacts:
        """Converts a meshkernel mesh1d to a ugrid mesh1d

        Args:
            contacts (Contacts): An instance of a meshkernel contacts entity
            name (str): The name of the contact entity.
            contact_type (ndarray): For each contact its type.
            contact_name_id (list): The name of each contact.
            contact_name_long (list): The long name of each contact.
            mesh_from_name (str): The name of the mesh where the contacts start.
            mesh_to_name (str): The name of the mesh where the contacts ends.
            mesh_from_location (c_int): The location type (node, edge or face) at the contact start.
            mesh_to_location (c_int): The location type (node, edge or face) at the contact end.
        """

        num_edges = len(contacts.mesh1d_indices)
        edges_array = np.full(num_edges * 2, dtype=np.int, fill_value=-1)
        for index, (mesh1d_indices, mesh2d_indices) in enumerate(
            zip(contacts.mesh1d_indices, contacts.mesh2d_indices)
        ):
            edges_array[index * 2] = mesh1d_indices
            edges_array[index * 2 + 1] = mesh2d_indices

        ugrid_contacts = UGridContacts(
            name=name,
            edges=edges_array,
            mesh_from_name=mesh_from_name,
            mesh_to_name=mesh_to_name,
            contact_type=contact_type,
            contact_name_id=contact_name_id,
            contact_name_long=contact_name_long,
            mesh_from_location=mesh_from_location,
            mesh_to_location=mesh_to_location,
        )

        return ugrid_contacts

    def contacts_get_num_topologies(self) -> int:
        """Description

        Gets the number of contacts topologies contained in the file.

        Returns:
            int: The number of contacts topologies contained in the file.

        """

        topology_enum = self.topology_get_contacts_enum()

        topology_count = c_int(0)
        self.__execute_function(
            self.lib.ug_topology_get_count,
            self._file_id,
            c_int(topology_enum),
            byref(topology_count),
        )
        return topology_count.value

    def __contacts_inquire(self, topology_id) -> CUGridContacts:
        """For internal use only.

        Inquires the contacts dimensions and names.

        Args:
            topology_id (int): The index of the contacts topology to inquire.

        Returns:
            CUGridContacts: The contacts dimensions.

        """

        c_ugrid_contacts = CUGridContacts()
        self.__execute_function(
            self.lib.ug_contacts_inq,
            self._file_id,
            c_int(topology_id),
            byref(c_ugrid_contacts),
        )
        return c_ugrid_contacts

    def contacts_get(self, topology_id) -> UGridContacts:
        """Gets the contacts data.

        Args:
            topology_id (int): The index of the contacts topology to retrieve.

        Returns:
            UGridContacts: The contacts (dimensions and data)
        """

        c_ugrid_contacts = self.__contacts_inquire(topology_id)
        name_size = self.__get_name_size()
        name_long_size = self.__get_name_long_size()

        ugrid_contacts = c_ugrid_contacts.allocate_memory(name_size, name_long_size)
        self.__execute_function(
            self.lib.ug_contacts_get,
            self._file_id,
            c_int(topology_id),
            byref(c_ugrid_contacts),
        )

        ugrid_contacts.name = decode_byte_vector_to_string(
            c_ugrid_contacts.name, name_size
        )
        ugrid_contacts.contact_name_id = decode_byte_vector_to_list_of_strings(
            c_ugrid_contacts.contact_name_id,
            c_ugrid_contacts.num_contacts,
            name_size,
        )
        ugrid_contacts.contact_name_long = decode_byte_vector_to_list_of_strings(
            c_ugrid_contacts.contact_name_long,
            c_ugrid_contacts.num_contacts,
            name_long_size,
        )

        ugrid_contacts.mesh_from_name = decode_byte_vector_to_string(
            c_ugrid_contacts.mesh_from_name, name_size
        )
        ugrid_contacts.mesh_to_name = decode_byte_vector_to_string(
            c_ugrid_contacts.mesh_to_name, name_size
        )

        return ugrid_contacts

    def contacts_define(self, contacts: UGridContacts) -> int:
        """Defines a new contacts in a UGrid file.

        Args:
            contacts (UGridContacts): An instance of Contacts class (dimensions and data)

        Returns:
            int: The index of the defined contacts topology.
        """

        name_size = self.__get_name_size()
        name_long_size = self.__get_name_long_size()

        c_ugrid_contacts = CUGridContacts.from_py_structure(
            contacts, name_size, name_long_size
        )

        c_topology_id = c_int(-1)

        self.__execute_function(
            self.lib.ug_contacts_def,
            self._file_id,
            byref(c_ugrid_contacts),
            byref(c_topology_id),
        )

        return c_topology_id.value

    def contacts_put(self, topology_id: int, contacts: UGridContacts) -> None:
        """Writes a new contacts in a UGrid file.

        Args:
            topology_id (int): The index of the contacts topology to write.
            contacts (UGridContacts): A contacts (dimensions and data)
        """
        name_size = self.__get_name_size()
        name_long_size = self.__get_name_long_size()

        c_ugrid_contacts = CUGridContacts.from_py_structure(
            contacts, name_size, name_long_size
        )

        self.__execute_function(
            self.lib.ug_contacts_put,
            self._file_id,
            c_int(topology_id),
            byref(c_ugrid_contacts),
        )

    def __get_error(self) -> str:
        c_error_message = c_char_p()
        self.__execute_function(self.lib.ug_error_get, byref(c_error_message))
        return c_error_message.value.decode("ASCII")

    def get_ugrid_version(self) -> str:
        """Get the version of the C++ UGrid library

        Returns:
            str: The version string
        """

        c_ugrid_version = c_char_p()
        self.__execute_function(self.lib.mkernel_get_version, byref(c_ugrid_version))
        return c_ugrid_version.value.decode("ASCII")

    def get_ugridpy_version(self) -> str:
        """Get the version of this Python wrapper

        Returns:
            str: The version string
        """

        return __version__

    def __execute_function(self, function: Callable, *args):
        """Utility function to execute a C function of UGrid and checks its status.

        Args:
            function (Callable): The function which we want to call.
            args: Arguments which will be passed to `function`.

        Raises:
            UGridError: This exception gets raised,
             if the UGrid library reports an error.
        """
        if function(*args) != Status.SUCCESS:
            error_message = self.__get_error()
            raise UGridError(error_message)

    def entity_get_node_location_enum(self) -> int:
        """Get the node location enum value

        Returns:
            int: The node location enum value
        """

        location = c_int(0)
        self.__execute_function(
            self.lib.ug_entity_get_node_location_enum, byref(location)
        )
        return location.value

    def entity_get_edge_location_enum(self) -> int:
        """Get the edge location enum value

        Returns:
            int: The edge location enum value
        """

        location = c_int(0)
        self.__execute_function(
            self.lib.ug_entity_get_edge_location_enum, byref(location)
        )
        return location.value

    def entity_get_face_location_enum(self) -> int:
        """Get the face location enum value

        Returns:
            int: The face location enum value
        """

        location = c_int(0)
        self.__execute_function(
            self.lib.ug_entity_get_face_location_enum, byref(location)
        )
        return location.value

    def topology_get_network1d_enum(self) -> int:

        """Gets the topology enum value associated with network1d.

        Returns:
            int: the topology enum value associated with network1d.
        """
        topology_enum = c_int(0)
        self.__execute_function(
            self.lib.ug_topology_get_network1d_enum, byref(topology_enum)
        )

        return topology_enum.value

    def topology_get_mesh1d_enum(self) -> int:

        """Gets the topology enum value associated with mesh1d.

        Returns:
            int: the topology enum value associated with mesh1d.
        """
        topology_enum = c_int(0)
        self.__execute_function(
            self.lib.ug_topology_get_mesh1d_enum, byref(topology_enum)
        )

        return topology_enum.value

    def topology_get_mesh2d_enum(self) -> int:

        """Gets the topology enum value associated with mesh2d.

        Returns:
            int: the topology enum value associated with mesh2d.
        """
        topology_enum = c_int(0)
        self.__execute_function(
            self.lib.ug_topology_get_mesh2d_enum, byref(topology_enum)
        )

        return topology_enum.value

    def topology_get_contacts_enum(self) -> int:

        """Gets the topology enum value associated with contacts.

        Returns:
            int: the topology enum value associated with contacts.
        """
        topology_enum = c_int(0)
        self.__execute_function(
            self.lib.ug_topology_get_contacts_enum, byref(topology_enum)
        )

        return topology_enum.value

    def __topology_count_data_variables(
        self, topology_id: int, topology_type: int, location: int
    ) -> int:
        """Gets the number of data variables for a specific topology at a specific location

        Args:
            topology_id (int): The index of the topology type.
            topology_type (int): The list with the attributes values.
            location (int): The location type

        Returns:
            int: The number of data
        """

        data_variable_count = c_int(0)
        self.__execute_function(
            self.lib.ug_topology_count_data_variables,
            self._file_id,
            c_int(topology_type),
            c_int(topology_id),
            c_int(location),
            byref(data_variable_count),
        )

        return data_variable_count.value

    def topology_get_data_variables(
        self, topology_id: int, topology_type: int, location: int
    ) -> list:
        """Gets the data variables for a specific topology at a specific location

        Args:
            topology_id (int): The index of the topology type.
            topology_type (int): The list with the attributes values.
            location (int): The location type

        Returns:
            list: The list of data variables
        """

        num_data_variables = self.__topology_count_data_variables(
            topology_id, topology_type, location
        )
        name_long_size = self.__get_name_long_size()

        buffer_size = name_long_size * num_data_variables
        string_buffer = " " * buffer_size

        string_buffer_encoded = c_char_p(string_buffer.encode("ASCII"))
        self.__execute_function(
            self.lib.ug_topology_count_data_variables,
            self._file_id,
            c_int(topology_type),
            c_int(topology_id),
            c_int(location),
            string_buffer_encoded,
        )

        attribute_list = decode_byte_vector_to_list_of_strings(
            string_buffer_encoded.value, num_data_variables, name_long_size
        )

        return attribute_list.value

    def __adjust_name(self, name: str) -> str:
        long_name = self.__get_name_long_size()
        name_long = name.ljust(long_name)
        return name_long

    def __variable_count_attributes(self, variable_name: str) -> int:
        """Counts the number of variable attributes.

        Args:
            variable_name (str): The variable name.

        Returns:
            int: The number of attributes
        """

        attributes_count = c_int(0)
        variable_name_long = self.__adjust_name(variable_name)
        c_variable_name_encoded = c_char_p(variable_name_long.encode("ASCII"))
        self.__execute_function(
            self.lib.ug_variable_count_attributes,
            self._file_id,
            c_variable_name_encoded,
            byref(attributes_count),
        )
        return attributes_count.value

    def variable_get_attributes_names(self, variable_name: str) -> list:
        """Gets the variable attribute names.

        Args:
            variable_name (str): The variable name.

        Returns:
            list: A list containing the variable attribute names.
        """

        num_attributes = self.__variable_count_attributes(variable_name)

        name_long_size = self.__get_name_long_size()
        buffer_size = name_long_size * num_attributes
        attribute_buffer = " " * buffer_size
        attribute_buffer_encoded = c_char_p(attribute_buffer.encode("ASCII"))

        variable_name_long = self.__adjust_name(variable_name)
        c_variable_name_encoded = c_char_p(variable_name_long.encode("ASCII"))

        self.__execute_function(
            self.lib.ug_variable_get_attributes_names,
            self._file_id,
            c_variable_name_encoded,
            attribute_buffer_encoded,
        )

        attribute_list = decode_byte_vector_to_list_of_strings(
            attribute_buffer_encoded.value, num_attributes, name_long_size
        )

        return attribute_list

    def variable_get_attributes_values(self, variable_name: str) -> list:
        """Gets the variable attribute values.

        Args:
            variable_name (str): The variable name.

        Returns:
            list: A list containing the variable attribute values.
        """

        num_attributes = self.__variable_count_attributes(variable_name)
        name_long_size = self.__get_name_long_size()

        buffer_size = name_long_size * num_attributes
        string_buffer = " " * buffer_size
        string_buffer_encoded = c_char_p(string_buffer.encode("ASCII"))

        variable_name_long = self.__adjust_name(variable_name)
        c_variable_name_encoded = c_char_p(variable_name_long.encode("ASCII"))

        self.__execute_function(
            self.lib.ug_variable_get_attributes_values,
            self._file_id,
            c_variable_name_encoded,
            string_buffer_encoded,
        )

        attribute_list = decode_byte_vector_to_list_of_strings(
            string_buffer_encoded.value, num_attributes, name_long_size
        )

        return attribute_list

    def __variable_get_dimensions(self, variable_name) -> np.ndarray:
        """Gets the variable dimensions

        Args:
            data_variable_name (str): The data variable name.

        Returns:
            np.ndarray: An array with the dimension values
        """

        variable_name_long = self.__adjust_name(variable_name)
        c_variable_name_encoded = c_char_p(variable_name_long.encode("ASCII"))
        c_num_dimensions = c_int(0)
        self.__execute_function(
            self.lib.ug_variable_count_dimensions,
            self._file_id,
            c_variable_name_encoded,
            byref(c_num_dimensions),
        )

        dimension_vec = np.empty(c_num_dimensions.value, dtype=np.int)
        dimension_vec_ptr = as_ctypes(dimension_vec)
        self.__execute_function(
            self.lib.ug_variable_get_data_dimensions,
            self._file_id,
            c_variable_name_encoded,
            dimension_vec_ptr,
        )
        return dimension_vec

    def variable_get_data_double(self, variable_name: str) -> np.ndarray:
        """Gets the variable data as a flat array of double

        Args:
            variable_name (str): The variable name.

        Returns:
            np.ndarray: A numpy array with the variable data
        """

        dimension_vec = self.__variable_get_dimensions(variable_name)
        data_vec_dimension = functools.reduce(operator.mul, dimension_vec)

        data_vec = np.empty(data_vec_dimension, dtype=np.double)
        data_vec_ptr = as_ctypes(data_vec)
        variable_name_long = self.__adjust_name(variable_name)
        c_variable_name_encoded = c_char_p(variable_name_long.encode("ASCII"))
        self.__execute_function(
            self.lib.ug_variable_get_data_double,
            self._file_id,
            c_variable_name_encoded,
            data_vec_ptr,
        )

        return data_vec

    def variable_get_data_int(self, variable_name: str) -> np.ndarray:
        """Gets the variable data as a flat array of strings

        Args:
            variable_name (str): The variable name.

        Returns:
            np.ndarray: A numpy array with the variable data
        """

        dimension_vec = self.__variable_get_dimensions(variable_name)

        data_vec_dimension = functools.reduce(operator.mul, dimension_vec)

        data_vec = np.empty(data_vec_dimension, dtype=np.int)
        data_vec_ptr = as_ctypes(data_vec)
        variable_name_long = self.__adjust_name(variable_name)
        c_variable_name_encoded = c_char_p(variable_name_long.encode("ASCII"))
        self.__execute_function(
            self.lib.ug_variable_get_data_int,
            self._file_id,
            c_variable_name_encoded,
            data_vec_ptr,
        )

        return data_vec

    def __variable_int_define(self, variable_name: str):
        """Defines a new integer variable

        Args:
            variable_name (str): The variable name.
        """

        variable_name_long = self.__adjust_name(variable_name)
        c_variable_name_encoded = c_char_p(variable_name_long.encode("ASCII"))

        self.__execute_function(
            self.lib.ug_variable_int_define, self._file_id, c_variable_name_encoded
        )

    def __attribute_define(
        self, variable_name: str, attribute_name: str, attribute_values
    ):
        """Defines a new variable attribute with a name and an array of values.

        Args:
            variable_name (str): The variable name.
            attribute_name (str): The attribute name.
            attribute_values: The attribute values. Can be a numpy array of int, floats or a string
        """

        variable_name_long = self.__adjust_name(variable_name)
        c_variable_name_encoded = c_char_p(variable_name_long.encode("ASCII"))

        attribute_name_long = self.__adjust_name(attribute_name)
        c_attribute_name_encoded = c_char_p(attribute_name_long.encode("ASCII"))

        attribute_values_len = c_int(len(attribute_values))

        if isinstance(
            attribute_values, np.ndarray
        ) and attribute_values.dtype is np.dtype("int32"):
            funct = self.lib.ug_attribute_int_define
            c_attribute_values = numpy_array_to_ctypes(attribute_values)
        elif isinstance(
            attribute_values, np.ndarray
        ) and attribute_values.dtype is np.dtype("float"):
            funct = self.lib.ug_attribute_double_define
            c_attribute_values = numpy_array_to_ctypes(attribute_values)
        elif isinstance(attribute_values, str):
            funct = self.lib.ug_attribute_char_define
            c_attribute_values = c_char_p(attribute_values.encode("ASCII"))
        else:
            raise UGridError(
                "__attribute_define: attribute_values types are not supported"
            )

        self.__execute_function(
            funct,
            self._file_id,
            c_variable_name_encoded,
            c_attribute_name_encoded,
            c_attribute_values,
            attribute_values_len,
        )

    def variable_int_with_attributes_define(
        self, variable_name: str, variable_dict: dict
    ):
        """Defines a new variable with attributes. It can be used to write the coordinate reference system to file.

        Args:
            variable_name (str): The new variable name.
            variable_dict (dict): A dictionary containing the variable values and names
        """

        self.__variable_int_define(variable_name)
        for names, values in variable_dict.items():
            self.__attribute_define(variable_name, names, values)

    def attribute_global_define(self, variable_dict: dict):
        """Defines new global attributes

        Args:
            variable_dict (dict): A dictionary containing the attribute names and values.
        """
        for attribute_name, attribute_value in variable_dict.items():

            attribute_name_long = self.__adjust_name(attribute_name)
            c_attribute_name_encoded = c_char_p(attribute_name_long.encode("ASCII"))

            c_attribute_value_encoded = c_char_p(attribute_value.encode("ASCII"))
            attribute_values_len = c_int(len(attribute_value))

            self.__execute_function(
                self.lib.ug_attribute_global_char_define,
                self._file_id,
                c_attribute_name_encoded,
                c_attribute_value_encoded,
                attribute_values_len,
            )
