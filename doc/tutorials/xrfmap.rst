Scenario A.1: process one FlyScan map
=====================================

Scenario A.1:

1. The PI actuators move the sample to the start position.
2. FlyScan scans the full sample.
3. The DataMerger writes the scan data to one NeXus file.
4. A workflow makes the element maps.

FlyScan scans the sample.
The DataMerger, a SOLEIL Tango device, writes the scan data to one NeXus file.
The workflow ``ewokssoleildemo.workflows.xrfmap_flyscan`` makes element maps from this NeXus file.

Run the commands in the root directory of the repository.

Make example data
-----------------

Make a PyMca configuration file. See :doc:`../howtoguides/pymca_config`.

.. code-block:: bash

    python doc/_ext/make_pymca_config.py pymca_example.cfg

Make a FlyScan NeXus file with simulated spectra of a Ta Siemens star:

.. code-block:: bash

    python scripts/make_flyscan_data.py pymca_example.cfg scan_0001.nxs parameters.json

The script also writes the processing parameters of this file to ``parameters.json``:

.. code-block:: json

    {
      "pymca_config": "pymca_example.cfg",
      "detector_names": ["xmap1_det00", "xmap1_det01"],
      "counter_name": "i0",
      "reference_time": 0.1,
      "positioners": ["samx", "samz"],
      "signal": "Ta_L"
    }

For your own data, write this file yourself. See :class:`ewokssoleildemo.apps.xrfmap.XrfmapParameters`.

Process a map in Python
-----------------------

.. code-block:: python

    import pathlib

    from ewoks import execute_graph
    from ewokssoleildemo.apps.xrfmap import WORKFLOW
    from ewokssoleildemo.apps.xrfmap import XrfmapParameters
    from ewokssoleildemo.apps.xrfmap import xrfmap_arguments

    parameters = XrfmapParameters.model_validate_json(
        pathlib.Path("parameters.json").read_text()
    )
    arguments = xrfmap_arguments("scan_0001.nxs", "processed", parameters)
    execute_graph(WORKFLOW, **arguments)

``execute_graph`` returns the URIs of the results.

The same from the command line:

.. code-block:: bash

    python -m ewokssoleildemo.apps.xrfmap scan_0001.nxs parameters.json processed

The workflow writes these files in ``processed/``:

* ``scan_0001_bliss.h5``: the NeXus file as a Bliss scan. See :doc:`../explanations/flyscan_data`.
* ``scan_0001_xrf.h5``: the XRF results.
* ``scan_0001_workflow.json``: the workflow with all its inputs.

Show the maps
-------------

.. code-block:: bash

    silx view processed/scan_0001_xrf.h5

Open ``/1.1/regrid/results/parameters`` and select ``Ta_L``.
The map shows the Siemens star.

Process a map on a worker
-------------------------

Start a worker. See :doc:`../howtoguides/worker`.
Then submit the workflow:

.. code-block:: python

    from ewoksjob.client import submit

    future = submit(args=(WORKFLOW,), kwargs=arguments)
    future.result()

Before you start Python, set the environment variable ``EWOKS_CONFIG_URI`` to the ewoksjob configuration file
of the worker, for example ``scripts/config_redis.py`` or ``scripts/config_sqlite.py``.

The same from the command line:

.. code-block:: bash

    EWOKS_CONFIG_URI=scripts/config_redis.py \
        python -m ewokssoleildemo.apps.xrfmap scan_0001.nxs parameters.json processed --submit --wait

Process a map after each scan on the test bench
-----------------------------------------------

``scripts/testbench_a1.py`` sends a FlyScan configuration file to the FlyScan server and starts the scan.
At the end of the scan, it reads the NeXus file name from the DataMerger and submits the workflow.

.. code-block:: bash

    EWOKS_CONFIG_URI=scripts/config_redis.py \
        python scripts/testbench_a1.py scan.cfg parameters.json processed

Use ``--server`` and ``--merger`` to change the Tango device names.
This script is not tested. It needs the FlyScan Tango devices.

.. literalinclude:: ../../scripts/testbench_a1.py
    :language: python
    :caption: scripts/testbench_a1.py
