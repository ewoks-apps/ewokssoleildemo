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

      pip install "ewokssoleildemo[job]"

   Then process a FlyScan file: see :doc:`tutorials/process_file`.

.. toctree::
   :hidden:

   tutorials
   howtoguides
   explanations
   reference
