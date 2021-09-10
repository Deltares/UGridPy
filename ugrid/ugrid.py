import logging
import platform
from ctypes import CDLL, byref, c_char_p, c_int
from enum import IntEnum, unique
from pathlib import Path
from typing import Callable

from ugrid.c_structures import (
    CNetwork1D,
    decode_byte_vector_to_list_of_string,
    decode_byte_vector_to_string,
)
from ugrid.errors import UGridError
from ugrid.py_structures import Network1D
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

    def _open(self, file_path, method) -> None:
        """Description

        Comment

        Args:

        """

        if method == "r":
            file_mode = self.lib.ug_file_read_mode()
        elif method == "w":
            file_mode = self.lib.ug_file_write_mode()
        elif method == "w+":
            file_mode = self.lib.ug_file_replace_mode()
        else:
            raise ValueError('Unsupported file mode')

        self._file_id = c_int(-1)

        file_path_bytes = bytes(file_path, encoding="utf8")
        self._execute_function(
            self.lib.ug_file_open,
            file_path_bytes,
            c_int(file_mode),
            byref(self._file_id),
        )


    def network1d_get_num_topologies(self) -> int:
        """Description

        Comment

        Args:

        """

        topology_enum = self.lib.ug_topology_get_network1d_enum()
        num_topologies = self.lib.ug_topology_get_count(
            self._file_id, c_int(topology_enum)
        )
        return num_topologies

    def _network1d_inquire(self, topology_id) -> CNetwork1D:
        """Description

        Comment

        Args:

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
        """Description

        Comment

        Args:

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
        network1d.node_name_id = decode_byte_vector_to_list_of_string(
            c_network1d.node_name_id, c_network1d.num_nodes, name_size
        )
        network1d.node_name_long = decode_byte_vector_to_list_of_string(
            c_network1d.node_name_long, c_network1d.num_nodes, name_long_size
        )

        network1d.branch_name_id = decode_byte_vector_to_list_of_string(
            c_network1d.branch_name_id, c_network1d.num_branches, name_size
        )
        network1d.branch_name_long = decode_byte_vector_to_list_of_string(
            c_network1d.branch_name_long, c_network1d.num_branches, name_long_size
        )

        return network1d

    def network1d_define(self, network1d: Network1D) -> int:
        """Description

        Comment

        Args:

        """

        name_size = self.lib.ug_name_get_length()
        name_long_size = self.lib.ug_name_get_long_length()

        c_network1D = CNetwork1D.from_py_structure(network1d, name_size, name_long_size)

        c_topology_id = c_int(-1)

        self._execute_function(self.lib.ug_network1d_def, self._file_id, byref(c_network1D), byref(c_topology_id))

        return c_topology_id.value

    def network1d_put(self, topology_id: int, network1d: Network1D) -> None:
        """Description

        Comment

        Args:

        """

        name_size = self.lib.ug_name_get_length()
        name_long_size = self.lib.ug_name_get_long_length()

        c_network1D = CNetwork1D.from_py_structure(network1d, name_size, name_long_size)

        self._execute_function(
            self.lib.ug_network1d_put, self._file_id, c_int(topology_id), byref(c_network1D)
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
