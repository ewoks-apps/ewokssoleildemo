# ewokssoleildemo

Ewoks workflows for the SOLEIL FlyScan test bench.
They make X-ray fluorescence maps from FlyScan NeXus files.

## Getting started

```bash
pip install -e ".[job]"
python doc/_ext/make_pymca_config.py pymca_example.cfg
python scripts/make_flyscan_data.py pymca_example.cfg scan_0001.nxs parameters.json
python -m ewokssoleildemo.apps.xrfmap scan_0001.nxs parameters.json processed
```

`python -m ewokssoleildemo.apps.xrfmap` and all scripts in `scripts/` have a `--help` option.

## Documentation

https://ewokssoleildemo.readthedocs.io/
