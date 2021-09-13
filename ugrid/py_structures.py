from __future__ import annotations

from numpy import ndarray, array


class Network1D:
    """This class is used for define/put/inquire/get Network1D data

    Attributes: TODO

    """

    def __init__(
            self,
            name,
            node_x,
            node_y,
            branch_node,
            branch_length,
            geometry_nodes_x,
            geometry_nodes_y,
            branch_order=array([]),
            node_name_id=[],
            node_name_long=[],
            branch_name_id=[],
            branch_name_long=[]
    ):
        self.name: str = name
        self.node_x: ndarray = node_x
        self.node_y: ndarray = node_y
        self.node_name_id: list = node_name_id
        self.node_name_long: list = node_name_long
        self.branch_node: ndarray = branch_node
        self.branch_length: ndarray = branch_length
        self.branch_order: ndarray = branch_order
        self.branch_name_id: list = branch_name_id
        self.branch_name_long: list = branch_name_long
        self.geometry_nodes_x: ndarray = geometry_nodes_x
        self.geometry_nodes_y: ndarray = geometry_nodes_y
        self.is_spherical: bool = False
        self.start_index: int = 0


class Mesh1D:
    """This class is used for define/put/inquire/get Mesh1D data

    Attributes: TODO

    """

    def __init__(
            self,
            name,
            network_name,
            branch_id,
            branch_offset,
            node_x=array([]),
            node_y=array([]),
            edge_node=array([]),
            edge_edge_id=array([]),
            edge_edge_offset=array([]),
            edge_x=array([]),
            edge_y=array([]),
            node_name_id=array([]),
            node_name_long=array([]),
            double_fill_value=-999.0,
            int_fill_value=-999,
    ):
        self.name: str = name
        self.network_name: str = network_name
        self.node_x: ndarray = node_x
        self.node_y: ndarray = node_y
        self.edge_node: ndarray = edge_node
        self.branch_id: ndarray = branch_id
        self.branch_offset: ndarray = branch_offset
        self.node_name_id: ndarray = node_name_id
        self.node_name_long: ndarray = node_name_long
        self.edge_edge_id: ndarray = edge_edge_id
        self.edge_edge_offset: ndarray = edge_edge_offset
        self.edge_x: ndarray = edge_x
        self.edge_y: ndarray = edge_y
        self.is_spherical: bool = False
        self.start_index: int = 0
        self.double_fill_value: float = double_fill_value
        self.int_fill_value: int = int_fill_value


class Mesh2D:
    """This class is used for define/put/inquire/get Mesh1D data

    Attributes: TODO

    """

    def __init__(
            self,
            name,
            node_x,
            node_y,
            edge_node,
            face_node=array([]),
            edge_x=array([]),
            edge_y=array([]),
            face_x=array([]),
            face_y=array([]),
            edge_face=array([]),
            face_edge=array([]),
            face_face=array([]),
            node_z=array([]),
            edge_z=array([]),
            face_z=array([]),
            layer_zs=array([]),
            interface_zs=array([]),
            boundary_node_connectivity=array([]),
            volume_coordinates=array([]),
            num_nodes=0,
            num_edges=0,
            num_faces=0,
            num_layers=0,
            start_index=0,
            num_face_nodes_max=4,
            is_spherical=False,
            double_fill_value=-999.0,
            int_fill_value=-999,
    ):
        self.name : str = name
        self.edge_node: ndarray = edge_node
        self.node_x: ndarray = node_x
        self.node_y: ndarray = node_y

        self.face_node: ndarray = face_node
        self.edge_x: ndarray = edge_x
        self.edge_y: ndarray = edge_y
        self.face_x: ndarray = face_x
        self.face_y: ndarray = face_y
        self.edge_face: ndarray = edge_face
        self.face_edge: ndarray = face_edge
        self.face_face: ndarray = face_face
        self.node_z: ndarray = node_z
        self.edge_z: ndarray = edge_z
        self.face_z: ndarray = face_z
        self.layer_zs: ndarray = layer_zs
        self.interface_zs: ndarray = interface_zs
        self.boundary_node_connectivity: ndarray = boundary_node_connectivity
        self.volume_coordinates: ndarray = volume_coordinates
        self.num_nodes: int = num_nodes
        self.num_edges: int = num_edges
        self.num_faces: int = num_faces
        self.num_layers: int = num_layers
        self.start_index: int = start_index
        self.num_face_nodes_max: int = num_face_nodes_max
        self.is_spherical: int = is_spherical
        self.double_fill_value: float = double_fill_value
        self.int_fill_value: int = int_fill_value


class Contacts:
    """This class is used for define/put/inquire/get Contacts data

    Attributes: TODO

    """

    def __init__(
            self,
            name,
            contacts,
            mesh_from_name,
            mesh_to_name,
            contact_type=array([]),
            contact_name_id=array([]),
            contact_name_long=array([]),
            mesh_from_location=0,
            mesh_to_location=0,
    ):
        self.name: str = name
        self.contacts: ndarray = contacts
        self.mesh_from_name: str = mesh_from_name
        self.mesh_to_name: str = mesh_to_name

        self.contact_type: ndarray = contact_type
        self.contact_name_id: list = contact_name_id
        self.contact_name_long: list = contact_name_long
        self.mesh_from_location: int = mesh_from_location
        self.mesh_to_location: int = mesh_to_location
        self.num_contacts: int = contacts.size // 2
