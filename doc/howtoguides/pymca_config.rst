Make a PyMca configuration
==========================

The fit task needs a PyMca configuration file.
:download:`make_pymca_config.py <../_ext/make_pymca_config.py>` makes an example configuration: the Ta L, Si K and Ar K lines.

.. code-block:: bash

    python make_pymca_config.py pymca_example.cfg

The result is :download:`pymca_example.cfg <../_generated/pymca_example.cfg>`.

To fit the detector calibration on the sum spectrum of a FlyScan NeXus file:

.. code-block:: bash

    python make_pymca_config.py pymca_ta.cfg /path/to/flyscan.nxs

The script uses the sum of all XIA channels (``xmap*channel*``) and the monochromator energy of the file.
For a different sample, change the elements in the script, or edit the configuration with PyMca.
The fit task uses the beam energy of the scan, not the energy in the configuration.
