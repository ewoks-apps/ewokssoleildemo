"""Submit the XRF map workflows to an ewoksjob worker.

The client needs ewoksjob. It does not need ewokssoleildemo: the worker loads the workflows.
The workflow inputs are the same as in ewokssoleildemo.apps.xrfmap.xrfmap_arguments.
"""

import json
import os

from ewoksjob.client import Future
from ewoksjob.client import submit

WORKFLOW = "ewokssoleildemo.workflows.xrfmap_flyscan"

WORKFLOW_SELECT_AREA = "ewokssoleildemo.workflows.xrfmap_flyscan_select_area"


def read_parameters(filename: str) -> dict:
    """Processing parameters from a JSON file. See ewokssoleildemo.apps.xrfmap.XrfmapParameters."""
    with open(filename) as f:
        return json.load(f)


def submit_xrfmap(
    filename: str, processed_dir: str, parameters: dict, select_area: bool = False
) -> Future:
    """Submit the processing of the FlyScan NeXus file `filename` with `WORKFLOW`,
    or with `WORKFLOW_SELECT_AREA` when `select_area` is true.
    The results go to `processed_dir`."""
    filename = os.path.abspath(filename)
    processed_dir = os.path.abspath(processed_dir)
    basename = os.path.splitext(os.path.basename(filename))[0]
    output_root_uri = os.path.join(processed_dir, f"{basename}_xrf.h5") + "::/1.1"
    reference_time = parameters["reference_time"]
    inputs = [
        {"id": "convert", "name": "filename", "value": filename},
        {
            "id": "convert",
            "name": "output_filename",
            "value": os.path.join(processed_dir, f"{basename}_bliss.h5"),
        },
        {"id": "sum", "name": "detector_names", "value": parameters["detector_names"]},
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
            "value": os.path.abspath(parameters["pymca_config"]),
        },
        {"id": "fit", "name": "energy_name", "value": "energy"},
        {"id": "norm", "name": "counter_name", "value": parameters["counter_name"]},
        {"id": "regrid", "name": "positioners", "value": parameters["positioners"]},
    ]
    if select_area:
        inputs.append({"id": "select", "name": "signal", "value": parameters["signal"]})
    kwargs = {
        "inputs": inputs,
        "outputs": [{"all": False}],
        # The worker loads the workflows from ewokssoleildemo
        "load_options": {"representation": "json_module"},
        # Workflow with all inputs, to reproduce the results
        "convert_destination": os.path.join(processed_dir, f"{basename}_workflow.json"),
    }
    workflow = WORKFLOW_SELECT_AREA if select_area else WORKFLOW
    return submit(args=(workflow,), kwargs=kwargs)
