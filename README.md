# ewokssoleildemo

Ewoks workflows for the SOLEIL FlyScan test bench.
They make X-ray fluorescence maps from FlyScan NeXus files.

## Getting started

```bash
pip install "ewokssoleildemo[job]"
```

Show the inputs of the workflow:

```bash
ewoks show xrfmap_flyscan --workflow-module ewokssoleildemo.workflows
```

Process a FlyScan file. Give the inputs with `-pn NODE:NAME=VALUE`:

```bash
ewoks execute xrfmap_flyscan --workflow-module ewokssoleildemo.workflows -pn ...
```

See the tutorial "Scenario 1: process a FlyScan file" in the documentation.

## Documentation

https://ewokssoleildemo.readthedocs.io/
