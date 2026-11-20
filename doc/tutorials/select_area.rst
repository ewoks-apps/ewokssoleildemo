Scenario A.2: select the next scan area
=======================================

Scenario A.2 repeats these steps:

1. FlyScan scans an area.
2. A workflow makes the element maps and selects a new area (step 5a).
3. The next FlyScan scan uses the new area and smaller pixels.

The workflow ``ewokssoleildemo.workflows.xrfmap_flyscan_select_area`` does step 2.
It is the workflow of :doc:`xrfmap`, with the task ``SelectArea`` at the end.
Make the example data of :doc:`xrfmap` first.

Select an area
--------------

Use the ``inputs`` of :doc:`xrfmap`, and add the element map for the selection.
``Ta_L`` is a fit result: the L lines of Ta.

.. code-block:: python

    inputs.append({"id": "select", "name": "signal", "value": "Ta_L"})
    result = execute_graph(
        "ewokssoleildemo.workflows.xrfmap_flyscan_select_area",
        inputs=inputs,
        load_options={"representation": "json_module"},
    )

The result for the example data:

.. code-block:: python

    {"sample_area": [3.03, 4.48, 1.14, 0.95], "pixel_size": 0.0635}

* ``sample_area``: start of the fast axis, start of the slow axis, width and height of the new area.
* ``pixel_size``: the new pixel size.

The units are the units of the positioners.

The same from the command line.
The parameter ``signal`` in ``parameters.json`` gives the element map.

.. code-block:: bash

    python -m ewokssoleildemo.apps.xrfmap scan_0001.nxs parameters.json processed --select-area

With a worker, add ``--submit --wait``.
The ``--wait`` option prints the result of the job.

How ``SelectArea`` selects the area
-----------------------------------

1. It selects the points of the element map above the 90th percentile.
2. It removes the regions that are less than approximately 5 points wide.
3. It finds the largest region of the remaining points.
4. The new area is the bounding box of this region.
   The fast axis is the positioner that moves between consecutive scan points.
5. The new pixel size is the old pixel size divided by 2.

The divisor of the pixel size is the input ``zoom``.
To change the percentile or ``zoom``, add inputs for the node ``select``:

.. code-block:: python

    inputs += [
        {"id": "select", "name": "percentile", "value": 95},
        {"id": "select", "name": "zoom", "value": 4},
    ]

Repeat on the test bench
------------------------

``scripts/testbench_a2.py`` repeats the steps of scenario A.2:

1. It starts a FlyScan scan.
2. It submits ``WORKFLOW_SELECT_AREA`` and waits for the result.
3. It writes ``sample_area`` and ``pixel_size_in_um`` in the easy-config parameters of the FlyScan configuration.

.. code-block:: bash

    EWOKS_CONFIG_URI=scripts/config_redis.py \
        python scripts/testbench_a2.py my_flyscan_config parameters.json processed --nscans 3

The first argument is the name of the FlyScan configuration.
Use ``--server`` and ``--merger`` to change the Tango device names.

This script is not tested. It needs the FlyScan Tango devices and the SOLEIL ``fs`` library.
Like ``scripts/testbench_a1.py``, it does not need *ewokssoleildemo*. See :doc:`xrfmap`.

.. warning::

    The script writes the workflow results to the easy-config without unit conversion.
    The easy-config description gives the start of the area in mm, but scan 17760 uses it in µm,
    the unit of the PI positions. SOLEIL must confirm this.

.. literalinclude:: ../../scripts/testbench_a2.py
    :language: python
    :caption: scripts/testbench_a2.py

The workflows process complete scans. They do not show the maps during the scan.
