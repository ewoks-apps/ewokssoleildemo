Ewoks Workflows
===============

.. list-table::
    :header-rows: 1

    * - Workflow name
      - Tasks
    * - ``ewokssoleildemo.workflows.xrfmap_flyscan``
      - FlyScan to Bliss → sum spectra → fit → normalize → raw counters → regrid
    * - ``ewokssoleildemo.workflows.xrfmap_flyscan_select_area``
      - The same tasks → select area

To load a workflow by its short name, for example ``xrfmap_flyscan``, give the Python package of the workflows:

On the command line, use ``--workflow-module``:

.. code-block:: bash

    ewoks execute xrfmap_flyscan --workflow-module ewokssoleildemo.workflows -pn ...

In Python, use ``root_module``:

.. code-block:: python

    execute_graph(
        "xrfmap_flyscan",
        inputs=inputs,
        load_options={"root_module": "ewokssoleildemo.workflows"},
    )
