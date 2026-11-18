Start an ewoksjob worker
========================

A worker executes the workflows that clients submit.
The clients and the worker use the same ewoksjob configuration file.
``scripts/start_worker.sh`` selects the ewoksjob configuration file for the worker.
For the clients, set the environment variable ``EWOKS_CONFIG_URI`` to the same file.

Run the commands in the root directory of the repository.

Redis
-----

Redis stores the jobs, the results and the Ewoks events.
The clients and the worker can be on different hosts.

.. code-block:: bash

    redis-server --save "" --appendonly no  # terminal 1
    ./scripts/start_worker.sh redis         # terminal 2

    # terminal 3: client
    EWOKS_CONFIG_URI=scripts/config_redis.py \
        python -m ewokssoleildemo.apps.xrfmap scan_0001.nxs parameters.json processed --submit --wait

When Redis is on a different host, set ``EWOKS_REDIS_URL`` for the clients and the worker:

.. code-block:: bash

    export EWOKS_REDIS_URL=redis://testbench:6379

SQLite
------

SQLite files store the jobs, the results and the Ewoks events. A server is not necessary.
The clients and the worker must be on the same host.

.. code-block:: bash

    ./scripts/start_worker.sh sqlite                      # terminal 1

    # terminal 2: client
    EWOKS_CONFIG_URI=scripts/config_sqlite.py \
        python -m ewokssoleildemo.apps.xrfmap scan_0001.nxs parameters.json processed --submit --wait

The SQLite files are in the directory ``sqlite/`` in the root directory of the repository.
Set ``EWOKS_SQLITE_DIR`` to use a different directory.
Use a local disk, not NFS or GPFS.

Options
-------

The worker uses the ``python`` of the active Python environment.

* The worker executes 2 workflows at the same time.
  Other arguments of ``start_worker.sh`` go to the Celery worker, for example ``--concurrency=4``.

The client sends file names, not data.
The worker must see the NeXus files and the output directory at the same paths as the client.
