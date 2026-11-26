Scenario 1: process a FlyScan file
==================================

The workflow ``xrfmap_flyscan`` makes element maps from a FlyScan NeXus file.
This tutorial makes a FlyScan NeXus file with simulated XRF spectra of a Ta Siemens star, and processes it.

Install *ewokssoleildemo* first. See :doc:`../howtoguides/installation`.
The commands use the current directory: they write ``scan_0001.nxs`` and the results in ``processed/``.

Make the example data
---------------------

Download :download:`make_pymca_config.py <../_ext/make_pymca_config.py>` and :download:`make_flyscan_data.py <../../scripts/make_flyscan_data.py>`, then:

.. code-block:: bash

    python make_pymca_config.py pymca_example.cfg
    python make_flyscan_data.py pymca_example.cfg scan_0001.nxs

* ``pymca_example.cfg``: the PyMca configuration for the XRF fit. See :doc:`../howtoguides/pymca_config`.
* ``scan_0001.nxs``: a FlyScan NeXus file with 2 XIA channels, the counter ``i0`` and the axes ``samx`` and ``samz``.
  The real time of each point is 100 ms. See :doc:`../explanations/flyscan_data`.

Execute the workflow from the command line
------------------------------------------

.. code-block:: bash

    ewoks execute xrfmap_flyscan --workflow-module ewokssoleildemo.workflows \
        -pn convert:filename=$PWD/scan_0001.nxs \
        -pn convert:output_filename=$PWD/processed/scan_0001_bliss.h5 \
        -pn 'sum:detector_names=["xmap1_det00","xmap1_det01"]' \
        -pn 'sum:detector_normalization_template=0.1*<instrument/{}/trigger_count_rate>/(<instrument/{}/elapsed_time>*<instrument/{}/event_count_rate>)' \
        -pn sum:output_root_uri=$PWD/processed/scan_0001_xrf.h5::/1.1 \
        -pn fit:config=$PWD/pymca_example.cfg \
        -pn fit:energy_name=energy \
        -pn norm:counter_name=i0 \
        -pn 'regrid:positioners=["samx","samz"]'

* ``--workflow-module`` gives the Python package of the workflow.
* ``-pn NODE:NAME=VALUE`` gives the value of the input ``NAME`` of the node ``NODE``.
* All file names must be absolute.

Before the execution, check the inputs: replace ``ewoks execute`` by ``ewoks show`` with the same options.
``ewoks show`` shows all inputs of all nodes, with their values and descriptions.

The workflow writes these files in ``processed/``:

* ``scan_0001_bliss.h5``: the NeXus file as a Bliss scan. See :doc:`../explanations/flyscan_data`.
* ``scan_0001_xrf.h5``: the XRF results.

To also save the workflow with all its inputs, add the execution option ``-o convert_destination=$PWD/processed/scan_0001_workflow.json``.

Execute the workflow from Python
--------------------------------

.. code-block:: python

    import os

    from ewoks import execute_graph

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
    execute_graph(
        "xrfmap_flyscan",
        inputs=inputs,
        load_options={"root_module": "ewokssoleildemo.workflows"},
    )

To also save the workflow with all its inputs, add ``convert_destination=f"{processed}/scan_0001_workflow.json"``.

Show the maps
-------------

.. code-block:: bash

    silx view processed/scan_0001_xrf.h5

Open ``/1.1/regrid/results/parameters`` and select ``Ta_L``.
The map shows the Siemens star.

Workflow inputs
---------------

.. list-table::
    :header-rows: 1

    * - Node:input
      - Value for ``scan_0001.nxs``
      - Description
    * - ``convert:filename``
      - ``scan_0001.nxs``
      - FlyScan NeXus file.
    * - ``convert:output_filename``
      - ``processed/scan_0001_bliss.h5``
      - New Bliss scan that refers to the NeXus file.
    * - ``sum:detector_names``
      - ``["xmap1_det00", "xmap1_det01"]``
      - XRF detectors to sum. The detector of the NeXus dataset ``xmap1channel00`` is ``xmap1_det00``.
    * - ``sum:detector_normalization_template``
      - ``0.1*<...>``
      - Dead time correction to 100 ms of live time. ``{}`` is the detector name.
        See :doc:`../explanations/deadtime`.
    * - ``sum:output_root_uri``
      - ``processed/scan_0001_xrf.h5::/1.1``
      - HDF5 group for the XRF results.
    * - ``fit:config``
      - ``pymca_example.cfg``
      - PyMca configuration.
    * - ``fit:energy_name``
      - ``energy``
      - Beam energy. ``convert`` saves the monochromator energy as ``energy``. Do not change.
    * - ``norm:counter_name``
      - ``i0``
      - Normalization counter (I0).
    * - ``regrid:positioners``
      - ``["samx", "samz"]``
      - Axes of the map. The positioner of the NeXus dataset ``samx_dataset`` is ``samx``.

The inputs of all tasks are in :doc:`../reference/tasks`.

Process a FlyScan file of a beamline
------------------------------------

Fit the detector calibration on the sum spectrum of the file:

.. code-block:: bash

    python make_pymca_config.py pymca_ta.cfg /path/to/flyscan.nxs

Then change the inputs of the workflow: the file names, the detectors, the real time in the dead time correction, the counter and the axes.
