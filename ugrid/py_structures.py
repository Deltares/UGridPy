from __future__ import annotations

from numpy import ndarray


class Network1D:
    """This class is used for define/put/inquire/get Network1D data

    Attributes: TODO

    """

    def __init__(
            self,
            node_x,
            node_y,
            branch_node,
            branch_length,
            branch_order,
            geometry_nodes_x,
            geometry_nodes_y,
    ):
        self.name: str = None
        self.node_x: ndarray = node_x
        self.node_y: ndarray = node_y
        self.node_name_id: list = None
        self.node_name_long: list = None
        self.branch_node: ndarray = branch_node
        self.branch_length: ndarray = branch_length
        self.branch_order: ndarray = branch_order
        self.branch_name_id: list = None
        self.branch_name_long: list = None
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
            node_x=None,
            node_y=None,
            edge_node=None,
            edge_edge_id=None,
            edge_edge_offset=None,
            edge_x=None,
            edge_y=None,
            node_name_id=None,
            node_name_long=None):
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
        self.is_spherical: int = 0
        self.start_index: int = 0
