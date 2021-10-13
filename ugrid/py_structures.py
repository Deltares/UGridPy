from __future__ import annotations

from numpy import array, ndarray


class UGridNetwork1D:
    """This class is used for define/put/inquire/get Network1D data

    Attributes:
        name (str): The network name.
        node_x (ndarray): The x-coordinates of the network node.
        node_y (ndarray): The y-coordinates of the network node.
        edge_node (ndarray): The nodes defining each branch.
        edge_length (ndarray): The edge lengths.
        geometry_nodes_x (ndarray): The geometry nodes x coordinates.
        geometry_nodes_y (ndarray): The geometry nodes y coordinates.
        num_edge_geometry_nodes (ndarray): The number of geometry node on each branch.
        edge_order (ndarray): The order of the branches.
        node_id (str): The node names ids.
        node_name_long (str): The node long names.
        edge_id (list): The name of the branches.
        edge_long_name (list): The long name of the branches.
    """

    def __init__(
        self,
        name,
        node_x,
        node_y,
        edge_node,
        edge_length,
        geometry_nodes_x,
        geometry_nodes_y,
        num_edge_geometry_nodes,
        edge_order=array([]),
        node_id=[],
        node_name_long=[],
        edge_id=[],
        edge_long_name=[],
    ):
        self.name: str = name
        self.node_x: ndarray = node_x
        self.node_y: ndarray = node_y
        self.node_id: list = node_id
        self.node_long_name: list = node_name_long
        self.edge_node: ndarray = edge_node
        self.edge_length: ndarray = edge_length
        self.edge_order: ndarray = edge_order
        self.edge_id: list = edge_id
        self.edge_long_name: list = edge_long_name
        self.geometry_nodes_x: ndarray = geometry_nodes_x
        self.geometry_nodes_y: ndarray = geometry_nodes_y
        self.num_edge_geometry_nodes = num_edge_geometry_nodes
        self.is_spherical: bool = False
        self.start_index: int = 0


class UGridMesh1D:
    """This class is used for define/put/inquire/get Mesh1D data

    Attributes:
        name (c_char_p): The mesh name.
        network_name (c_char_p): The x-coordinates of the network node.
        node_x (ndarray):  The node x coordinate.
        node_y (ndarray):  The node y coordinate.
        edge_node (ndarray): The edge node connectivity.
        node_edge_id (ndarray):  The network edge id where every node lies.
        node_edge_offset (ndarray): The offset of each node on the network edge.
        node_name_id (list): A list of node names ids.
        node_name_long (c_char_p): A list of node long names.
        edge_edge_id (ndarray): The network edge id where every edge lies.
        edge_edge_offset (ndarray): The offset of each edge on the network edge.
        edge_x (ndarray): The edge x coordinate.
        edge_y (ndarray): The edge y coordinate.
        double_fill_value (c_double): The fill value for array of doubles.
        int_fill_value (c_int): The fill value for array of integers.
    """

    def __init__(
        self,
        name,
        network_name,
        node_edge_id,
        node_edge_offset,
        node_x=array([]),
        node_y=array([]),
        edge_node=array([]),
        edge_edge_id=array([]),
        edge_edge_offset=array([]),
        edge_x=array([]),
        edge_y=array([]),
        node_name_id=[],
        node_name_long=[],
        double_fill_value=-999.0,
        int_fill_value=-999,
    ):
        self.name: str = name
        self.network_name: str = network_name
        self.node_x: ndarray = node_x
        self.node_y: ndarray = node_y
        self.edge_node: ndarray = edge_node
        self.node_edge_id: ndarray = node_edge_id
        self.node_edge_offset: ndarray = node_edge_offset
        self.node_name_id: list = node_name_id
        self.node_name_long: list = node_name_long
        self.edge_edge_id: ndarray = edge_edge_id
        self.edge_edge_offset: ndarray = edge_edge_offset
        self.edge_x: ndarray = edge_x
        self.edge_y: ndarray = edge_y
        self.is_spherical: bool = False
        self.start_index: int = 0
        self.double_fill_value: float = double_fill_value
        self.int_fill_value: int = int_fill_value


class UGridMesh2D:
    """This class is used for define/put/inquire/get Mesh2D data

    Attributes:
        name (str): The mesh name.
        edge_nodes (ndarray): The nodes composing each mesh 2d edge.
        face_nodes (ndarray): The nodes composing each mesh 2d face.
        nodes_per_face (ndarray): The nodes composing each mesh 2d face.
        node_x (ndarray): The x-coordinates of the nodes.
        node_y (ndarray): The y-coordinates of the nodes.
        edge_x (ndarray): The x-coordinates of the mesh edges' middle points.
        edge_y (ndarray): The x-coordinates of the mesh edges' middle points.
        face_x (ndarray): The x-coordinates of the mesh faces' mass centers.
        face_y (ndarray): The y-coordinates of the mesh faces' mass centers.
        edge_face (ndarray): The edges composing each face.
        face_edge (ndarray): For each face, the edges composing it.
        face_face (ndarray): For each face, the neighboring faces.
        node_z (ndarray): The node z coordinates.
        edge_z (ndarray): The edge z coordinates.
        face_z (ndarray): The face z coordinates.
        layer_zs (ndarray): The z coordinates of a layer.
        interface_zs (ndarray): The z coordinates of a layer interface.
        boundary_node_connectivity (ndarray): To be detailed.
        volume_coordinates (ndarray): To be detailed.
        start_index (int): The start index used in arrays using indices, such as in the branch_node array.
        num_face_nodes_max (int): The maximum number of face nodes.
        is_spherical (c_int): 1 if coordinates are in a spherical system, 0 otherwise.
        double_fill_value (c_double): The fill value for array of doubles.
        int_fill_value (c_int): The fill value for array of integers.
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
        start_index=0,
        num_face_nodes_max=4,
        is_spherical=False,
        double_fill_value=-999.0,
        int_fill_value=-999,
    ):
        self.name: str = name
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
        self.start_index: int = start_index
        self.num_face_nodes_max: int = num_face_nodes_max
        self.is_spherical: int = is_spherical
        self.double_fill_value: float = double_fill_value
        self.int_fill_value: int = int_fill_value


class UGridContacts:
    """This class is used for define/put/inquire/get Contacts data

    Attributes:
        name (str): The name of the contact entity.
        edges (ndarray): The actual contacts, expressed as pair of indices from a mesh index to another mesh index.
        contact_type (ndarray): For each contact its type.
        contact_name_id (list): The name of each contact.
        contact_name_long (list): The long name of each contact.
        mesh_from_name (str): The name of the mesh where the contacts start.
        mesh_to_name (str): The name of the mesh where the contacts ends.
        mesh_from_location (c_int): The location type (node, edge or face) at the contact start.
        mesh_to_location (c_int): The location type (node, edge or face) at the contact end.
        num_contacts (c_int): The number of contacts.
    """

    def __init__(
        self,
        name,
        edges,
        mesh_from_name,
        mesh_to_name,
        contact_type=array([]),
        contact_name_id=list,
        contact_name_long=list,
        mesh_from_location=0,
        mesh_to_location=0,
    ):
        self.name: str = name
        self.edges: ndarray = edges
        self.mesh_from_name: str = mesh_from_name
        self.mesh_to_name: str = mesh_to_name

        self.contact_type: ndarray = contact_type
        self.contact_name_id: list = contact_name_id
        self.contact_name_long: list = contact_name_long
        self.mesh_from_location: int = mesh_from_location
        self.mesh_to_location: int = mesh_to_location
