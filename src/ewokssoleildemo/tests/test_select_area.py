import h5py
import numpy
import pytest

from ewokssoleildemo.tasks.select_area import SelectArea


@pytest.mark.parametrize("axes", [["samx", "samz"], ["samz", "samx"]])
def test_select_area(tmp_path, axes):
    fast = numpy.linspace(0, 10, 101)  # samx
    slow = numpy.linspace(0, 7, 71)  # samz
    image = numpy.zeros((fast.size, slow.size))
    image[30:60, 20:40] = 100
    if axes[0] == "samz":
        image = image.T
    samz, samx = numpy.meshgrid(slow, fast, indexing="ij")
    filename = str(tmp_path / "xrf.h5")
    with h5py.File(filename, "w") as root:
        root["1.1/measurement/samx"] = samx.flatten()
        root["1.1/measurement/samz"] = samz.flatten()
        parameters = root.create_group("1.1/regrid/results/parameters")
        parameters.attrs["axes"] = axes
        parameters["Ta_L"] = image
        parameters["samx"] = fast
        parameters["samz"] = slow

    task = SelectArea(
        inputs={
            "xrf_results_uri": f"{filename}::/1.1/regrid/results",
            "bliss_scan_uri": f"{filename}::/1.1",
            "signal": "Ta_L",
        }
    )
    task.execute()

    numpy.testing.assert_allclose(task.outputs.sample_area, [3, 2, 2.9, 1.9])
    numpy.testing.assert_allclose(task.outputs.pixel_size, 0.05)
