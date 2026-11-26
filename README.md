# ewokssoleildemo

Ewoks workflows for the SOLEIL FlyScan test bench.
They make X-ray fluorescence maps from FlyScan NeXus files.

## Getting started

```bash
pip install "ewokssoleildemo[job]"
```

Then process a FlyScan file with `ewoks execute xrfmap_flyscan --workflow-module ewokssoleildemo.workflows`.
To check the inputs first, use `ewoks show` with the same options.
See the tutorial "Scenario 1: process a FlyScan file" in the documentation.

## Documentation

https://ewokssoleildemo.readthedocs.io/
