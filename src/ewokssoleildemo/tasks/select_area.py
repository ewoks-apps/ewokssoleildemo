"""Select the next scan area from an XRF map."""

import h5py
import numpy
from ewokscore import Task
from ewokscore.model import BaseInputModel
from ewokscore.model import BaseOutputModel
from ewoksfluo.io.hdf5 import split_h5uri
from pydantic import Field
from scipy import ndimage


class Inputs(BaseInputModel):
    xrf_results_uri: str = Field(
        description="Regridded XRF results.",
        examples=["/processed/scan_0001_xrf.h5::/1.1/regrid/results"],
    )
    signal: str = Field(description="Element map to select from.", examples=["Ta_L"])
    percentile: float = Field(
        default=90, description="Select the map points above this percentile."
    )
    zoom: float = Field(default=2, description="Pixel size reduction factor.")


class Outputs(BaseOutputModel):
    sample_area: list[float] = Field(
        description="Next scan area: start fast axis, start slow axis, width, height.",
        examples=[[3.5, 2.0, 1.5, 1.0]],
    )
    pixel_size: float = Field(description="Next pixel size.", examples=[0.05])


class SelectArea(Task, input_model=Inputs, output_model=Outputs):
    """Select the largest region with a high signal and scan it with smaller pixels."""

    def run(self):
        filename, h5path = split_h5uri(self.inputs.xrf_results_uri)
        with h5py.File(filename, "r") as h5file:
            parameters = h5file[h5path]["parameters"]
            slow_axis, fast_axis = parameters.attrs["axes"]
            image = parameters[self.inputs.signal][()]
            fast = parameters[fast_axis][()]
            slow = parameters[slow_axis][()]

        mask = image > numpy.nanpercentile(image, self.inputs.percentile)
        mask = ndimage.binary_opening(mask, iterations=2)
        labels, nlabels = ndimage.label(mask)
        if not nlabels:
            raise RuntimeError(f"No region found in {self.inputs.signal!r}")
        sizes = ndimage.sum(mask, labels, range(1, nlabels + 1))
        largest = int(numpy.argmax(sizes))
        slow_slice, fast_slice = ndimage.find_objects(labels)[largest]

        fast_range = fast[fast_slice]
        slow_range = slow[slow_slice]
        self.outputs.sample_area = [
            float(fast_range[0]),
            float(slow_range[0]),
            float(fast_range[-1] - fast_range[0]),
            float(slow_range[-1] - slow_range[0]),
        ]
        self.outputs.pixel_size = float(abs(fast[1] - fast[0]) / self.inputs.zoom)
