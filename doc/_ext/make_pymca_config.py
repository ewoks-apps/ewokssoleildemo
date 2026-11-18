"""Create an example PyMca configuration: Ta L, Si K and Ar K lines.

Also a Sphinx extension that creates this configuration in ``_generated/``.
"""

import argparse
import os
import re
from typing import TYPE_CHECKING
from typing import Optional

import h5py
import numpy
from ewoksfluo.tasks.example_data.xrf_spectra import _get_configuration
from ewoksfluo.xrffit.pymca_config import pymca_configdict_from_model
from ewoksfluo.xrffit.pymca_config import pymca_configdict_to_file
from PyMca5.PyMcaPhysics.xrf import ClassMcaTheory

if TYPE_CHECKING:
    from sphinx.application import Sphinx


def main(cfg_filename: str, nxs_filename: Optional[str] = None) -> None:
    model = _get_configuration(
        peaks={"Ta": "L", "Si": "K", "Ar": "K"},
        xmin=100,
        xmax=1350,
        energy=12,
        elements=["Ta", "Si"],
    )
    cfg = pymca_configdict_from_model(model)

    if nxs_filename:
        calibration = _fit_calibration(cfg, _sum_spectrum(nxs_filename))
        print(calibration)
    else:
        calibration = _CALIBRATION
    for key, value in calibration.items():
        cfg["detector"][key] = value
        cfg["detector"][f"fixed{key}"] = 1

    pymca_configdict_to_file(cfg, cfg_filename)


def setup(app: "Sphinx") -> dict:
    app.connect("builder-inited", _make_doc_config)
    return {"parallel_read_safe": True, "parallel_write_safe": True}


def _make_doc_config(app: "Sphinx") -> None:
    dirname = os.path.join(app.srcdir, "_generated")
    os.makedirs(dirname, exist_ok=True)
    main(os.path.join(dirname, "pymca_example.cfg"))


_CALIBRATION = {"zero": 0.0, "gain": 0.01, "noise": 0.1, "fano": 0.114}


def _fit_calibration(cfg: dict, spectrum: numpy.ndarray) -> dict:
    for key in _CALIBRATION:
        cfg["detector"][f"fixed{key}"] = 0
    mcafit = ClassMcaTheory.McaTheory()
    mcafit.configure(cfg)
    mcafit.setData(
        numpy.arange(spectrum.size),
        spectrum,
        xmin=cfg["fit"]["xmin"],
        xmax=cfg["fit"]["xmax"],
    )
    mcafit.estimate()
    _, result = mcafit.startfit(digest=1)
    return {
        key: float(result["fittedpar"][result["parameters"].index(key.capitalize())])
        for key in _CALIBRATION
    }


_SPECTRA = re.compile(r"^xmap\d+channel\d+$")


def _sum_spectrum(nxs_filename: str) -> numpy.ndarray:
    """Sum of all spectra of all XIA channels."""
    with h5py.File(nxs_filename, "r") as nxroot:
        entry = next(iter(nxroot.values()))
        spectrum = 0
        for name, dset in entry["scan_data"].items():
            if not _SPECTRA.match(name):
                continue
            for row in range(dset.shape[0]):
                spectrum = spectrum + dset[row].sum(axis=0, dtype=numpy.float64)
    return spectrum


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cfg_filename", help="PyMca configuration file to write")
    parser.add_argument(
        "nxs_filename",
        nargs="?",
        help="Fit the detector calibration on the sum spectrum of this FlyScan NeXus file",
    )
    args = parser.parse_args()
    main(args.cfg_filename, args.nxs_filename)
