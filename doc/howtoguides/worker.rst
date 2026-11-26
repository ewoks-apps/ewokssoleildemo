Start an ewoksjob worker
========================

A worker executes the workflows that clients submit.
The clients and the worker use the same ewoksjob configuration file.
The worker needs *ewokssoleildemo*. See :doc:`installation`.

Redis
-----

Redis stores the jobs, the results and the Ewoks events.
The clients and the worker can be on different hosts.
To install Redis, see :doc:`installation`.

Download the ewoksjob configuration :download:`config_redis.py <../../scripts/config_redis.py>`.

Start the Redis server in a terminal:

.. code-block:: bash

    redis-server --save "" --appendonly no

Start the worker in a second terminal:

.. code-block:: bash

    ewoksjob --config /path/to/config_redis.py worker --pool=process

When Redis is on a different host, change ``localhost`` in ``config_redis.py`` to the Redis host.
For the clients, set ``EWOKS_CONFIG_URI`` to the path of ``config_redis.py``.

SQLite
------

SQLite files store the jobs, the results and the Ewoks events. A server is not necessary.
The clients and the worker must be on the same host.

Download the ewoksjob configuration :download:`config_sqlite.py <../../scripts/config_sqlite.py>`.
Start the worker:

.. code-block:: bash

    ewoksjob --config /path/to/config_sqlite.py worker --pool=process

The SQLite files are in the directory ``ewokssoleildemo_sqlite`` of the temporary directory of the host, for example ``/tmp/ewokssoleildemo_sqlite``.
For the clients, set ``EWOKS_CONFIG_URI`` to the path of ``config_sqlite.py``.

Options
-------

* ``--pool=process``: the ewoksfluo tasks start sub-processes. The default pool ``prefork`` does not allow this.
* ``--concurrency=2``: the worker executes 2 workflows at the same time.

The other options are the options of ``celery worker``. See the `ewoksjob documentation <https://ewoksjob.readthedocs.io>`_.
