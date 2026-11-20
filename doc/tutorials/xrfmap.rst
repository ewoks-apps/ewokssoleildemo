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

Process a map in Python
-----------------------

.. code-block:: python

    import os

    from ewoks import execute_graph

    workflow = "ewokssoleildemo.workflows.xrfmap_flyscan"
    processed = os.path.abspath("processed")
    inputs = [
        # Input: the FlyScan NeXus file
        {"id": "convert", "name": "filename", "value": os.path.abspath("scan_0001.nxs")},
        # Output: a new Bliss scan that refers to the NeXus file
        {"id": "convert", "name": "output_filename", "value": f"{processed}/scan_0001_bliss.h5"},
        # XRF detectors to sum: "xmap1channel00" in the NeXus file is "xmap1_det00"
        {"id": "sum", "name": "detector_names", "value": ["xmap1_det00", "xmap1_det01"]},
        # Dead time correction to 0.1 s of live time. "{}" is the detector name.
        {
            "id": "sum",
            "name": "detector_normalization_template",
            "value": "0.1*<instrument/{}/trigger_count_rate>"
            "/(<instrument/{}/elapsed_time>*<instrument/{}/event_count_rate>)",
        },
        # Output: the XRF results in the HDF5 group "/1.1" of a new file
        {"id": "sum", "name": "output_root_uri", "value": f"{processed}/scan_0001_xrf.h5::/1.1"},
        # PyMca configuration
        {"id": "fit", "name": "config", "value": os.path.abspath("pymca_example.cfg")},
        # Beam energy: "convert" saves the monochromator energy as "energy". Do not change.
        {"id": "fit", "name": "energy_name", "value": "energy"},
        # Normalization counter: "i0" in the NeXus file
        {"id": "norm", "name": "counter_name", "value": "i0"},
        # Axes of the map: "samx_dataset" and "samz_dataset" in the NeXus file
        {"id": "regrid", "name": "positioners", "value": ["samx", "samz"]},
    ]
    execute_graph(
        workflow,
        inputs=inputs,
        load_options={"representation": "json_module"},
        convert_destination=f"{processed}/scan_0001_workflow.json",
    )

In ``inputs``, all file names must be absolute.
The example data has a real time of 0.1 s for each point.
For the dead time correction, see :doc:`../explanations/deadtime`.
``load_options`` loads the workflow by its name.
``convert_destination`` saves the workflow with all its inputs.
``execute_graph`` returns the URIs of the results.

The workflow writes these files in ``processed/``:

* ``scan_0001_bliss.h5``: the NeXus file as a Bliss scan. See :doc:`../explanations/flyscan_data`.
* ``scan_0001_xrf.h5``: the XRF results.
* ``scan_0001_workflow.json``: the workflow with all its inputs.

Process a map from the command line
-----------------------------------

The command line reads the processing parameters from a JSON file.
For the example data, ``make_flyscan_data.py`` writes ``parameters.json``:

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

.. code-block:: bash

    python -m ewokssoleildemo.apps.xrfmap scan_0001.nxs parameters.json processed

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

    future = submit(
        args=(workflow,),
        kwargs={"inputs": inputs, "load_options": {"representation": "json_module"}},
    )
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

Use ``--server`` to change the Tango device name of the FlyScan server.
This script is not tested. It needs the FlyScan Tango devices.

The script needs ``ewoksjob[redis]`` (or ``ewoksjob[sql]``) and PyTango. It does not need *ewokssoleildemo*:
only the worker needs it. ``scripts/xrfmap_job.py`` submits the workflow.

.. literalinclude:: ../../scripts/testbench_a1.py
    :language: python
    :caption: scripts/testbench_a1.py

.. literalinclude:: ../../scripts/xrfmap_job.py
    :language: python
    :caption: scripts/xrfmap_job.py
