"""Read SOLEIL FlyScan NeXus files with Ewoks tasks for Bliss scans."""

import os
import re
from typing import Optional

import h5py
from ewokscore import Task
from ewokscore.model import BaseInputModel
from ewokscore.model import BaseOutputModel
from pydantic import Field


class Inputs(BaseInputModel):
    filename: str = Field(
        description="FlyScan NeXus file written by the DataMerger.",
        examples=["/data/scan_0001.nxs"],
    )
    output_filename: str = Field(
        description="HDF5 file for the Bliss scan. The scan data are virtual "
        "datasets that refer to the FlyScan NeXus file.",
        examples=["/processed/scan_0001_bliss.h5"],
    )
    scan_number: int = Field(default=1, description="Scan number in the output file.")
    overwrite: bool = Field(default=True, description="Overwrite an existing scan.")


class Outputs(BaseOutputModel):
    bliss_scan_uri: str = Field(
        description="Bliss scan URI.",
        examples=["/processed/scan_0001_bliss.h5::/1.1"],
    )


class FlyscanToBliss(Task, input_model=Inputs, output_model=Outputs):
    """Expose a FlyScan map as a Bliss scan with one point per pixel."""

    def run(self):
        filename = os.path.abspath(self.inputs.filename)
        output_filename = os.path.abspath(self.inputs.output_filename)
        scan_name = f"{self.inputs.scan_number}.1"

        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
        with h5py.File(filename, "r") as nxroot:
            with h5py.File(output_filename, "a") as bliss_root:
                if scan_name in bliss_root:
                    if not self.inputs.overwrite:
                        raise FileExistsError(f"{output_filename}::/{scan_name}")
                    del bliss_root[scan_name]
                bliss_root.attrs["NX_class"] = "NXroot"
                _save_bliss_scan(_flyscan_entry(nxroot), bliss_root, scan_name)

        self.outputs.bliss_scan_uri = f"{output_filename}::/{scan_name}"


_MCA_DATASET = re.compile(
    r"^(?P<board>xmap\d+)(?P<field>channel|livetime|realtime|icr|ocr)(?P<channel>\d+)$"
)

_MCA_FIELDS = {
    "channel": "data",
    "livetime": "trigger_live_time",
    "realtime": "elapsed_time",
    "icr": "trigger_count_rate",
    "ocr": "event_count_rate",
}

_POSITIONER_SUFFIX = "_dataset"


def _flyscan_entry(nxroot: h5py.File) -> h5py.Group:
    for entry in nxroot.values():
        if entry.attrs.get("NX_class") in ("NXentry", b"NXentry"):
            return entry
    raise ValueError(f"No NXentry in {nxroot.filename}")


def _save_bliss_scan(entry: h5py.Group, bliss_root: h5py.File, scan_name: str) -> None:
    scan = bliss_root.create_group(scan_name)
    scan.attrs["NX_class"] = "NXentry"
    scan["title"] = f"{os.path.basename(entry.file.filename)}::{entry.name}"
    instrument = scan.create_group("instrument")
    instrument.attrs["NX_class"] = "NXinstrument"
    measurement = scan.create_group("measurement")
    measurement.attrs["NX_class"] = "NXcollection"
    positioners_start = instrument.create_group("positioners_start")
    positioners_start.attrs["NX_class"] = "NXcollection"

    energy = _beam_energy(entry)
    if energy is not None:
        positioners_start["energy"] = energy[()]
        positioners_start["energy"].attrs["units"] = energy.attrs.get("units", "keV")

    for name, source in entry["scan_data"].items():
        match = _MCA_DATASET.match(name)
        if match:
            group_name = f"{match['board']}_det{match['channel']}"
            field = _MCA_FIELDS[match["field"]]
            detector = _require_nxgroup(instrument, group_name, "NXdetector")
            dset = _flatten(detector, field, source)
            if field == "data":
                measurement[group_name] = h5py.SoftLink(dset.name)
            else:
                measurement[f"{group_name}_{field}"] = h5py.SoftLink(dset.name)
        elif name.endswith(_POSITIONER_SUFFIX):
            group_name = name[: -len(_POSITIONER_SUFFIX)]
            positioner = _require_nxgroup(instrument, group_name, "NXpositioner")
            dset = _flatten(positioner, "value", source)
            measurement[group_name] = h5py.SoftLink(dset.name)
            positioners_start[group_name] = source[(0,) * source.ndim]
        else:
            detector = _require_nxgroup(instrument, name, "NXdetector")
            dset = _flatten(detector, "data", source)
            measurement[name] = h5py.SoftLink(dset.name)


def _beam_energy(entry: h5py.Group) -> Optional[h5py.Dataset]:
    for instrument in entry.values():
        if not isinstance(instrument, h5py.Group):
            continue
        for group in instrument.values():
            if (
                isinstance(group, h5py.Group)
                and group.attrs.get("NX_class")
                in ("NXmonochromator", b"NXmonochromator")
                and "energy" in group
            ):
                return group["energy"]
    return None


def _require_nxgroup(parent: h5py.Group, name: str, nx_class: str) -> h5py.Group:
    group = parent.require_group(name)
    group.attrs["NX_class"] = nx_class
    return group


def _flatten(parent: h5py.Group, name: str, source: h5py.Dataset) -> h5py.Dataset:
    """Virtual dataset that merges the first two dimensions of `source`."""
    nrows, ncols = source.shape[:2]
    layout = h5py.VirtualLayout(
        shape=(nrows * ncols,) + source.shape[2:], dtype=source.dtype
    )
    vsource = h5py.VirtualSource(source)
    for row in range(nrows):
        layout[row * ncols : (row + 1) * ncols] = vsource[row]
    dset = parent.create_virtual_dataset(name, layout)
    units = source.attrs.get("units")
    if units:
        dset.attrs["units"] = units
    return dset
