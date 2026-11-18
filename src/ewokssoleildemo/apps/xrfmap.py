"""Process a FlyScan XRF map."""

import argparse
import os
import pathlib
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

try:
    from ewoks import execute_graph
except ImportError:
    execute_graph = None

try:
    from ewoksjob.client import submit
except ImportError:
    submit = None

WORKFLOW = "ewokssoleildemo.workflows.xrfmap_flyscan"

WORKFLOW_SELECT_AREA = "ewokssoleildemo.workflows.xrfmap_flyscan_select_area"


class XrfmapParameters(BaseModel):
    """Processing parameters of a FlyScan XRF map."""

    pymca_config: str = Field(description="PyMca configuration file.")
    detector_names: list[str] = Field(
        description="XRF detectors to sum. The detector of the NeXus dataset "
        "`xmap1channel00` is `xmap1_det00`.",
        examples=[["xmap1_det00", "xmap1_det01"]],
    )
    counter_name: str = Field(description="Normalization counter.", examples=["i0"])
    reference_time: float = Field(
        description="Live time in seconds after the dead time correction.",
        examples=[0.1],
    )
    positioners: list[str] = Field(
        description="Axes of the map.", examples=[["samx", "samz"]]
    )
    signal: Optional[str] = Field(
        default=None,
        description="Element map to select the next scan area from.",
        examples=["Ta_L"],
    )


def main() -> None:
    """Command line interface: `python -m ewokssoleildemo.apps.xrfmap --help`."""
    parser = argparse.ArgumentParser(
        description="Process a FlyScan XRF map. Use --submit to process on an ewoksjob "
        "worker: set EWOKS_CONFIG_URI to the configuration of the worker."
    )
    parser.add_argument("filename", help="FlyScan NeXus file")
    parser.add_argument("parameters", help="JSON file with the processing parameters")
    parser.add_argument("processed_dir", help="Directory for the results")
    parser.add_argument(
        "--select-area", action="store_true", help="Select the next scan area"
    )
    parser.add_argument(
        "--submit", action="store_true", help="Submit to an ewoksjob worker"
    )
    parser.add_argument(
        "--wait", action="store_true", help="Wait for the result of the job"
    )
    args = parser.parse_args()

    workflow = WORKFLOW_SELECT_AREA if args.select_area else WORKFLOW
    parameters = XrfmapParameters.model_validate_json(
        pathlib.Path(args.parameters).read_text()
    )
    arguments = xrfmap_arguments(
        args.filename, args.processed_dir, parameters, select_area=args.select_area
    )
    if not args.submit:
        if execute_graph is None:
            parser.error("Install ewoks: pip install ewokssoleildemo[job]")
        print(execute_graph(workflow, **arguments))
        return

    if submit is None:
        parser.error("Install ewoksjob: pip install ewokssoleildemo[job]")
    future = submit(args=(workflow,), kwargs=arguments)
    print("Job", future.uuid)
    if args.wait:
        print(future.result())


def xrfmap_arguments(
    filename: str,
    processed_dir: str,
    parameters: XrfmapParameters,
    select_area: bool = False,
) -> dict:
    """Keyword arguments of `ewoks.execute_graph` to process the FlyScan NeXus file `filename`
    with `WORKFLOW`, or with `WORKFLOW_SELECT_AREA` when `select_area` is true.
    The results go to `processed_dir`."""
    filename = os.path.abspath(filename)
    processed_dir = os.path.abspath(processed_dir)
    basename = os.path.splitext(os.path.basename(filename))[0]
    output_root_uri = os.path.join(processed_dir, f"{basename}_xrf.h5") + "::/1.1"
    reference_time = parameters.reference_time
    inputs = [
        {"id": "convert", "name": "filename", "value": filename},
        {
            "id": "convert",
            "name": "output_filename",
            "value": os.path.join(processed_dir, f"{basename}_bliss.h5"),
        },
        {"id": "sum", "name": "detector_names", "value": parameters.detector_names},
        {"id": "sum", "name": "output_root_uri", "value": output_root_uri},
        {
            # Live time correction to `reference_time` seconds for every point:
            # reference_time / energy live time = reference_time * ICR / (real time * OCR)
            "id": "sum",
            "name": "detector_normalization_template",
            "value": f"{reference_time}*<instrument/{{}}/trigger_count_rate>"
            "/(<instrument/{}/elapsed_time>*<instrument/{}/event_count_rate>)",
        },
        {
            "id": "fit",
            "name": "config",
            "value": os.path.abspath(parameters.pymca_config),
        },
        {"id": "fit", "name": "energy_name", "value": "energy"},
        {"id": "norm", "name": "counter_name", "value": parameters.counter_name},
        {"id": "regrid", "name": "positioners", "value": parameters.positioners},
    ]
    if select_area:
        inputs.append({"id": "select", "name": "signal", "value": parameters.signal})
    return {
        "inputs": inputs,
        "outputs": [{"all": False}],
        # WORKFLOW and WORKFLOW_SELECT_AREA are package resources
        "load_options": {"representation": "json_module"},
        # Workflow with all inputs, to reproduce the results
        "convert_destination": os.path.join(processed_dir, f"{basename}_workflow.json"),
    }


if __name__ == "__main__":
    main()
