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
    bliss_scan_uri: str = Field(
        description="Bliss scan with the positions of the map axes.",
        examples=["/processed/scan_0001_xrf.h5::/1.1"],
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

    def run(self) -> None:
        filename, h5path = split_h5uri(self.inputs.xrf_results_uri)
        with h5py.File(filename, "r") as h5file:
            parameters = h5file[h5path]["parameters"]
            axes = list(parameters.attrs["axes"])
            image = parameters[self.inputs.signal][()]
            grid = [parameters[axis][()] for axis in axes]

        filename, h5path = split_h5uri(self.inputs.bliss_scan_uri)
        with h5py.File(filename, "r") as h5file:
            measurement = h5file[h5path]["measurement"]
            ifast, step = _fast_axis([measurement[axis][()] for axis in axes])

        mask = image > numpy.nanpercentile(image, self.inputs.percentile)
        mask = ndimage.binary_opening(mask, iterations=2)
        labels, nlabels = ndimage.label(mask)
        if not nlabels:
            raise RuntimeError(f"No region found in {self.inputs.signal!r}")
        sizes = ndimage.sum(mask, labels, range(1, nlabels + 1))
        largest = int(numpy.argmax(sizes))
        slices = ndimage.find_objects(labels)[largest]

        fast_range = grid[ifast][slices[ifast]]
        slow_range = grid[1 - ifast][slices[1 - ifast]]
        self.outputs.sample_area = [
            float(fast_range[0]),
            float(slow_range[0]),
            float(fast_range[-1] - fast_range[0]),
            float(slow_range[-1] - slow_range[0]),
        ]
        self.outputs.pixel_size = float(step / self.inputs.zoom)


def _fast_axis(positions: list[numpy.ndarray]) -> tuple[int, float]:
    """Index and scan step of the axis that moves between consecutive scan points."""
    steps = [numpy.median(numpy.abs(numpy.diff(values))) for values in positions]
    ifast = int(
        numpy.argmax([step / numpy.ptp(v) for step, v in zip(steps, positions)])
    )
    return ifast, float(steps[ifast])
