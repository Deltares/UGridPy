# UGridPy

`UGridPy` is a library for writing/reading ugrid files.
It supports 1D and 2D unstructured meshes.
Support for curvilinear meshes is planned.
The underlying C++ library `UGrid` can be found [here](https://github.com/Deltares/UGrid.git).

# Installation

## Windows

The library can be installed from PyPI by executing

```bash
pip install ugrid
```

## Linux

Currently, we only offer wheels specific to Deltares' CentOS machines.
We plan to release a manylinux wheel at PyPI in the future. 

# Examples

*To be detailed*

# License

`UGridPy` uses the MIT license.
However, the wheels on PyPI bundle the LGPL licensed [UGrid](https://github.com/Deltares/UGrid).
Please make sure that this fits your needs before depending on it.


# Contributing

In order to install `UGridPy` locally, please execute the following line inside your virtual environment

```bash
pip install -e ".[tests, lint, docs]"
```

Then add a compiled `UGridApi.dll` into your `src` folder.

Also make sure that your editor is configured to format the code with [`black`](https://black.readthedocs.io/en/stable/) and [`isort`](https://pycqa.github.io/isort/).
