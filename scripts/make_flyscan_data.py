"""Create a FlyScan NeXus file with simulated XRF spectra of a Ta Siemens star.

Also create the processing parameters for this file.
The NeXus file has the layout of the files from the SOLEIL DataMerger.
The spectra use the lines and the detector calibration of the PyMca configuration.
"""

import argparse
import json

import h5py
import numpy
from ewoksfluo.tasks.example_data.deadtime import apply_dualchannel_signal_processing
from PyMca5.PyMcaIO.ConfigDict import ConfigDict
from PyMca5.PyMcaPhysics.xrf.ClassMcaTheory import McaTheory


def main(pymca_config: str, nxs_filename: str, parameters_filename: str) -> None:
    fast = numpy.linspace(0, 10, 80)  # samx
    slow = numpy.linspace(0, 8, 60)  # samz
    samx, samz = numpy.meshgrid(fast, slow)
    ta = _siemens_star(samx, samz)

    counts = {
        "Ta L": 1000 * ta,
        "Si K": numpy.full(ta.shape, 300.0),
        "Ar K": numpy.full(ta.shape, 50.0),
        "Scatter Peak000": numpy.full(ta.shape, 500.0),
        "Scatter Compton000": numpy.full(ta.shape, 500.0),
    }
    spectra = 0
    for name, profile in _line_profiles(pymca_config).items():
        spectra = spectra + counts[name][..., None] * profile

    numpy.random.seed(0)
    with h5py.File(nxs_filename, "w") as nxroot:
        entry = nxroot.create_group("flyscan_00001")
        entry.attrs["NX_class"] = "NXentry"
        mono = entry.create_group("BEAMLINE/monochromator")
        mono.attrs["NX_class"] = "NXmonochromator"
        mono["energy"] = 12.0
        mono["energy"].attrs["units"] = "keV"
        scan_data = entry.create_group("scan_data")
        scan_data.attrs["NX_class"] = "NXdata"
        for channel in ("00", "01"):
            mca = apply_dualchannel_signal_processing(
                spectra, max_dt_slow=30, elapsed_time=_ELAPSED_TIME
            )
            scan_data[f"xmap1channel{channel}"] = mca["spectrum"]
            scan_data[f"xmap1icr{channel}"] = mca["trigger_count_rate"]
            scan_data[f"xmap1ocr{channel}"] = mca["event_count_rate"]
            scan_data[f"xmap1livetime{channel}"] = mca["trigger_live_time"]
            scan_data[f"xmap1realtime{channel}"] = mca["elapsed_time"]
        scan_data["samx_dataset"] = samx
        scan_data["samz_dataset"] = samz
        scan_data["i0"] = numpy.random.poisson(10000, ta.shape)

    parameters = {
        "pymca_config": pymca_config,
        "detector_names": ["xmap1_det00", "xmap1_det01"],
        "counter_name": "i0",
        "reference_time": _ELAPSED_TIME,
        "positioners": ["samx", "samz"],
        "signal": "Ta_L",
    }
    with open(parameters_filename, "w") as f:
        json.dump(parameters, f, indent=2)


_ELAPSED_TIME = 0.1


def _siemens_star(x: numpy.ndarray, y: numpy.ndarray) -> numpy.ndarray:
    """Ta fraction: 8 spokes, thicker in the center."""
    x = x - x.mean()
    y = y - y.mean()
    angle = numpy.arctan2(y, x)
    radius = numpy.hypot(x, y)
    spokes = numpy.sin(8 * angle) > 0
    return spokes * (radius < 3.5) * (1 + 2 * numpy.exp(-(radius**2) / 2))


def _line_profiles(pymca_config: str) -> dict[str, numpy.ndarray]:
    """Spectrum of each line group, normalized to an area of 1."""
    cfg = ConfigDict()
    cfg.read(pymca_config)
    mca_theory = McaTheory()
    mca_theory.configure(cfg)
    x = numpy.arange(2048)
    mca_theory.config["fit"]["use_limit"] = 0
    mca_theory.setData(x=x, y=numpy.zeros(x.size))
    mca_theory.config["fit"]["linearfitflag"] = 1
    mca_theory.enableOptimizedLinearFit()
    mca_theory.estimate()
    parameters = numpy.asarray(mca_theory.parameters)
    return {
        name: mca_theory.linearMcaTheoryDerivative(parameters, i, x)
        for i, name in enumerate(mca_theory.PARAMETERS)
        if i >= mca_theory.NGLOBAL
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pymca_config", help="PyMca configuration file")
    parser.add_argument("nxs_filename", help="FlyScan NeXus file to write")
    parser.add_argument(
        "parameters_filename", help="JSON file with the processing parameters to write"
    )
    args = parser.parse_args()
    main(args.pymca_config, args.nxs_filename, args.parameters_filename)
