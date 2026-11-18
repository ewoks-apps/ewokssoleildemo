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

Load a workflow by name with ``load_options={"representation": "json_module"}``.
``xrfmap_arguments`` adds this option.
