"""Start a FlyScan scan on the test bench, then submit the XRF map workflow to an ewoksjob worker.

UNTESTED: requires the FlyScan Tango devices.
Set EWOKS_CONFIG_URI to the ewoksjob configuration of the worker, for example scripts/config_redis.py.
"""

import argparse
import os
import pathlib
import time

import tango
from ewoksjob.client import submit


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("flyscan_config", help="FlyScan configuration file (.cfg)")
    parser.add_argument("pymca_config", help="PyMca configuration file")
    parser.add_argument("processed_dir", help="Directory for the results")
    parser.add_argument(
        "--server", default="flyscan/core/server.1", help="FlyScan server device"
    )
    args = parser.parse_args()

    server = tango.DeviceProxy(args.server)
    server.set_timeout_millis(30000)
    merger = tango.DeviceProxy(server.mergerDevice)

    server.configuration = pathlib.Path(args.flyscan_config).read_text().splitlines()
    server.Start()
    while server.state() in (tango.DevState.RUNNING, tango.DevState.STANDBY):
        print(f"{server.scanProgress:.0f} %")
        time.sleep(1)
    filename = list(merger.outputNexusFiles)[-1]
    print("Scan saved in", filename)

    # The worker must see the files at the same paths
    basename = os.path.splitext(os.path.basename(filename))[0]
    processed_dir = os.path.abspath(args.processed_dir)
    # Parameters for the XIA channels 02 and 03, the counter miVtf1,
    # the PI actuators Tx and Tz, and 25 ms of real time per point
    inputs = [
        {"id": "convert", "name": "filename", "value": filename},
        {
            "id": "convert",
            "name": "output_filename",
            "value": f"{processed_dir}/{basename}_bliss.h5",
        },
        {
            "id": "sum",
            "name": "detector_names",
            "value": ["xmap1_det02", "xmap1_det03"],
        },
        {
            "id": "sum",
            "name": "detector_normalization_template",
            "value": "0.025*<instrument/{}/trigger_count_rate>"
            "/(<instrument/{}/elapsed_time>*<instrument/{}/event_count_rate>)",
        },
        {
            "id": "sum",
            "name": "output_root_uri",
            "value": f"{processed_dir}/{basename}_xrf.h5::/1.1",
        },
        {"id": "fit", "name": "config", "value": os.path.abspath(args.pymca_config)},
        {"id": "fit", "name": "energy_name", "value": "energy"},
        {"id": "norm", "name": "counter_name", "value": "miVtf1"},
        {"id": "regrid", "name": "positioners", "value": ["Tx", "Tz"]},
    ]
    future = submit(
        args=("xrfmap_flyscan",),
        kwargs={
            "inputs": inputs,
            "load_options": {"root_module": "ewokssoleildemo.workflows"},
        },
    )
    print("Job", future.uuid)


if __name__ == "__main__":
    main()
