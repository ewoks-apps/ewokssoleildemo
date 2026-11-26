Dead time correction
====================

The XIA electronics give these values for each point:

* real time :math:`t_{\mathrm{real}}`
* input count rate :math:`\mathrm{ICR}`
* output count rate :math:`\mathrm{OCR}`

The ``livetime`` dataset of the NeXus file is the trigger live time.
The trigger live time does not include all the dead time of the spectrum. The workflows do not use it.

The live time of the spectrum is:

.. math::

    t_{\mathrm{live}} = t_{\mathrm{real}} \frac{\mathrm{OCR}}{\mathrm{ICR}}

Before the sum of the detectors, the workflows multiply each spectrum by the factor :math:`f`:

.. math::

    f = \frac{t_{\mathrm{ref}}}{t_{\mathrm{live}}}
      = \frac{t_{\mathrm{ref}} \, \mathrm{ICR}}{t_{\mathrm{real}} \, \mathrm{OCR}}

The workflow input ``sum:detector_normalization_template`` gives :math:`f`.
:math:`t_{\mathrm{ref}}` is the number at the start of this input.
For the example data of :doc:`../tutorials/process_file`, :math:`t_{\mathrm{ref}} = 0.1` s: all spectra have the counts for 100 ms of live time.
