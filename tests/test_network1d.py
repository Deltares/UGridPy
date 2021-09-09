import numpy as np
import pytest
from numpy import ndarray
from numpy.testing import assert_array_equal

from ugrid import Network1D, UGrid


def test_network1d_get():
    r"""Tests `network1d_get_num_topologies` and `network1d_get` to read a network1d from file."""

    with UGrid("./data/AllUGridEntities.nc", "r") as ugrid_lib:
        num_network_topologies = ugrid_lib.network1d_get_num_topologies()
        network1d = ugrid_lib.network1d_get(num_network_topologies - 1)
        assert_array_equal(1, num_network_topologies)
