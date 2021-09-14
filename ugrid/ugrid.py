import logging
import platform
from ctypes import CDLL, byref, c_char_p, c_int
from enum import IntEnum, unique
from pathlib import Path
from typing import Callable

from ugrid.c_structures import (
    CContacts,
    CMesh1D,
    CMesh2D,
    CNetwork1D,
    decode_byte_vector_to_list_of_strings,
    decode_byte_vector_to_string,
)
from ugrid.errors import UGridError
from ugrid.py_structures import Contacts, Mesh1D, Mesh2D, Network1D
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
        self._open(file_path, method)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self._execute_function(self.lib.ug_file_close, self._file_id)
        error_message = self._get_error()

        # Raise an exception if an error is present
        if error_message:
            raise UGridError(error_message)

    def _open(self, file_path: str, method: str) -> None:
        """Opens a NetCDF file containing a UGrid entities

        Comment

        Args:
            file_path (bool): The path of the file to open
            method (bool): The opening method ("r" for read, "w" for write, and "w+" for replace)
        """

        if method == "r":
            file_mode = self.lib.ug_file_read_mode()
        elif method == "w":
            file_mode = self.lib.ug_file_write_mode()
        elif method == "w+":
            file_mode = self.lib.ug_file_replace_mode()
        else:
            raise ValueError("Unsupported file mode")

        self._file_id = c_int(-1)

        file_path_bytes = bytes(file_path, encoding="utf8")
        self._execute_function(
            self.lib.ug_file_open,
            file_path_bytes,
            c_int(file_mode),
            byref(self._file_id),
        )

    def network1d_get_num_topologies(self) -> int:
        """Gets the number of network topologies contained in the file.

        Returns:
            int: The number of network topologies contained in the file.
        """

        topology_enum = self.lib.ug_topology_get_network1d_enum()
        num_topologies = self.lib.ug_topology_get_count(
            self._file_id, c_int(topology_enum)
        )
        return num_topologies

    def _network1d_inquire(self, topology_id) -> CNetwork1D:
        """For internal use only.

        Inquires the network1d dimensions and names.

        Args:
            topology_id (int): The index of the network topology to inquire.

        Returns:
            CNetwork1D: The network1d dimensions.
        """

        c_network1d = CNetwork1D()
        self._execute_function(
            self.lib.ug_network1d_inq,
            self._file_id,
            c_int(topology_id),
            byref(c_network1d),
        )
        return c_network1d

    def network1d_get(self, topology_id) -> Network1D:
        """Gets the network1d data.

        Args:
            topology_id (int): The index of the network1d topology to retrieve.

        Returns:
            Network1D: The network1d (dimensions and data)
        """

        c_network1d = self._network1d_inquire(topology_id)
        name_size = self.lib.ug_name_get_length()
        name_long_size = self.lib.ug_name_get_long_length()

        network1d = c_network1d.allocate_memory(name_size, name_long_size)
        self._execute_function(
            self.lib.ug_network1d_get,
            self._file_id,
            c_int(topology_id),
            byref(c_network1d),
        )

        network1d.is_spherical = bool(c_network1d.is_spherical)
        network1d.start_index = c_network1d.start_index
        network1d.name = decode_byte_vector_to_string(c_network1d.name, name_size)
        network1d.node_name_id = decode_byte_vector_to_list_of_strings(
            c_network1d.node_name_id, c_network1d.num_nodes, name_size
        )
        network1d.node_name_long = decode_byte_vector_to_list_of_strings(
            c_network1d.node_name_long, c_network1d.num_nodes, name_long_size
        )

        network1d.branch_name_id = decode_byte_vector_to_list_of_strings(
            c_network1d.branch_name_id, c_network1d.num_branches, name_size
        )
        network1d.branch_name_long = decode_byte_vector_to_list_of_strings(
            c_network1d.branch_name_long, c_network1d.num_branches, name_long_size
        )

        return network1d

    def network1d_define(self, network1d: Network1D) -> int:
        """Defines a new network1d in a UGrid file.

        Args:
            network1d (Network1D): A network1d (dimensions and data)

        Returns:
            int: The index of the defined network topology.
        """

        name_size = self.lib.ug_name_get_length()
        name_long_size = self.lib.ug_name_get_long_length()

        c_network1D = CNetwork1D.from_py_structure(network1d, name_size, name_long_size)

        c_topology_id = c_int(-1)

        self._execute_function(
            self.lib.ug_network1d_def,
            self._file_id,
            byref(c_network1D),
            byref(c_topology_id),
        )

        return c_topology_id.value

    def network1d_put(self, topology_id: int, network1d: Network1D) -> None:
        """Writes a new network1d to UGrid file.

        Args:
            topology_id (int): The index of the network1d topology to write.
            network1d (Network1D): An instance of Network1D (with dimensions and data)
        """

        name_size = self.lib.ug_name_get_length()
        name_long_size = self.lib.ug_name_get_long_length()

        c_network1D = CNetwork1D.from_py_structure(network1d, name_size, name_long_size)

        self._execute_function(
            self.lib.ug_network1d_put,
            self._file_id,
            c_int(topology_id),
            byref(c_network1D),
        )

    def mesh1d_get_num_topologies(self) -> int:
        """Gets the number of mesh1d topologies contained in the file.

        Returns:
            int: The number of mesh1d topologies contained in the file.
        """

        topology_enum = self.lib.ug_topology_get_mesh1d_enum()
        num_topologies = self.lib.ug_topology_get_count(
            self._file_id, c_int(topology_enum)
        )
        return num_topologies

    def _mesh1d_inquire(self, topology_id) -> CMesh1D:
        """For internal use only.

        Inquires the mesh1d dimensions and names.

        Args:
            topology_id (int): The index of the mesh1d topology to inquire.

        Returns:
            CMesh1D: The mesh1d dimensions.

        """

        c_mesh1d = CMesh1D()
        self._execute_function(
            self.lib.ug_mesh1d_inq,
            self._file_id,
            c_int(topology_id),
            byref(c_mesh1d),
        )
        return c_mesh1d

    def mesh1d_get(self, topology_id) -> Mesh1D:
        """Gets the mesh1d data.

        Args:
            topology_id (int): The index of the mesh1d topology to retrieve.

        Returns:
            Mesh1D: The mesh1d (dimensions and data)
        """

        c_mesh1d = self._mesh1d_inquire(topology_id)
        name_size = self.lib.ug_name_get_length()
        name_long_size = self.lib.ug_name_get_long_length()

        mesh1d = c_mesh1d.allocate_memory(name_size, name_long_size)
        self._execute_function(
            self.lib.ug_mesh1d_get,
            self._file_id,
            c_int(topology_id),
            byref(c_mesh1d),
        )

        mesh1d.is_spherical = bool(c_mesh1d.is_spherical)
        mesh1d.start_index = c_mesh1d.start_index
        mesh1d.double_fill_value = c_mesh1d.double_fill_value
        mesh1d.int_fill_value = c_mesh1d.int_fill_value

        mesh1d.name = decode_byte_vector_to_string(c_mesh1d.name, name_size)
        mesh1d.network_name = decode_byte_vector_to_string(
            c_mesh1d.network_name, name_size
        )

        mesh1d.node_name_id = decode_byte_vector_to_list_of_strings(
            c_mesh1d.node_name_id, c_mesh1d.num_nodes, name_size
        )
        mesh1d.node_name_long = decode_byte_vector_to_list_of_strings(
            c_mesh1d.node_name_long, c_mesh1d.num_nodes, name_long_size
        )

        return mesh1d

    def mesh1d_define(self, mesh1d: Mesh1D) -> int:
        """Defines a new mesh1d in a UGrid file.

        Args:
            mesh1d (Mesh1D): A mesh1d (dimensions and data)

        Returns:
            int: The index of the defined mesh1d topology.
        """

        name_size = self.lib.ug_name_get_length()
        name_long_size = self.lib.ug_name_get_long_length()

        c_mesh1d = CMesh1D.from_py_structure(mesh1d, name_size, name_long_size)

        c_topology_id = c_int(-1)

        self._execute_function(
            self.lib.ug_mesh1d_def, self._file_id, byref(c_mesh1d), byref(c_topology_id)
        )

        return c_topology_id.value

    def mesh1d_put(self, topology_id: int, mesh1d: Mesh1D) -> None:
        """Writes a new mesh1d to UGrid file.

        Args:
            topology_id (int): The index of the mesh1d topology to write.
            mesh1d (Mesh1D): An instance of mesh1d (with dimensions and data)
        """

        name_size = self.lib.ug_name_get_length()
        name_long_size = self.lib.ug_name_get_long_length()

        c_mesh1d = CMesh1D.from_py_structure(mesh1d, name_size, name_long_size)

        self._execute_function(
            self.lib.ug_mesh1d_put, self._file_id, c_int(topology_id), byref(c_mesh1d)
        )

    def mesh2d_get_num_topologies(self) -> int:
        """Description

        Gets the number of mesh2d topologies contained in the file.

        Returns:
            int: The number of mesh2d topologies contained in the file.

        """

        topology_enum = self.lib.ug_topology_get_mesh2d_enum()
        num_topologies = self.lib.ug_topology_get_count(
            self._file_id, c_int(topology_enum)
        )
        return num_topologies

    def _mesh2d_inquire(self, topology_id) -> CMesh2D:
        """For internal use only.

        Inquires the mesh2d dimensions and names.

        Args:
            topology_id (int): The index of the mesh2d topology to inquire.

        Returns:
            CMesh2D: The mesh2d dimensions.

        """

        c_mesh2d = CMesh2D()
        self._execute_function(
            self.lib.ug_mesh2d_inq,
            self._file_id,
            c_int(topology_id),
            byref(c_mesh2d),
        )
        return c_mesh2d

    def mesh2d_get(self, topology_id) -> Mesh2D:
        """Gets the mesh2d data.

        Args:
            topology_id (int): The index of the mesh2d topology to retrieve.

        Returns:
            Mesh2D: The mesh2d (dimensions and data)
        """

        c_mesh2d = self._mesh2d_inquire(topology_id)
        name_size = self.lib.ug_name_get_length()

        mesh2d = c_mesh2d.allocate_memory(name_size)
        self._execute_function(
            self.lib.ug_mesh2d_get,
            self._file_id,
            c_int(topology_id),
            byref(c_mesh2d),
        )

        mesh2d.is_spherical = bool(c_mesh2d.is_spherical)
        mesh2d.start_index = c_mesh2d.start_index
        mesh2d.double_fill_value = c_mesh2d.double_fill_value
        mesh2d.int_fill_value = c_mesh2d.int_fill_value

        mesh2d.name = decode_byte_vector_to_string(c_mesh2d.name, name_size)

        return mesh2d

    def mesh2d_define(self, mesh2d: Mesh2D) -> int:
        """Defines a new mesh2d in a UGrid file.

        Args:
            mesh2d (Mesh2D): A mesh2d (dimensions and data)

        Returns:
            int: The index of the defined mesh2d topology.
        """

        name_size = self.lib.ug_name_get_length()

        c_mesh2d = CMesh2D.from_py_structure(mesh2d, name_size)

        c_topology_id = c_int(-1)

        self._execute_function(
            self.lib.ug_mesh2d_def, self._file_id, byref(c_mesh2d), byref(c_topology_id)
        )

        return c_topology_id.value

    def mesh2d_put(self, topology_id: int, mesh2d: Mesh2D) -> None:
        """Writes a new mesh2d in a UGrid file.

        Args:
            topology_id (int): The index of the mesh2d topology to write.
            mesh2d (Mesh2D): A mesh2d (dimensions and data)
        """

        name_size = self.lib.ug_name_get_length()
        c_mesh2d = CMesh2D.from_py_structure(mesh2d, name_size)

        self._execute_function(
            self.lib.ug_mesh2d_put, self._file_id, c_int(topology_id), byref(c_mesh2d)
        )

    def contacts_get_num_topologies(self) -> int:
        """Description

        Gets the number of contacts topologies contained in the file.

        Returns:
            int: The number of contacts topologies contained in the file.

        """

        topology_enum = self.lib.ug_topology_get_contacts_enum()
        num_topologies = self.lib.ug_topology_get_count(
            self._file_id, c_int(topology_enum)
        )
        return num_topologies

    def _contacts_inquire(self, topology_id) -> CContacts:
        """For internal use only.

        Inquires the contacts dimensions and names.

        Args:
            topology_id (int): The index of the contacts topology to inquire.

        Returns:
            CContacts: The contacts dimensions.

        """

        c_contacts = CContacts()
        self._execute_function(
            self.lib.ug_contacts_inq,
            self._file_id,
            c_int(topology_id),
            byref(c_contacts),
        )
        return c_contacts

    def contacts_get(self, topology_id) -> Contacts:
        """Gets the contacts data.

        Args:
            topology_id (int): The index of the contacts topology to retrieve.

        Returns:
            Contacts: The contacts (dimensions and data)
        """

        c_contacts = self._contacts_inquire(topology_id)
        name_size = self.lib.ug_name_get_length()
        name_long_size = self.lib.ug_name_get_long_length()

        contacts = c_contacts.allocate_memory(name_size, name_long_size)
        self._execute_function(
            self.lib.ug_contacts_get,
            self._file_id,
            c_int(topology_id),
            byref(c_contacts),
        )

        contacts.name = decode_byte_vector_to_string(c_contacts.name, name_size)
        contacts.contact_name_id = decode_byte_vector_to_list_of_strings(
            c_contacts.contact_name_id, c_contacts.num_contacts, name_size
        )
        contacts.contact_name_long = decode_byte_vector_to_list_of_strings(
            c_contacts.contact_name_long, c_contacts.num_contacts, name_long_size
        )

        contacts.mesh_from_name = decode_byte_vector_to_string(
            c_contacts.mesh_from_name, name_size
        )
        contacts.mesh_to_name = decode_byte_vector_to_string(
            c_contacts.mesh_to_name, name_size
        )

        return contacts

    def contacts_define(self, contacts: Contacts) -> int:
        """Defines a new contacts in a UGrid file.

        Args:
            contacts (Contacts): An instance of Contacts class (dimensions and data)

        Returns:
            int: The index of the defined contacts topology.
        """

        name_size = self.lib.ug_name_get_length()
        name_long_size = self.lib.ug_name_get_long_length()

        c_contacts = CContacts.from_py_structure(contacts, name_size, name_long_size)

        c_topology_id = c_int(-1)

        self._execute_function(
            self.lib.ug_contacts_def,
            self._file_id,
            byref(c_contacts),
            byref(c_topology_id),
        )

        return c_topology_id.value

    def contacts_put(self, topology_id: int, contacts: Contacts) -> None:
        """Writes a new contacts in a UGrid file.

        Args:
            topology_id (int): The index of the contacts topology to write.
            contacts (Contacts): A contacts (dimensions and data)
        """

        name_size = self.lib.ug_name_get_length()
        name_long_size = self.lib.ug_name_get_long_length()

        c_contacts = CContacts.from_py_structure(contacts, name_size, name_long_size)

        self._execute_function(
            self.lib.ug_contacts_put,
            self._file_id,
            c_int(topology_id),
            byref(c_contacts),
        )

    def _get_error(self) -> str:
        c_error_message = c_char_p()
        self.lib.ug_error_get(byref(c_error_message))
        return c_error_message.value.decode("ASCII")

    def get_ugrid_version(self) -> str:
        """Get the version of the underlying C++ UGrid library

        Returns:
            str: The version string
        """

        c_ugrid_version = c_char_p()
        self.lib.mkernel_get_version(byref(c_ugrid_version))
        return c_ugrid_version.value.decode("ASCII")

    def get_ugridpy_version(self) -> str:
        """Get the version of this Python wrapper

        Returns:
            str: The version string
        """

        return __version__

    def _execute_function(self, function: Callable, *args):
        """Utility function to execute a C function of UGrid and checks its status.

        Args:
            function (Callable): The function which we want to call.
            args: Arguments which will be passed to `function`.

        Raises:
            UGridError: This exception gets raised,
             if the UGrid library reports an error.
        """
        if function(*args) != Status.SUCCESS:
            error_message = self._get_error()
            raise UGridError(error_message)
