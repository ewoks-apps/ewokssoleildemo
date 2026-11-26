Scenario 4: select the next scan area
=====================================

The workflow ``xrfmap_flyscan_select_area`` is the workflow ``xrfmap_flyscan`` with the task ``SelectArea`` at the end.
It selects the area and the pixel size of the next scan from an element map.

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

Select an area
--------------

Use the command of :doc:`process_file` with the new workflow name and one more input:

.. code-block:: bash

    ewoks execute xrfmap_flyscan_select_area --workflow-module ewokssoleildemo.workflows \
        -pn convert:filename=$PWD/scan_0001.nxs \
        -pn convert:output_filename=$PWD/processed/scan_0001_bliss.h5 \
        -pn 'sum:detector_names=["xmap1_det00","xmap1_det01"]' \
        -pn 'sum:detector_normalization_template=0.1*<instrument/{}/trigger_count_rate>/(<instrument/{}/elapsed_time>*<instrument/{}/event_count_rate>)' \
        -pn sum:output_root_uri=$PWD/processed/scan_0001_xrf.h5::/1.1 \
        -pn fit:config=$PWD/pymca_example.cfg \
        -pn fit:energy_name=energy \
        -pn norm:counter_name=i0 \
        -pn 'regrid:positioners=["samx","samz"]' \
        -pn select:signal=Ta_L \
        --outputs end --merge-outputs

``select:signal`` is the element map for the selection. ``Ta_L`` is a fit result: the L lines of Ta.
To check the inputs first, replace ``ewoks execute`` by ``ewoks show``, and remove ``--outputs end --merge-outputs``.
``--outputs end --merge-outputs`` shows the outputs of the last node:

.. code-block:: python

    {"pixel_size": 0.0633, "sample_area": [3.03, 4.48, 1.14, 0.95]}

* ``sample_area``: start of the fast axis, start of the slow axis, width and height of the new area.
* ``pixel_size``: the new pixel size.

The units are the units of the positioners. ``samx`` is the fast axis.

From Python, ``execute_graph`` returns the result:

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
        {"id": "select", "name": "signal", "value": "Ta_L"},
    ]
    result = execute_graph(
        "xrfmap_flyscan_select_area",
        inputs=inputs,
        load_options={"root_module": "ewokssoleildemo.workflows"},
    )

Select an area on a worker
--------------------------

Start a worker. See :doc:`../howtoguides/worker`. Then submit the workflow:

.. code-block:: bash

    export EWOKS_CONFIG_URI=/path/to/config_redis.py

    ewoksjob submit xrfmap_flyscan_select_area --workflow-module ewokssoleildemo.workflows --load-remote \
        -pn convert:filename=$PWD/scan_0001.nxs \
        -pn convert:output_filename=$PWD/processed/scan_0001_bliss.h5 \
        -pn 'sum:detector_names=["xmap1_det00","xmap1_det01"]' \
        -pn 'sum:detector_normalization_template=0.1*<instrument/{}/trigger_count_rate>/(<instrument/{}/elapsed_time>*<instrument/{}/event_count_rate>)' \
        -pn sum:output_root_uri=$PWD/processed/scan_0001_xrf.h5::/1.1 \
        -pn fit:config=$PWD/pymca_example.cfg \
        -pn fit:energy_name=energy \
        -pn norm:counter_name=i0 \
        -pn 'regrid:positioners=["samx","samz"]' \
        -pn select:signal=Ta_L \
        --outputs end --merge-outputs --wait 600

To check the inputs first, replace ``ewoksjob submit`` by ``ewoks show``, and remove ``--load-remote``, ``--outputs end --merge-outputs`` and ``--wait 600``.
``ewoks show`` needs *ewokssoleildemo*.

From Python, ``future.result()`` returns the result:

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
        {"id": "select", "name": "signal", "value": "Ta_L"},
    ]
    future = submit(
        args=("xrfmap_flyscan_select_area",),
        kwargs={
            "inputs": inputs,
            "load_options": {"root_module": "ewokssoleildemo.workflows"},
        },
    )
    result = future.result()

Set ``EWOKS_CONFIG_URI`` before you start Python.

How ``SelectArea`` selects the area
-----------------------------------

1. It selects the points of the element map above the 90th percentile.
2. It removes the regions that are less than approximately 5 points wide.
3. It finds the largest region of the remaining points.
4. The new area is the bounding box of this region.
   The fast axis is the positioner that moves between consecutive scan points.
5. The new pixel size is the scan step of the fast axis divided by 2.

To change the percentile or the divisor of the pixel size, add inputs for the node ``select``,
for example ``-pn select:percentile=95 -pn select:zoom=4``.

Repeat on the test bench
------------------------

:download:`testbench_select_area.py <../../scripts/testbench_select_area.py>` repeats these steps:

1. It starts a FlyScan scan.
2. It submits the workflow ``xrfmap_flyscan_select_area`` to an ewoksjob worker and waits for the result.
3. It writes ``sample_area`` and ``pixel_size_in_um`` in the easy-config parameters of the FlyScan configuration.

Start a worker. See :doc:`../howtoguides/worker`. Then start the scans:

.. code-block:: bash

    EWOKS_CONFIG_URI=/path/to/config_redis.py \
        python testbench_select_area.py my_flyscan_config pymca_ta.cfg processed --nscans 3

The first argument is the name of the FlyScan configuration.
``pymca_ta.cfg`` is a PyMca configuration for the test bench. See :doc:`../howtoguides/pymca_config`.
Use ``--server`` to change the Tango device name of the FlyScan server.

The positions in the NeXus file are in µm. The easy-config has the start of the area in mm.
The script divides the start of the area by 1000.

The script needs ``ewoksjob[redis]`` (or ``ewoksjob[sql]``) and the SOLEIL ``fs`` library. It does not need *ewokssoleildemo*.
This script is not tested. It needs the FlyScan Tango devices and the ``fs`` library.

.. literalinclude:: ../../scripts/testbench_select_area.py
    :language: python
    :caption: testbench_select_area.py
