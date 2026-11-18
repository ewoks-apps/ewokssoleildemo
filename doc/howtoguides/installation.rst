Installation
============

Install *ewokssoleildemo* from the repository:

.. code-block:: bash

    git clone https://gitlab.esrf.fr/workflow/ewoksapps/ewokssoleildemo.git
    cd ewokssoleildemo
    pip install -e ".[job]"

The ``job`` extra installs ``ewoks`` and ``ewoksjob``, to execute workflows and to submit workflows to a worker.
Python 3.10 or higher is necessary.

A worker with Redis also needs a Redis server. Install it with the package manager of the host,
for example ``dnf install redis``.
