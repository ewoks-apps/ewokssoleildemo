"""Scenario A.1 on the test bench: FlyScan scan, then XRF processing with ewoksjob.

UNTESTED: requires the FlyScan Tango devices.
Set EWOKS_CONFIG_URI to the configuration of the worker, for example scripts/config_redis.py.
"""

import argparse
import pathlib
import time

import tango
from xrfmap_job import read_parameters
from xrfmap_job import submit_xrfmap


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("flyscan_config", help="FlyScan configuration file (.cfg)")
    parser.add_argument("parameters", help="JSON file with the processing parameters")
    parser.add_argument("processed_dir", help="Directory for the results")
    parser.add_argument(
        "--server", default="flyscan/core/server.1", help="FlyScan server device"
    )
    args = parser.parse_args()

    parameters = read_parameters(args.parameters)
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

    future = submit_xrfmap(filename, args.processed_dir, parameters)
    print("Job", future.uuid)


if __name__ == "__main__":
    main()
