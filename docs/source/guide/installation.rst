Installation
============

Requirements
------------

- Python **3.13** (declared in ``pyproject.toml`` as ``requires-python = "==3.13.*"``).
- ``numpy >= 2.0``.
- ``scipy >= 1.15``.

From a clean environment
------------------------

Create a virtual environment and install the package in editable mode along
with the documentation extras:

.. code-block:: bash

   python3.13 -m venv .venv
   source .venv/bin/activate
   python -m pip install -U pip
   python -m pip install -e ".[docs]"

Build the wheel
---------------

To build an installable distribution:

.. code-block:: bash

   python -m pip install -U build
   python -m build --wheel
   pip install dist/derivatives_pricing-*.whl

Build the documentation
-----------------------

Once the ``docs`` extra is installed:

.. code-block:: bash

   cd docs
   make html

The site is generated at ``docs/build/html/index.html``.
