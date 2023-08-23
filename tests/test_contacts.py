import numpy as np
from meshkernel import Contacts
from numpy.testing import assert_array_equal

from ugrid import UGrid, UGridContacts

def create_contacts() -> UGridContacts:
    r"""Creates an instance of UGridContacts to be used for testing"""

    name = "2d1dlinks"
    edges = np.array(
        [
            13,
            1,
            13,
            2,
            13,
            3,
            13,
            4,
            70,
            5,
            76,
            6,
            91,
            7,
            13,
            8,
            13,
            9,
            13,
            10,
            13,
            11,
            13,
            12,
            178,
            13,
            200,
            14,
            228,
            15,
            255,
            16,
            277,
            17,
            293,
            18,
            304,
            19,
            315,
            20,
            326,
            21,
            337,
            22,
            353,
            23,
        ],
        dtype=np.int32,
    )
    contact_type = np.array(
        [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        dtype=np.int32,
    )

    mesh_from_name = "mesh2d"
    mesh_to_name = "1dmesh"
    mesh_from_location = 0
    mesh_to_location = 0
    contact_name_id = ["linkid" for _ in range(edges.size // 2)]
    contact_name_long = ["linklongname" for _ in range(edges.size // 2)]

    ugrid_contacts = UGridContacts(
        name=name,
        edges=edges,
        contact_type=contact_type,
        mesh_from_name=mesh_from_name,
        mesh_to_name=mesh_to_name,
        mesh_from_location=mesh_from_location,
        mesh_to_location=mesh_to_location,
        contact_name_id=contact_name_id,
        contact_name_long=contact_name_long,
    )
    return ugrid_contacts


def test_contacts_get():
    r"""Tests `contacts_get_num_topologies` and `contacts_get` to read a contacts from file."""

    with UGrid("./data/AllUGridEntities.nc", "r") as ug:
        num_contacts_topologies = ug.contacts_get_num_topologies()
        ugrid_contacts = ug.contacts_get(num_contacts_topologies - 1)

        expected_contacts = create_contacts()

        assert expected_contacts.name == ugrid_contacts.name
        assert expected_contacts.mesh_from_name == ugrid_contacts.mesh_from_name
        assert expected_contacts.mesh_to_name == ugrid_contacts.mesh_to_name

        assert expected_contacts.mesh_from_location == ugrid_contacts.mesh_from_location
        assert expected_contacts.mesh_to_location == ugrid_contacts.mesh_to_location

        assert_array_equal(ugrid_contacts.contact_type, expected_contacts.contact_type)
        assert_array_equal(ugrid_contacts.edges, expected_contacts.edges)


def test_contacts_define_and_put():
    r"""Tests `contacts_define` and `contacts_put` to define and write a contacts to file."""

    with UGrid("./data/written_files/ContactsWrite.nc", "w+") as ug:
        ugrid_contacts = create_contacts()
        topology_id = ug.contacts_define(ugrid_contacts)
        assert topology_id == 0
        ug.contacts_put(topology_id, ugrid_contacts)


def test_contacts_meshkernel_define_and_put():
    r"""Tests a meshkernel contacts is correctly converted to UGridContacts and written to file."""
    mesh1d_indices = np.array([0, 1, 2], dtype=np.int32)
    mesh2d_indices = np.array([0, 1, 2], dtype=np.int32)

    contacts = Contacts(mesh1d_indices=mesh1d_indices, mesh2d_indices=mesh2d_indices)

    contact_type = np.array([3, 3, 3], dtype=np.int32)
    contact_name_id = ["linkid" for _ in range(mesh1d_indices.size)]
    contact_name_long = ["linklongname" for _ in range(mesh1d_indices.size)]

    ugrid_contacts = UGrid.from_meshkernel_contacts_to_ugrid_contacts(
        contacts=contacts,
        name="contacts",
        contact_type=contact_type,
        contact_name_id=contact_name_id,
        contact_name_long=contact_name_long,
        mesh_from_name="mesh2d",
        mesh_to_name="mesh1d",
        mesh_from_location=0,
        mesh_to_location=0,
    )
    with UGrid("./data/written_files/Mesh2DMesKernelWrite.nc", "w+") as ug:
        topology_id = ug.contacts_define(ugrid_contacts)
        assert topology_id == 0
        ug.contacts_put(topology_id, ugrid_contacts)
