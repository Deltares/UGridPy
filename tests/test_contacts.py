import numpy as np
from numpy.testing import assert_array_equal

from ugrid import UGrid, UGridContacts


def create_contacts():
    r"""Create a contacts"""

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
        dtype=np.int,
    )
    contact_type = np.array(
        [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        dtype=np.int,
    )

    mesh_from_name = "mesh2d"
    mesh_to_name = "1dmesh"
    mesh_from_location = 0
    mesh_to_location = 0
    contact_name_id = ["linkid" for _ in range(edges.size // 2)]
    contact_name_long = ["linklongname" for _ in range(edges.size // 2)]

    edges = UGridContacts(
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
    return edges


def test_contacts_get():
    r"""Tests `contacts_get_num_topologies` and `contacts_get` to read a contacts from file."""

    with UGrid("./data/AllUGridEntities.nc", "r") as ug:
        num_contacts_topologies = ug.contacts_get_num_topologies()
        contacts = ug.contacts_get(num_contacts_topologies - 1)

        expected_contacts = create_contacts()

        assert expected_contacts.name == contacts.name
        assert expected_contacts.mesh_from_name == contacts.mesh_from_name
        assert expected_contacts.mesh_to_name == contacts.mesh_to_name

        assert expected_contacts.mesh_from_location == contacts.mesh_from_location
        assert expected_contacts.mesh_to_location == contacts.mesh_to_location
        assert expected_contacts.num_contacts == contacts.num_contacts

        assert_array_equal(contacts.contact_type, expected_contacts.contact_type)
        assert_array_equal(contacts.edges, expected_contacts.edges)


def test_contacts_define_and_put():
    r"""Tests `contacts_define` and `contacts_put` to define and write a contacts to file."""

    with UGrid("./data/written_files/ContactsWrite.nc", "w+") as ug:
        contacts = create_contacts()
        topology_id = ug.contacts_define(contacts)
        assert topology_id == 0
        ug.contacts_put(topology_id, contacts)
