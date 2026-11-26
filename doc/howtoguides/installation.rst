Installation
============

Python 3.10 or higher is necessary. Install in a Python environment, for example a venv or a conda environment.

Processing host
---------------

To execute the workflows, or to start a worker, install *ewokssoleildemo*:

.. code-block:: bash

    pip install "ewokssoleildemo[job]"

The ``job`` extra installs ``ewoks`` and ``ewoksjob``.

A worker with Redis also needs a Redis server. Install it with conda (root is not necessary):

.. code-block:: bash

    conda create -n redis -c conda-forge redis-server
    conda activate redis

or with the package manager of the host, for example ``dnf install redis``.

Client
------

A client that only submits workflows to a worker does not need *ewokssoleildemo*.
For a worker with Redis:

.. code-block:: bash

    pip install "ewoksjob[redis]"

For a worker with SQLite:

.. code-block:: bash

    pip install "ewoksjob[sql]"
