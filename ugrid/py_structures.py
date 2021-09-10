from __future__ import annotations

from numpy import ndarray


class Network1D:
    """This class is used for define/put/inquire/get UGrid data

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
