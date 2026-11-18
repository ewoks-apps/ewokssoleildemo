FlyScan data
============

The DataMerger, a SOLEIL Tango device, writes all scan data in the ``NXdata`` group ``scan_data``.
Each dataset has the shape of the map: (lines, points per line).
The XRF spectra have one more dimension: (lines, points per line, channels).

The ewoksfluo tasks read Bliss scans. A Bliss scan has one point for each map pixel.
The task ``FlyscanToBliss`` writes a Bliss scan that refers to the NeXus file.
The datasets are HDF5 virtual datasets. The spectra are not copied.
Do not move the NeXus file after the processing.

.. list-table::
    :header-rows: 1

    * - NeXus dataset in ``scan_data``
      - Bliss dataset in ``instrument``
    * - ``xmap1channel00``
      - ``xmap1_det00/data``
    * - ``xmap1realtime00``
      - ``xmap1_det00/elapsed_time``
    * - ``xmap1icr00``
      - ``xmap1_det00/trigger_count_rate``
    * - ``xmap1ocr00``
      - ``xmap1_det00/event_count_rate``
    * - ``xmap1livetime00``
      - ``xmap1_det00/trigger_live_time``
    * - ``samx_dataset``
      - ``samx/value``
    * - ``i0``
      - ``i0/data``

The task also writes:

* ``instrument/positioners_start``: the first position of each axis, and the energy of the monochromator.
* ``measurement``: links to all datasets.
