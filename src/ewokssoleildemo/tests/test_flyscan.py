import h5py
import numpy

from ewokssoleildemo.tasks.flyscan import FlyscanToBliss


def test_flyscan_to_bliss(tmp_path):
    nrows, ncols, nchan = 3, 4, 5
    spectra = numpy.arange(nrows * ncols * nchan).reshape(nrows, ncols, nchan)
    samx = numpy.tile(numpy.arange(ncols, dtype=float), (nrows, 1)) + 5
    filename = str(tmp_path / "flyscan.nxs")
    with h5py.File(filename, "w") as nxroot:
        entry = nxroot.create_group("flyscan_1")
        entry.attrs["NX_class"] = "NXentry"
        mono = entry.create_group("BEAMLINE/Monochromator")
        mono.attrs["NX_class"] = "NXmonochromator"
        mono["energy"] = 12.0
        mono["energy"].attrs["units"] = "keV"
        scan_data = entry.create_group("scan_data")
        scan_data["xmap1channel00"] = spectra
        scan_data["xmap1icr00"] = numpy.ones((nrows, ncols))
        scan_data["samx_dataset"] = samx
        scan_data["i0"] = numpy.ones((nrows, ncols))

    task = FlyscanToBliss(
        inputs={"filename": filename, "output_filename": str(tmp_path / "bliss.h5")}
    )
    task.execute()

    bliss_filename, scan_name = task.outputs.bliss_scan_uri.split("::/")
    with h5py.File(bliss_filename, "r") as root:
        scan = root[scan_name]
        numpy.testing.assert_array_equal(
            scan["measurement/xmap1_det00"][()], spectra.reshape(-1, nchan)
        )
        numpy.testing.assert_array_equal(scan["measurement/samx"][()], samx.flatten())
        assert scan["instrument/xmap1_det00/trigger_count_rate"].shape == (12,)
        assert scan["measurement/i0"].shape == (12,)
        assert scan["instrument/positioners_start/samx"][()] == 5
        assert scan["instrument/positioners_start/energy"][()] == 12
