Scenario 3: process a scan on the test bench
============================================

On the test bench, the processing starts at the end of the scan:

1. FlyScan scans the sample.
2. The DataMerger, a SOLEIL Tango device, writes the scan data to one NeXus file.
3. A client submits the workflow ``xrfmap_flyscan`` for this file to an ewoksjob worker.

:download:`testbench_process_scan.py <../../scripts/testbench_process_scan.py>` is the client.
It sends a FlyScan configuration file to the FlyScan server and starts the scan.
At the end of the scan, it reads the NeXus file name from the DataMerger and submits the workflow.

Make a PyMca configuration
--------------------------

Download :download:`make_pymca_config.py <../_ext/make_pymca_config.py>`.
Fit the detector calibration on the sum spectrum of a NeXus file of the test bench:

.. code-block:: bash

    python make_pymca_config.py pymca_ta.cfg /path/to/flyscan.nxs

The workflow uses ``pymca_ta.cfg`` for the XRF fit. See :doc:`../howtoguides/pymca_config`.

Start the scan
--------------

Start a worker. See :doc:`../howtoguides/worker`. Then start the scan:

.. code-block:: bash

    EWOKS_CONFIG_URI=/path/to/config_redis.py \
        python testbench_process_scan.py scan.cfg pymca_ta.cfg processed

* ``scan.cfg``: the FlyScan configuration file.
* ``pymca_ta.cfg``: the PyMca configuration.
* ``processed``: the directory for the results.

Use ``--server`` to change the Tango device name of the FlyScan server (default: ``flyscan/core/server.1``).

The script needs ``ewoksjob[redis]`` (or ``ewoksjob[sql]``) and PyTango. It does not need *ewokssoleildemo*.
The script sets ``convert:filename`` to the NeXus file of the DataMerger.
The other workflow inputs are the inputs of :doc:`process_file`. For other detectors, counters or axes, change the list ``inputs`` in the script.
The client host needs access to the Tango devices. For a client on a different host than the worker, see :doc:`worker`.

This script is not tested. It needs the FlyScan Tango devices.

.. literalinclude:: ../../scripts/testbench_process_scan.py
    :language: python
    :caption: testbench_process_scan.py

The workflow processes the complete scan. It does not show the maps during the scan.
