Scenario 2: process a file on a worker
======================================

A client submits the workflow to an ewoksjob worker. The worker executes the workflow.
For example, the client is the FlyScan host and the worker is a processing host.

Start a worker in a different terminal and keep it running. See :doc:`../howtoguides/worker`.
The commands use the current directory: they write ``scan_0001.nxs`` and the results in ``processed/``.

Make the example data
---------------------

Download :download:`make_pymca_config.py <../_ext/make_pymca_config.py>` and :download:`make_flyscan_data.py <../../scripts/make_flyscan_data.py>`, then:

.. code-block:: bash

    python make_pymca_config.py pymca_example.cfg
    python make_flyscan_data.py pymca_example.cfg scan_0001.nxs

* ``pymca_example.cfg``: the PyMca configuration for the XRF fit. See :doc:`../howtoguides/pymca_config`.
* ``scan_0001.nxs``: a FlyScan NeXus file with 2 XIA channels, the counter ``i0`` and the axes ``samx`` and ``samz``.
  The real time of each point is 100 ms.

Submit from the command line
----------------------------

Set ``EWOKS_CONFIG_URI`` to the path of the ewoksjob configuration of the worker, then submit the workflow:

.. code-block:: bash

    export EWOKS_CONFIG_URI=/path/to/config_redis.py

    ewoksjob submit xrfmap_flyscan --workflow-module ewokssoleildemo.workflows --load-remote \
        -pn convert:filename=$PWD/scan_0001.nxs \
        -pn convert:output_filename=$PWD/processed/scan_0001_bliss.h5 \
        -pn 'sum:detector_names=["xmap1_det00","xmap1_det01"]' \
        -pn 'sum:detector_normalization_template=0.1*<instrument/{}/trigger_count_rate>/(<instrument/{}/elapsed_time>*<instrument/{}/event_count_rate>)' \
        -pn sum:output_root_uri=$PWD/processed/scan_0001_xrf.h5::/1.1 \
        -pn fit:config=$PWD/pymca_example.cfg \
        -pn fit:energy_name=energy \
        -pn norm:counter_name=i0 \
        -pn 'regrid:positioners=["samx","samz"]' \
        --wait 600

The inputs are the same as in :doc:`process_file`.
To check the inputs first, replace ``ewoksjob submit`` by ``ewoks show``, and remove ``--load-remote`` and ``--wait 600``. ``ewoks show`` needs *ewokssoleildemo*.

* ``--load-remote``: the worker loads the workflow. The client does not need *ewokssoleildemo*.
* ``--wait 600``: wait at most 600 seconds for the end of the job.

Submit from Python
------------------

.. code-block:: python

    import os

    from ewoksjob.client import submit

    processed = os.path.abspath("processed")
    inputs = [
        {"id": "convert", "name": "filename", "value": os.path.abspath("scan_0001.nxs")},
        {"id": "convert", "name": "output_filename", "value": f"{processed}/scan_0001_bliss.h5"},
        {"id": "sum", "name": "detector_names", "value": ["xmap1_det00", "xmap1_det01"]},
        {
            "id": "sum",
            "name": "detector_normalization_template",
            "value": "0.1*<instrument/{}/trigger_count_rate>"
            "/(<instrument/{}/elapsed_time>*<instrument/{}/event_count_rate>)",
        },
        {"id": "sum", "name": "output_root_uri", "value": f"{processed}/scan_0001_xrf.h5::/1.1"},
        {"id": "fit", "name": "config", "value": os.path.abspath("pymca_example.cfg")},
        {"id": "fit", "name": "energy_name", "value": "energy"},
        {"id": "norm", "name": "counter_name", "value": "i0"},
        {"id": "regrid", "name": "positioners", "value": ["samx", "samz"]},
    ]
    future = submit(
        args=("xrfmap_flyscan",),
        kwargs={
            "inputs": inputs,
            "load_options": {"root_module": "ewokssoleildemo.workflows"},
        },
    )
    future.result()

Set ``EWOKS_CONFIG_URI`` before you start Python.
The worker loads the workflow. The client needs only ``ewoksjob[redis]``, or ``ewoksjob[sql]`` for SQLite.

The client sends file names, not data.
The worker must see the NeXus file, the PyMca configuration and the output directory at the same paths as the client.

A client on a different host than the worker:

* needs Redis. With SQLite, the client and the worker must be on the same host.
* needs a copy of ``config_redis.py``. Set ``EWOKS_CONFIG_URI`` to this copy.
* needs a file system that the worker host also sees, at the same paths.
