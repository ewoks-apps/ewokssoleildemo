ewokssoleildemo |version|
=========================

*ewokssoleildemo* makes X-ray fluorescence (XRF) maps from the NeXus files of the SOLEIL FlyScan system.
It is a demonstration of `Ewoks <https://ewoks.esrf.fr>`_ for SOLEIL.

The workflows use the XRF tasks of `ewoksfluo <https://ewoksfluo.readthedocs.io>`_.
They can run in one Python process, or on an `ewoksjob <https://ewoksjob.readthedocs.io>`_ worker.

*ewokssoleildemo* has been developed by the `Software group <http://www.esrf.eu/Instrumentation/software>`_
of the `European Synchrotron <https://www.esrf.eu/>`_.

.. admonition:: Quick Start

   .. code-block:: bash

      git clone https://gitlab.esrf.fr/workflow/ewoksapps/ewokssoleildemo.git
      cd ewokssoleildemo
      pip install -e ".[job]"
      python doc/_ext/make_pymca_config.py pymca_example.cfg
      python scripts/make_flyscan_data.py pymca_example.cfg scan_0001.nxs parameters.json
      python -m ewokssoleildemo.apps.xrfmap scan_0001.nxs parameters.json processed

.. toctree::
   :hidden:

   tutorials
   howtoguides
   explanations
   reference
