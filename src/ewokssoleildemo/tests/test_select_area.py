import h5py
import numpy

from ewokssoleildemo.tasks.select_area import SelectArea


def test_select_area(tmp_path):
    fast = numpy.linspace(0, 10, 101)
    slow = numpy.linspace(0, 7, 71)
    image = numpy.zeros((slow.size, fast.size))
    image[20:40, 30:60] = 100
    filename = str(tmp_path / "xrf.h5")
    with h5py.File(filename, "w") as root:
        parameters = root.create_group("1.1/regrid/results/parameters")
        parameters.attrs["axes"] = ["samz", "samx"]
        parameters["Ta_L"] = image
        parameters["samx"] = fast
        parameters["samz"] = slow

    task = SelectArea(
        inputs={"xrf_results_uri": f"{filename}::/1.1/regrid/results", "signal": "Ta_L"}
    )
    task.execute()

    numpy.testing.assert_allclose(task.outputs.sample_area, [3, 2, 2.9, 1.9])
    numpy.testing.assert_allclose(task.outputs.pixel_size, 0.05)
